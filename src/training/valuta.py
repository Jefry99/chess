import os
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
from multiprocessing import Manager
from time import sleep

from src.board.game import Game, cnn_input, Winner, ai_move
from src.ai_non_nostra.model_chess import ChessModel
from src.ai_non_nostra.player_chess import ChessPlayer
from src.ai_non_nostra.config import Config
from src.ai_non_nostra.data_helper import get_next_generation_model_dirs
from src.ai_non_nostra.model_helper import save_as_best_model, load_best_model_weight

class EvaluateWorker:
    """
    Worker which evaluates trained models and keeps track of the best one

    Attributes:
        :ivar Config config: config to use for evaluation
        :ivar PlayConfig config: PlayConfig to use to determine how to play, taken from config.eval.play_config
        :ivar ChessModel current_model: currently chosen best model
        :ivar Manager m: multiprocessing manager
        :ivar list(Connection) cur_pipes: pipes on which the current best ChessModel is listening which will be used to
            make predictions while playing a game.
    """
    def __init__(self, config: Config):
        """
        :param config: Config to use to control how evaluation should work
        """
        self.config = config
        self.play_config = config.eval.play_config
        self.current_model = self.load_current_model()
        self.m = Manager()
        self.cur_pipes = self.m.list([self.current_model.get_pipes(self.play_config.search_threads) for _ in range(self.play_config.max_processes)])

    def start(self):
        """
        Start evaluation, endlessly loading the latest models from the directory which stores them and
        checking if they do better than the current model, saving the result in self.current_model
        """
        #while True:
        ng_model, model_dir = self.load_next_generation_model()
        print("start evaluate model " + str(model_dir))
        ng_is_great = self.evaluate_model(ng_model)
        print("did evaluate model")
        if ng_is_great:
            print("New Model become best model: " + str(model_dir))
            save_as_best_model(ng_model)
            self.current_model = ng_model
        self.move_model(model_dir)
        print('finito')

    def evaluate_model(self, ng_model):
        """
        Given a model, evaluates it by playing a bunch of games against the current model.

        :param ChessModel ng_model: model to evaluate
        :return: true iff this model is better than the current_model
        """
        ng_pipes = self.m.list([ng_model.get_pipes(self.play_config.search_threads) for _ in range(self.play_config.max_processes)])
        futures = []
        with ProcessPoolExecutor(max_workers=self.play_config.max_processes) as executor:
            for game_idx in range(self.config.eval.game_num):
                fut = executor.submit(play_game, self.config, cur=self.cur_pipes, ng=ng_pipes, current_white=(game_idx % 2 == 0))
                futures.append(fut)
            print("Completato le partite")
            results = []
            for fut in as_completed(futures):
                # ng_score := if ng_model win -> 1, lose -> 0, draw -> 0.5
                ng_score, current_white = fut.result()
                results.append(ng_score)
                print(results)
                win_rate = sum(results) / len(results)
                game_idx = len(results)
                colors = ("current_model", "ng_model")
                if not current_white:
                    colors = reversed(colors)
                if len(results)-sum(results) >= self.config.eval.game_num * (1-self.config.eval.replace_rate):
                    print("lose count reach " + str(results.count(0)) + " so give up challenge")
                    return False
                if sum(results) >= self.config.eval.game_num * self.config.eval.replace_rate:
                    print("win count reach " + str(results.count(1)) + " so change best model")
                    return True

        win_rate = sum(results) / len(results)
        print("winning rate " + str(win_rate * 100))
        return win_rate >= self.config.eval.replace_rate

    def move_model(self, model_dir):
        """
        Moves the newest model to the specified directory

        :param file model_dir: directory where model should be moved
        """
        rc = self.config.resource
        new_dir = os.path.join(rc.next_generation_model_dir, "copies", model_dir)
        os.rename(model_dir, new_dir)

    def load_current_model(self):
        """
        Loads the best model from the standard directory.
        :return ChessModel: the model
        """
        model = ChessModel(self.config)
        load_best_model_weight(model)
        return model

    def load_next_generation_model(self):
        """
        Loads the next generation model from the standard directory
        :return (ChessModel, file): the model and the directory that it was in
        """
        rc = self.config.resource
        while True:
            dirs = get_next_generation_model_dirs(self.config.resource)
            if dirs:
                break
            print("There is no next generation model to evaluate")
            sleep(60)
        model_dir = dirs[-1] if self.config.eval.evaluate_latest_first else dirs[0]
        config_path = os.path.join(model_dir, rc.next_generation_model_config_filename)
        weight_path = os.path.join(model_dir, rc.next_generation_model_weight_filename)
        model = ChessModel(self.config)
        model.load(config_path, weight_path)
        return model, model_dir


def play_game(config, cur, ng, current_white: bool) -> (float, bool):
    """
    Plays a game against models cur and ng and reports the results.

    :param Config config: config for how to play the game
    :param ChessModel cur: should be the current model
    :param ChessModel ng: should be the next generation model
    :param bool current_white: whether cur should play white or black
    :return (float, ChessEnv, bool): the score for the ng model
        (0 for loss, .5 for draw, 1 for win), the env after the game is finished, and a bool
        which is true iff cur played as white in that game.
    """
    cur_pipes = cur.pop()
    ng_pipes = ng.pop()
    env = Game()
    
    current_player = ChessPlayer(config, pipes=cur_pipes, play_config=config.eval.play_config)
    ng_player = ChessPlayer(config, pipes=ng_pipes, play_config=config.eval.play_config)
    if current_white:
        white, black = current_player, ng_player
    else:
        white, black = ng_player, current_player
    while not env.done():
        if env.white_to_move:
            action = white.action(env)
        else:
            action = black.action(env)
        move = ai_move(action)
        env.check_move(move[0], move[1], promotion=move[2])
        if env.num_move >= config.eval.max_game_length:
            env.adjudicate()

    if env.winner == Winner.draw:
        ng_score = 0.5
    elif env.winner == current_white:
        ng_score = 0
    else:
        ng_score = 1
    cur.append(cur_pipes)
    ng.append(ng_pipes)
    return ng_score, current_white

def main():
    EvaluateWorker(Config()).start()