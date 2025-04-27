import os
import music21 as m21
import json
import numpy as np
import tensorflow.keras as keras
import matplotlib.pyplot as plt



def convert_songs_to_int(songs, mappings):
    # Conversion des datas  74 _ _ _ 69 en integers suivant le mapping
    
    int_songs = []

    songs = songs.split() # 74 _ _ _ 69 --> ['74', '_', '_', '_', '69']

    # map songs to int
    for symbol in songs:
        int_songs.append(mappings[symbol])

    return int_songs


#  ---------------------Générer séquences d'entrainement
def generate_training_sequences(sequence_length, songs, mappings):
    """Create input and output data samples for training. Each sample is a sequence.

    :param sequence_length (int): Length of each sequence. With a quantisation at 16th notes, 64 notes equates to 4 bars
    :param songs (string) : songs datas
    :param mappings (dict): mapping between 

    :return inputs (ndarray): Training inputs
    :return targets (ndarray): Training targets
    """

    # map songs to int
    int_songs = convert_songs_to_int(songs, mappings)

    inputs = [] # fenetre qu'on décalle
    targets = [] # note qu'on cherche à prédire à partir de la séquence d'input

    # generate the training sequences
    num_sequences = len(int_songs) - sequence_length
    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])

    # one-hot encode the sequences
    vocabulary_size = len(set(int_songs))
    # inputs size: (# of sequences, sequence length, vocabulary size)
    inputs = keras.utils.to_categorical(inputs, num_classes=vocabulary_size)
    targets = np.array(targets)

    return inputs, targets


#  --------------------- Construction du modèle
def build_model(output_units, num_units, loss, learning_rate):
    """Builds and compiles model

    :param output_units (int): Num output units
    :param num_units (list of int): Num of units in hidden layers
    :param loss (str): Type of loss function to use
    :param learning_rate (float): Learning rate to apply

    :return model (tf model)
    """

    # create the model architecture
    input = keras.layers.Input(shape=(None, output_units))
    x = keras.layers.LSTM(num_units[0])(input)
    x = keras.layers.Dropout(0.2)(x)

    output = keras.layers.Dense(output_units, activation="softmax")(x)

    model = keras.Model(input, output)

    # compile model
    model.compile(loss=loss,
                  optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
                  metrics=["accuracy"])

    model.summary()

    return model



# --------------------- Génération de mélodies

def sample_with_temperature(probabilites, temperature):
    """Samples an index from a probability array reapplying softmax using temperature

    :param predictions (nd.array): Array containing probabilities for each of the possible outputs.
    :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
        A number closer to 1 makes the generation more unpredictable.

    :return index (int): Selected output symbol
    """
    predictions = np.log(probabilites) / temperature
    probabilites = np.exp(predictions) / np.sum(np.exp(predictions))

    choices = range(len(probabilites)) # [0, 1, 2, 3]
    index = np.random.choice(choices, p=probabilites)

    return index


def generate_melody(model, start_symbols, mappings, seed, num_steps, max_sequence_len, temperature):
    """Generates a melody using the DL model and returns a midi file.

        :param seed (str): Melody seed with the notation used to encode the dataset
        :param num_steps (int): Number of steps to be generated
        :param max_sequence_len (int): Max number of steps in seed to be considered for generation
        :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
            A number closer to 1 makes the generation more unpredictable.

        :return melody (list of str): List with symbols representing a melody
    """

    # create seed with start symbols
    seed = seed.split()
    melody = seed
    seed = start_symbols + seed

    # map seed to int
    seed = [mappings[symbol] for symbol in seed]

    for _ in range(num_steps):
        # limit the seed to max_sequence_length
        seed = seed[-max_sequence_len:]
        
        # one-hot encode the seed
        onehot_seed = keras.utils.to_categorical(seed, num_classes=len(mappings))
        # (1, max_sequence_length, num of symbols in the vocabulary)
        onehot_seed = onehot_seed[np.newaxis, ...]

        # make a prediction
        probabilities = model.predict(onehot_seed)[0]
        # [0.1, 0.2, 0.1, 0.6] -> 1
        output_int = sample_with_temperature(probabilities, temperature)

        # update seed
        seed.append(output_int)

        # map int to our encoding
        output_symbol = [k for k, v in mappings.items() if v == output_int][0]

        # check whether we're at the end of a melody
        if output_symbol == "/":
            break

        # update melody
        melody.append(output_symbol)

    return melody
