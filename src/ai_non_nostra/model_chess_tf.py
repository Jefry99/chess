"""
Defines the actual model for making policy and value predictions given an observation.
"""

import ftplib
import hashlib
import json
import os

from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Conv2D, Dense, Flatten, Activation, Add, BatchNormalization
#from tensorflow.keras.regularizers import L2 as l2
from tensorflow.keras.regularizers import l2
from tensorflow.keras.models import model_from_json

from src.ai_non_nostra.config import Config
from src.ai_non_nostra.api_chess import ChessModelAPI

# noinspection PyPep8Naming



class ChessModel:
    """
    The model which can be trained to take observations of a game of chess and return value and policy
    predictions.

    Attributes:
        :ivar Config config: configuration to use
        :ivar Model model: the Keras model to use for predictions
        :ivar digest: basically just a hash of the file containing the weights being used by this model
        :ivar ChessModelAPI api: the api to use to listen for and then return this models predictions (on a pipe).
    """
    def __init__(self, config: Config):
        self.config = config
        self.api = None
        self.model = None  # type: Model
        self.digest = None

    def get_pipes(self, num = 1):
        """
        Creates a list of pipes on which observations of the game state will be listened for. Whenever
        an observation comes in, returns policy and value network predictions on that pipe.

        :param int num: number of pipes to create
        :return str(Connection): a list of all connections to the pipes that were created
        """
        if self.api is None:
            self.api = ChessModelAPI(self)
            self.api.start()
        return [self.api.create_pipe() for _ in range(num)]

    def build(self):
        """
        Builds the full Keras model and stores it in self.model.
        """
        mc = self.config.model
        in_x = x = Input((18, 8, 8))

        # (batch, channels, height, width)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_first_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg),
                   name="input_conv-"+str(mc.cnn_first_filter_size)+"-"+str(mc.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name="input_batchnorm")(x)
        x = Activation("relu", name="input_relu")(x)

        for i in range(mc.res_layer_num):
            x = self._build_residual_block(x, i + 1)

        res_out = x
        
        # for policy output
        x = Conv2D(filters=2, kernel_size=1, data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg),
                    name="policy_conv-1-2")(res_out)
        x = BatchNormalization(axis=1, name="policy_batchnorm")(x)
        x = Activation("relu", name="policy_relu")(x)
        x = Flatten(name="policy_flatten")(x)
        # no output for 'pass'
        policy_out = Dense(self.config.n_labels, kernel_regularizer=l2(mc.l2_reg), activation="softmax", name="policy_out")(x)

        # for value output
        x = Conv2D(filters=4, kernel_size=1, data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg),
                    name="value_conv-1-4")(res_out)
        x = BatchNormalization(axis=1, name="value_batchnorm")(x)
        x = Activation("relu",name="value_relu")(x)
        x = Flatten(name="value_flatten")(x)
        x = Dense(mc.value_fc_size, kernel_regularizer=l2(mc.l2_reg), activation="relu", name="value_dense")(x)
        value_out = Dense(1, kernel_regularizer=l2(mc.l2_reg), activation="tanh", name="value_out")(x)

        self.model = Model(in_x, [policy_out, value_out], name="chess_model")

    def _build_residual_block(self, x, index):
        mc = self.config.model
        in_x = x
        res_name = "res"+str(index)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg), 
                   name=res_name+"_conv1-"+str(mc.cnn_filter_size)+"-"+str(mc.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name=res_name+"_batchnorm1")(x)
        x = Activation("relu",name=res_name+"_relu1")(x)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(mc.l2_reg), 
                   name=res_name+"_conv2-"+str(mc.cnn_filter_size)+"-"+str(mc.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name="res"+str(index)+"_batchnorm2")(x)
        x = Add(name=res_name+"_add")([in_x, x])
        x = Activation("relu", name=res_name+"_relu2")(x)
        return x

    @staticmethod
    def fetch_digest(weight_path):
        if os.path.exists(weight_path):
            m = hashlib.sha256()
            with open(weight_path, "rb") as f:
                m.update(f.read())
            return m.hexdigest()

    def load(self, config_path, weight_path):
        """

        :param str config_path: path to the file containing the entire configuration
        :param str weight_path: path to the file containing the model weights
        :return: true iff successful in loading
        """
        if os.path.exists(config_path) and os.path.exists(weight_path):
            with open(config_path, "rt") as f:
                self.model = model_from_json(json.load(f))
            self.model.load_weights(weight_path)
            self.model.make_predict_function()
            self.digest = self.fetch_digest(weight_path)
            return True
        else:
            return False

    def save(self, config_path, weight_path):
        """

        :param str config_path: path to save the entire configuration to
        :param str weight_path: path to save the model weights to
        """
        with open(config_path, "wt") as f:
            json.dump(self.model.to_json(), f)
            self.model.save_weights(weight_path)
        self.digest = self.fetch_digest(weight_path)
