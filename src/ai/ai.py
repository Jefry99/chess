# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
# pylint: disable=missing-docstring
# pylint: disable=g-explicit-length-test

from __future__ import absolute_import
from __future__ import division
#from __future__ import google_type_annotations
from __future__ import print_function

import collections
import math
import typing
from typing import Dict, List, Optional

import numpy
import tensorflow as tf

MAXIMUM_FLOAT_VALUE = float('inf')

KnownBounds = collections.namedtuple('KnownBounds', ['min', 'max'])

class Action(object):
      def __init__(self, index: int):
        self.index = index
    
      def __hash__(self):
        return self.index
    
      def __eq__(self, other):
        return self.index == other.index
    
      def __gt__(self, other):
        return self.index > other.index

class NetworkOutput(typing.NamedTuple):
    value: float
    reward: float
    policy_logits: Dict[Action, float]
    hidden_state: List[float]

class Network(object):
    def initial_inference(self, image) -> NetworkOutput: #Representation + prediction function
        return NetworkOutput(0, 0, {}, [])
    
    def recurrent_inference(self, hidden_state, action) -> NetworkOutput: #Dynamics + prediction function
        return NetworkOutput(0, 0, {}, [])
    
    def get_weights(self): #Ritorna i pesi della nn
        return[]
    
    def training_steps(self) -> int: #Ritorna quanti step la nn ha eseguito
        return 0

class Player(object):
    pass

class MinMaxStats(object):

    def __init__(self, known_bounds: Optional[KnownBounds]):
        self.maximum = 1
        self.minimum = -1

    def update(self, value: float):
        self.maximum = max(self.maximum, value)
        self.minimum = min(self.minimum, value)

    def normalize(self, value: float) -> float:
        if self.maximum > self.minimum:
            return (value - self.minimum) / (self.maximum - self.minimum)
        return value

class AiConfig(object):
      def __init__(self, action_space_size: int, max_moves: int, discount: float, dirichlet_alpha: float, num_simulations: int,
                   batch_size: int, td_steps: int, num_actors: int, lr_init: float, lr_decay_steps: float, visit_softmax_temperature_fn, known_bounds: Optional[KnownBounds] = None):
        ### Self-Play
        self.action_space_size = action_space_size
        self.num_actors = num_actors
    
        self.visit_softmax_temperature_fn = visit_softmax_temperature_fn
        self.max_moves = max_moves
        self.num_simulations = num_simulations
        self.discount = discount
    
        # Root prior exploration noise.
        self.root_dirichlet_alpha = dirichlet_alpha
        self.root_exploration_fraction = 0.25
    
        # UCB formula
        self.pb_c_base = 19652
        self.pb_c_init = 1.25
    
        # If we already have some information about which values occur in the
        # environment, we can use them to initialize the rescaling.
        # This is not strictly necessary, but establishes identical behaviour to
        # AlphaZero in board games.
        self.known_bounds = known_bounds
    
        ### Training
        self.training_steps = int(1000e3)
        self.checkpoint_interval = int(1e3)
        self.window_size = int(1e6)
        self.batch_size = batch_size
        self.num_unroll_steps = 5
        self.td_steps = td_steps
    
        self.weight_decay = 1e-4
        self.momentum = 0.9
    
        # Exponential learning rate schedule
        self.lr_init = lr_init
        self.lr_decay_rate = 0.1
        self.lr_decay_steps = lr_decay_steps

      def new_game(self):
        return Game(self.action_space_size, self.discount)

class ActionHistory(object):
      """Simple history container used inside the search.
    
      Only used to keep track of the actions executed.
      """
      def __init__(self, history: List[Action], action_space_size: int):
        self.history = list(history)
        self.action_space_size = action_space_size
    
      def clone(self):
        return ActionHistory(self.history, self.action_space_size)
    
      def add_action(self, action: Action):
        self.history.append(action)
    
      def last_action(self) -> Action:
        return self.history[-1]
    
      def action_space(self) -> List[Action]:
        return [Action(i) for i in range(self.action_space_size)]
    
      def to_play(self) -> Player:
        return Player()

