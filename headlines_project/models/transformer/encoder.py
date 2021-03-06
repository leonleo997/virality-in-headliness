from headlines_project.lib import *
from tensorflow.python.keras.layers import Dropout

from .encoder_layer import TransformerEncoderLayer
from .positional_embedding import PositionalEmbedding

class TransformerEncoder(tf.keras.models.Model):
    def __init__(self, num_layers, d_model, num_heads, dff, embedding_layer,
                 causal_attention=False, dropout_rate=0.2):
        """

        :param num_layers:
        :param d_model:
        :param num_heads:
        :param dff:
        :param embedding_layer:
        :param causal_attention:
        :param dropout_rate:
        """
        super(TransformerEncoder, self).__init__()
        self.d_model = d_model
        self.num_layers = num_layers
        self.embedding_layer = embedding_layer
        self.num_heads = num_heads
        self.encoder_layers = [TransformerEncoderLayer(d_model, self.num_heads, dff, rate=dropout_rate)
                               for _ in range(num_layers)]
        error_message = f"d_model and embedding output dim must be equal, {d_model} != {self.embedding_layer.output_dim}"
        assert d_model == self.embedding_layer.output_dim, error_message
        self.positional_embedding = PositionalEmbedding(self.embedding_layer)
        self.causal_attention = causal_attention
        self.dropout = Dropout(dropout_rate)

    def call(self, input_tokens, training):
        """
        Args:
          input_tokens(tf.Tensor): tensor with shape (batch_size, max_length) of tokens
          training(bool): Whether model is training or not

        Returns:
          x(tf.Tensor): Contextualized word embeddings (batch_size, input_seq_len, d_model)
          layers_att_weights(dict): dictionary with layer names as keys and
                              attention weights of shape (batch_size, num_heads, max_length, max_length)
                              for each layer as values 
        """
        embeddings, mask = self.positional_embedding(input_tokens, training, causal_attention=self.causal_attention)

        x = self.dropout(embeddings, training=training)

        layers_att_weights = {}

        for i in range(self.num_layers):
            x, weights = self.encoder_layers[i](x, training, mask)
            layers_att_weights[f"encoder_layer_{i + 1}"] = weights
        return x, layers_att_weights
