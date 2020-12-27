
import os
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from logging import getLogger
from multiprocessing import Manager
from threading import Thread
from time import time

from src.board.game import Game, cnn_input, Winner, ai_move
from src.ai_non_nostra.config import Config
from src.ai_non_nostra.player_chess import ChessPlayer
from multiprocessing import Manager
from src.ai_non_nostra.model_helper import load_best_model_weight, save_as_best_model, reload_best_model_weight_if_changed
from src.ai_non_nostra.model_chess_tf import ChessModel
from src.ai_non_nostra.data_helper import write_game_data_to_file, get_game_data_filenames

class SelfPlayWorker:
    """
    Worker which trains a chess model using self play data. ALl it does is do self play and then write the
    game data to file, to be trained on by the optimize worker.

    Attributes:
        :ivar Config config: config to use to configure this worker
        :ivar ChessModel current_model: model to use for self play
        :ivar Manager m: the manager to use to coordinate between other workers
        :ivar list(Connection) cur_pipes: pipes to send observations to and get back mode predictions.
        :ivar list((str,list(float))): list of all the moves. Each tuple has the observation in FEN format and
            then the list of prior probabilities for each action, given by the visit count of each of the states
            reached by the action (actions indexed according to how they are ordered in the uci move list).
    """
    def __init__(self, config: Config):
        self.config = config
        self.current_model = self.load_model()
        self.m = Manager()
        self.cur_pipes = self.m.list([self.current_model.get_pipes(self.config.play.search_threads) for _ in range(self.config.play.max_processes)])
        self.buffer = []

    def start(self):
        """
        Do self play and write the data to the appropriate file.
        """
        self.buffer = []

        futures = deque()
        with ProcessPoolExecutor(max_workers=self.config.play.max_processes) as executor:
            for game_idx in range(self.config.play.max_processes):
                futures.append(executor.submit(self_play_buffer, self.config, cur=self.cur_pipes))
            game_idx = 0
            while True:
                game_idx += 1
                data = futures.popleft().result()
                '''
                print(f"game {game_idx:3} time={time() - start_time:5.1f}s "
                    f"halfmoves={env.num_halfmoves:3} {env.winner:12} "
                    f"{'by resign ' if env.resigned else '          '}")
                '''

                self.buffer += data
                self.flush_buffer()
                '''
                if (game_idx % self.config.play_data.nb_game_in_file) == 0:
                    self.flush_buffer()
                    reload_best_model_weight_if_changed(self.current_model)
                '''
                futures.append(executor.submit(self_play_buffer, self.config, cur=self.cur_pipes)) # Keep it going

        if len(data) > 0:
            self.flush_buffer()

    def load_model(self):
        """
        Load the current best model
        :return ChessModel: current best model
        """
        model = ChessModel(self.config)
        if self.config.opts.new or not load_best_model_weight(model):
            model.build()
            save_as_best_model(model)
        return model

    def flush_buffer(self):
        """
        Flush the play data buffer and write the data to the appropriate location
        """
        print('salvo su file')
        rc = self.config.resource
        game_id = datetime.now().strftime("%Y%m%d-%H%M%S.%f")
        path = os.path.join(rc.play_data_dir, rc.play_data_filename_tmpl % game_id)
        thread = Thread(target=write_game_data_to_file, args=(path, self.buffer))
        thread.start()
        self.buffer = []
        print('finito salvataggio')

    def remove_play_data(self):
        """
        Delete the play data from disk
        """
        files = get_game_data_filenames(self.config.resource)
        if len(files) < self.config.play_data.max_file_num:
            return
        for i in range(len(files) - self.config.play_data.max_file_num):
            os.remove(files[i])


def self_play_buffer(config, cur) -> (list):
    """
    Play one game and add the play data to the buffer
    :param Config config: config for how to play
    :param list(Connection) cur: list of pipes to use to get a pipe to send observations to for getting
        predictions. One will be removed from this list during the game, then added back
    :return (ChessEnv,list((str,list(float)): a tuple containing the final ChessEnv state and then a list
        of data to be appended to the SelfPlayWorker.buffer
    """
    pipes = cur.pop() # borrow
    env = Game()

    white = ChessPlayer(config, pipes=pipes)
    black = ChessPlayer(config, pipes=pipes)

    while not env.done():
        if env.white_to_move():
            action = white.action(env)
        else:
            action = black.action(env)

        move = ai_move(action)
        print(move)
        env.check_move(move[0], move[1], promotion=move[2])

        if env.num_move >= config.play.max_game_length:
            env.adjudicate()

    if env.winner == Winner.white:
        black_win = -1
    elif env.winner == Winner.black:
        black_win = 1
    else:
        black_win = 0

    black.finish_game(black_win)
    white.finish_game(-black_win)

    data = []
    for i in range(len(white.moves)):
        data.append(white.moves[i])
        if i < len(black.moves):
            data.append(black.moves[i])

    env.print_board()
    cur.append(pipes)
    return data

def main():
    SelfPlayWorker(Config()).start()
    