class Environment(object):
      """The environment MuZero is interacting with."""
    
      def step(self, action):
        pass

def make_board_game_config(action_space_size: int, max_moves: int, dirichlet_alpha: float, lr_init: float) -> AiConfig:
      def visit_softmax_temperature(num_moves, training_steps):
        if num_moves < 30:
          return 1.0
        else:
          return 0.0
    
      return AiConfig(
          action_space_size=action_space_size,
          max_moves=max_moves,
          discount=1.0,
          dirichlet_alpha=dirichlet_alpha,
          num_simulations=800,
          batch_size=2048,
          td_steps=max_moves,
          num_actors=3000,
          lr_init=lr_init,
          lr_decay_steps=400e3,
          visit_softmax_temperature_fn=visit_softmax_temperature,
          known_bounds=KnownBounds(-1, 1))

def make_chess_config() -> AiConfig: #Crea una configurazione per gli scacchi
      return make_board_game_config(
          action_space_size=4672, max_moves=512, dirichlet_alpha=0.3, lr_init=0.1)

class Game(object):
    #Una singola interazione con l'ambiente
    
    def __init__(self, action_space_size: int, discount: float):
        self.environment = Environment() #L'ambiente specifico del gioco, nel nostro scacco gli scacchi
        self.history = [] #Lista di azioni prese durante il gioco
        self.rewards = [] #Lista di reward ricevuti ad ogni turno di gioco
        self.child_visits = [] #Lista di distribuzione di probabilità delle azioni dalla radice ad ogni turno di gioco
        self.root_values = [] #Una lista dei valori del nodo radice ad ogni turno di gioco
        self.action_space_size = action_space_size
        self.discount = discount
        
        #Usa idea dal temporal difference learning per calcolare il target value di ogni stato in posizione da state_index a state_index + num_unroll_steps
        """
        TD-learning is a common technique used in reinforcement learning — the idea is that we can update the value of a 
        state using the estimated discounted value of a position td_steps into the near future plus the discounted rewards 
        up until that point, rather than just using the total discounted rewards accrued by the end of the episode.
        """
        def make_target(self, state_index: int, num_unroll_steps: int, td_steps: int, to_play: Player):
            #Il value target è il discounted value del nodo radice dell'albero di ricerca N step nel futuro, più la discounted sum di tutti i reward fino a lì
            targets = []
            for current_index in range(state_index, state_index + num_unroll_steps + 1):
                bootstrap_index = current_index + td_steps #L'indice della posizione td_steps nel futuro che utilizziamo per stimare il valore di reward successivi
                if bootstrap_index < len(self.root_values):
                    value = self.root_values[bootstrap_index] * self.discount**td_steps
                else:
                    #il bootstrap_index è alla fine dell'episodio
                    value = 0
                #Negli scacchi, td_steps deve essere messo a max_moves così che bootstrap_index finisca sempre dopo la fine dell'episodio, dato che il reward per gli scacchi c'è solo alla fine
                for i, reward in enumerate(self.rewards[current_index:bootstrap_index]):
                    value += reward * self.discount**i  # pytype: disable=unsupported-operands

                if current_index < len(self.root_values):
                    targets.append((value, self.rewards[current_index], self.child_visits[current_index]))
                else:
                    #Stati oltre la fine del gioco
                    targets.append((0, 0, []))
                return targets

        def terminal(self) -> bool:
                # Game specific termination rules.
                pass
            
        def legal_actions(self) -> List[Action]:
                # Game specific calculation of legal actions.
                return []
            
        def apply(self, action: Action):
                reward = self.environment.step(action)
                self.rewards.append(reward)
                self.history.append(action)
            
        def store_search_statistics(self, root: Node):
                sum_visits = sum(child.visit_count for child in root.children.values())
                action_space = (Action(index) for index in range(self.action_space_size))
                self.child_visits.append([
                    root.children[a].visit_count / sum_visits if a in root.children else 0
                    for a in action_space
                ])
                self.root_values.append(root.value())
            
        def make_image(self, state_index: int):
                # Game specific feature planes.
                return []

        def to_play(self) -> Player:
           return Player()
    
        def action_history(self) -> ActionHistory:
           return ActionHistory(self.history, self.action_space_size)

