import os
import music21 as m21
import json


# Load .krn songs
def load_songs(data_path, max_songs_nb):
    songs = []
    for path, subdirs, files in os.walk(data_path):
        for file in files:
            if file[-3:] == "krn":
                #print(os.path.join(path, file))
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
                max_songs_nb -= 1
                if max_songs_nb == 0 : return songs
    return songs



# Load text file
def load(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song


# Load json file (and return its length)
def load_json(file_path):
    with open(file_path, "r") as fp:
        mappings = json.load(fp)
    return mappings, len(mappings)



# durations are expressed in quarter length
ACCEPTABLE_DURATIONS = [
    0.25, # 16th note
    0.5, # 8th note
    0.75,
    1.0, # quarter note
    1.5,
    2, # half note
    3,
    4 # whole note
]

def has_acceptable_durations(song, acceptable_durations):
    for note in song.flatten().notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True




# Transposition en Cmaj/Amin
def transpose(song, print_enabled=False):
    # transpose song in Cmaj/Amin


    # get key signature
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measures_part0[0][4]
    if print_enabled : print("old key : ", key)

    # estimate key if not indicated
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")

    #get interval for transposition
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
    
    transposed_song = song.transpose(interval)

    return transposed_song




# Encode song
def encode_song(song, time_step=0.25):
    """Converts a score into a time-series-like music representation. Each item in the encoded list represents 'min_duration'
    quarter lengths. The symbols used at each step are: integers for MIDI notes, 'r' for representing a rest, and '_'
    for representing notes/rests that are carried over into a new time step. Here's a sample encoding:

        ["r", "_", "60", "_", "_", "_", "72" "_"]

    :param song (m21 stream): Piece to encode
    :param time_step (float): Duration of each time step in quarter length
    :return:
    """

    encoded_song = []

    for event in song.flatten().notesAndRests:

        # handle notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi # 60
        # handle rests
        elif isinstance(event, m21.note.Rest):
            symbol = "r"

        # convert the note/rest into time series notation
        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):

            # if it's the first time we see a note/rest, let's encode it. Otherwise, it means we're carrying the same
            # symbol in a new time step
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    # cast encoded song to str
    encoded_song = " ".join(map(str, encoded_song))

    return encoded_song





# Mettre toutes les musiques encodées dans un fichier texte
def create_single_file_dataset(dataset_path, file_dataset_path, sequence_length):
    """Generates a file collating all the encoded songs and adding new piece delimiters.

    :param dataset_path (str): Path to folder containing the encoded songs
    :param file_dataset_path (str): Path to file for saving songs in single file
    :param sequence_length (int): # of time steps to be considered for training (64 ~ 2 mesures)
    :return songs (str): String containing all songs in dataset + delimiters
    """

    new_song_delimiter = "/ " * sequence_length
    songs = ""

    # load encoded songs and add delimiters
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)
            songs = songs + song + " " + new_song_delimiter

    # remove empty space from last character of string
    songs = songs[:-1]

    # save string that contains all the dataset
    with open(file_dataset_path, "w") as fp:
        fp.write(songs)

    return songs



# Mapping des symboles utilisés par l'encodage
def create_mapping(songs, mapping_path):
    """Creates a json file that maps the symbols in the song dataset onto integers

    :param songs (str): String with all songs
    :param mapping_path (str): Path where to save mapping
    :return:
    """
    mappings = {}

    # identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))

    # create mappings
    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i

    # save voabulary to a json file
    with open(mapping_path, "w") as fp:
        json.dump(mappings, fp, indent=4)






def convert_to_midi(melody, step_duration=0.25):
    """Converts a melody into a MIDI stream

    :param melody (list of str):
    :param min_duration (float): Duration of each time step in quarter length
    :return: midi stream
    """

    # create a music21 stream
    stream = m21.stream.Stream()

    start_symbol = None
    step_counter = 1

    # parse all the symbols in the melody and create note/rest objects
    for i, symbol in enumerate(melody):

        # handle case in which we have a note/rest
        if symbol != "_" or i + 1 == len(melody):

            # ensure we're dealing with note/rest beyond the first one
            if start_symbol is not None:

                quarter_length_duration = step_duration * step_counter # 0.25 * 4 = 1

                # handle rest
                if start_symbol == "r":
                    m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                # handle note
                else:
                    m21_event = m21.note.Note(int(start_symbol), quarterLength=quarter_length_duration)

                stream.append(m21_event)

                # reset the step counter
                step_counter = 1

            start_symbol = symbol

        # handle case in which we have a prolongation sign "_"
        else:
            step_counter += 1

    return stream
    # # write the m21 stream to a midi file
    # stream.write(format, file_name)