class SharedStorage(object): #Gestisce il salvataggio e il caricamento dei nn
    
    def __init__(self):
        self.networks = {}
    
    def latest_network(self) -> Network: 
        if self.networks: #Se esiste già almeno una nn, ritorna l'ultima
            return self.networks[max(self.networks.keys())]
        else: #Altrimenti creala
            return make_uniform_network()
    
    def save_network(self, step: int, network: Network): #Salva il network passatogli di classe Network in networksc on key = step
        self.networks[step] = network

class ReplayBuffer(object): #Salva informazioni sulle partite precedenti
    def __init__(self, config: AiConfig):
        self.window_size = config.window_size #Numero di partite salvate nel buffer
        self.batch_size = config.batch_size
        self.buffer = []

    def save_game(self, game): #Aggiungo la partita passata nel buffer di memoria
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0) #Elimino la partita aggiunta più vecchia se supero la window_size
        self.buffer.append(game)
    
    def sample_batch(self, num_unroll_steps: int, td_steps: int):
        games = [self.sample_game() for _ in range(self.batch_size)]
        game_pos = [(g, self.sample_position(g)) for g in games]
        #Una singola batch è una lista di tuple, dove ogni tupla ha 3 elementi
        # (1) g.make_image(i) - L'osservazione della posizione scelta
        # (2) g.history[i:i + num_unroll_steps] - Una lista delle prossime num_unroll_steps azioni prese dopo la posizione attuale (se esistono)
        # (3) g.make_target(i, num_unroll_steps, td_steps, g.to_play()) - Una lista di target che saranno usati per allenare la nn. C'è una lista di tuple target_value, target_reward e target_policy
        return [(g.make_image(i), g.history[i:i + num_unroll_steps], g.make_target(i, num_unroll_steps, td_steps, g.to_play())) for (g,i) in game_pos]

    def sample_game(self) -> Game:
        # Sample game from buffer either uniformly or according to some priority.
        return self.buffer[0]

    def sample_position(self, game) -> int:
        # Sample position from game either uniformly or according to some priority.
        return -1
  
class Node(object):
    
    def __init__(self, prior:float):
        self.visit_count = 0 #Numero di volte che è stato visitato
        self.to_play = -1 #Quale giocatore deve muovere
        self.prior = prior #La precedente probabilità di scegliere un'azione che arriva a questo nodo
        self.value_sum = 0 #Il valore somma di tutti i nodi precedenti 
        self.children = {} #I nodi figli
        self.hidden_state = None
        self.reward = 0 #Il reward previsto ricevuto entrando in questo nodo 
    
    def expanded(self) -> bool: #Ritorna se è un nodo foglia o meno
        return len(self.children) > 0 
    
    def value(self) -> float:
        if self.visit_count == 0:
            return 0
        return (self.value_sum / self.visit_count) #Ritorna un valore che diminuisce ad oogni visita di questo nodo per migliorare l'esplorazione    

def run_selfplay(config: AiConfig, storage: SharedStorage, replay_buffer: ReplayBuffer):
    while True:
        network = storage.latest_network() #Prende l'ultima versione del nn
        game = play_game(config, network) #Gioca una partita
        replay_buffer.save_game(game) #Salva la partita giocata

def play_game(config: AiConfig, network: Network) -> Game:
    #Ogni partita inizia alla posizione iniziale della scacchiera, e ripetutamente esegue una ricerca sull'albero di Monte Carlo finché non si raggiunge la fine della partita
    game = config.new_game()
    
    while not game.terminal() and len(game.history) < config.max_moves:
        #Alla radice dell'albero di ricerca usiamo la representation function per ottenere un hidden state della posizione attuale
        root = Node(0) #Albero di Monte Carlo inizializzato alla radice
        current_observation = game.make_image(-1)
        expand_node(root, game.to_play(), game.legal_actions(), network.initial_inference(current_observation))
        add_exploration_noise(config, root)
        
        #Successivamente eseguiamo una ricerca sull'albero di Monte Carlo usando solo sequenze di azioni e il modello della nn
        run_mcts(config, root, game.action_history(), network)
        action = select_action(config, len(game.history), root, network)
        game.apply(action)
        game.store_search_statistics(root)
    return game

def expand_node(node: Node, to_play: Player, actions: List[Action], network_output: NetworkOutput): #Espandiamo un nodo usando il valore, il reward e la predizione della policy ottenuta dalla nn
    node.to_play = to_play 
    node.hidden_state = network_output.hidden_state #Ottengo l'hidden state del nodo
    node.reward = network_output.reward #Ottengo il reward del nodo
    policy = {a: math.exp(network_output.policy_logits[a]) for a in actions}
    policy_sum = sum(policy.values())
    for action,p in policy.items():
        node.children[action] = Node(p / policy_sum)

def add_exploration_noise(config: AiConfig, node: Node): #All'inizio di una ricerca, aggiungiamo del rumore per incentivare l'esplorazione
    actions = list(node.children.keys())
    noise = numpy.random.dirichlet([config.root_dirichlet_alpha] * len(actions))
    frac = config.root_exploration_fraction
    for a, n in zip(actions, noise):
        node.children[a].prior = node.children[a].prior * (1-frac) + n * frac

def run_mcts(config: AiConfig, root: Node, action_history: ActionHistory, network:Network): #Algoritmo di ricerca nell'albero di Monte Carlo
    #Per decidere un'azione, si eseguono N simulazioni, sempre iniziando dalla radice e attraversando l'albero usando la formula UCB finché non si raggiunge un nodo foglia
    min_max_stats = MinMaxStats(config.known_bounds) #Minimo e massimo reward mai ottenuto per normalizzare l'output a dei valori sensati
    
    for _ in range(config.num_simulations):
        history = action_history.clone() # history è inizializzata con la lista di azioni prese dall'inizio del gioco
        node = root #Il nodo corrente è l'attuale radice
        search_path = [node] #Essendo la radice, search_path contiene solo il nodo radice inizialmente
        
        while node.expanded():
            action, node = select_child(config, node, min_max_stats)
            history.add_action(action)
            search_path.append(node)
        
        #Dentro la ricerca nell'albero usiamo la dynamics function per ottenere lo hidden state dopo un'azione e lo hidden state precedente
        parent = search_path[-2]
        #Viene chiamata recurrent_inference sul genitore del nodo, per ottenere il reward previsto ed il nuovo hidden state (dal dynamics network) e la policy e value dal nuovo hidden state (dal prediction network)
        network_output = network.recurrent_inference(parent.hidden_state, history.last_action())
        #Espande quindi il nodo creando i figli e assegnando ad ognuno il policy prior. L'AI non sa quali azioni sono legali o meno, quindi crea un nodo per ogni azione possibile
        expand_node(node, history.to_play(), history.action_space(), network_output)
        
        backpropagate(search_path, network_output.value, history.to_play(), config.discount, min_max_stats)
        
def select_child(config: AiConfig, node: Node, min_max_stats: MinMaxStats):
    #Lo ucb_score è il valore stimato dell'azione Q(s,a) con un bonus esplorazione sulla precedente probabilità di selezionare l'azione P(s, a) e il numero di volte l'azione è già stata selezionata N(s, a) 
    action, child = max((ucb_score(config, node, child, min_max_stats), action, child) for action, child in node.children.items())
    return (action, child)
    #Inizialmente il bonus eplorazione è il valore determinante, ma all'aumento delle simulazioni le azioni migliori prevalgono
    
def backpropagate(search_path: List[Node], value: float, to_play: Player, discount: float, min_max_stats:MinMaxStats):
    # Alla fine della simulazione, propaghiamo la valutazione fino alla radice dell'albero
    for node in search_path:
        node.value_sum += value if node.to_play == to_play else -value #Il valore è opposto in base al turno di gioco (se è positivo per un giocatore deve essere negativo per l'altro)
        node.visit_count + 1
        min_max_stats.update(node.value())
        value = node.reward + discount * value

def select_action(config: AiConfig, num_moves: int, node:Node, network: Network):
    #Scelgo l'azione in base al numero di visite di ogni nodo
    visit_counts = [(child.visit_count, action) for action, child in node.children.items()]
    t = config.visit_softmax_temperature_fn(num_moves = num_moves, training_steps = network.training_steps())
    _, action = softmax_sample(visit_counts, t)
    return action

def visit_softmax_temperature(num_moves, training_steps):
    if num_moves < 30:
        #Per le prime 30 mosse, la temperatura è 1, ossia la probabilità di selezione di ogni azione è proporzionale al numero di visite di essa
        return 1.0
    else:
        #Dalla 30° mossa in poi, l'azione con il massimo numero di visite è selezionata
        return 0.0
    
def train_network(config: AiConfig, storage: SharedStorage, replay_buffer: ReplayBuffer):
    network = Network() #Inizializza un oggetto Network che crea tre istanze delle nn inizializzate randomicamente
    learning_rate = config.lr_init * config.lr_decay_rate**(tf.train.get_global_step() / config.lr_decay_steps)
    optimizer = tf.train.MomentumOptimizer(learning_rate, config.momentum) #Creiamo l'ottimizzatore gradient descent che calcolerà la magnitude e la direzione degli aggiornamenti dei pesi ad ogni step
    
    for i in range(config.training_steps):
        if i % config.checkpoint_interval == 0:
            storage.save_network(i, network) #Salva il network ad ogni checkpoint_interval steps
        batch = replay_buffer.sample_batch(config.num_unroll_steps, config.td_steps) #Prende un batch di posizioni dal replay_buffer e le usa per aggiornare il network
        update_weights(optimizer, network, batch, config.weight_decay)
    storage.save_network(config.training_steps, network)

def update_weights(optimizer: tf.optimizers.Optimizer, network: Network, batch, weight_decay: float):
    loss = 0
    for image, actions, targets in batch:
        #Step iniziale dall'effettiva osservazione
        #Ottengo il valore, il reward e la policy della posizione attuale
        value, reward, policy_logits, hidden_state = network.initial_inference(image)
        #Da queste creo la lista di prediction
        predictions = [(1.0, value, reward, policy_logits)]
        
        for action in actions: 
            #Ogni azione viene visitate con recurrent_inference per predire il valore, il reward e la policy dall'attuale hidden_state
            value, reward, policy_logits, hidden_state = network.recurrent_inference(hidden_state, action)
            #Queste sono appese alla lista predictions con peso di 1/num_rollout_steps, così che il peso totale di recurrent_inference è uguale a quella di initial_inference)
            predictions.append([1.0/len(actions), value, reward, policy_logits])
            hidden_state = tf.scale_gradient(hidden_state, 0.5)
        
        for prediction, target in zip(predictions, targets):
            gradient_scale, value, reward, policy_logits = prediction
            target_value, target_reward, target_policy = target
            
            l = (
                scalar_loss(value, target_value) + 
                scalar_loss(reward, target_reward) + 
                tf.nn.softmax_cross_entropy_with_logits(logits = policy_logits, labels = target_policy))
        
            loss += tf.scale_gradient(l, gradient_scale)
        
        for weights in network.get_weights():
            loss += weight_decay * tf.nn.l2_loss(weights)
        
        optimizer.minimize(loss)

def ucb_score(config: AiConfig, parent: Node, child: Node,
                  min_max_stats: MinMaxStats) -> float:
      pb_c = math.log((parent.visit_count + config.pb_c_base + 1) /
                      config.pb_c_base) + config.pb_c_init
      pb_c *= math.sqrt(parent.visit_count) / (child.visit_count + 1)
    
      prior_score = pb_c * child.prior
      value_score = min_max_stats.normalize(child.value())
      return prior_score + value_score

def scalar_loss(prediction, target) -> float:
      # MSE in board games, cross entropy between categorical values in Atari.
      return -1

# Stubs to make the typechecker happy.
def softmax_sample(distribution, temperature: float):
    return 0, 0

def launch_job(f, *args):
    f(*args)

def make_uniform_network():
    return Network()


config = make_chess_config()
storage = SharedStorage()
replayBuffer = ReplayBuffer(config)
train_network(config, storage, replayBuffer)
print("Premi un tasto per uscire")
input()