import librosa
import os
import numpy
import pickle
import imageio
imageio.plugins.ffmpeg.download()
import moviepy.editor as MovieEditor
import matplotlib as plt
import youtubeopinion.database.db as db
from bson.binary import Binary
from pathlib import Path
from pydub import AudioSegment


video_directory = '../../Data/Videos/'
mp4_extension = '.mp4'
mp3_extesion = '.mp3'
wav_extension = '.wav'
fragment_extension = '-fragment-'
values_separator = ';'
feature_separator = '|'
duration_separator = '-'

def get_audio_from_video(video_code):

    print('## RETRIEVING AUDIO FROM VIDEO ##')

    current_directory = os.getcwd()
    file_name = ''
    separator = '/'

    file = Path(video_directory  + str(video_code) + separator + str(video_code) + mp3_extesion)

    if not os.path.exists(video_directory + str(video_code)):
        os.makedirs(video_directory + str(video_code))

    if file.is_file():
        print('## AUDIO FILE ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    os.chdir(video_directory + str(video_code))

    video = MovieEditor.VideoFileClip(video_code + mp4_extension)
    video.audio.write_audiofile(video_code + mp3_extesion)

    sound = AudioSegment.from_mp3(video_code + mp3_extesion)
    sound.export(video_code + wav_extension, format="wav")

    os.chdir(current_directory)

    print('## AUDIO FROM VIDEO RETRIEVED WITH SUCCESS! ##')


def generate_audio_features(sentences, video_code):

    get_audio_from_video(video_code)
    audio_fragmentation(sentences, video_code)

    database = db.get_db()

    if database.audio_features.find_one({'video_code': video_code}) is not None:
        print('## AUDIO FEATURES ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    print('## GENERATING AUDIO FEATURES ##')

    current_directory = os.getcwd()

    os.chdir(video_directory + str(video_code) + '/Fragments/Audio')

    database.audio_features.remove({'video_code': video_code})

    for code, sentence in sentences.items():

        start = sentence['start']
        end = sentence['end']

        sentence_start = int(float(sentence['start']) * 1000)

        y, sr = librosa.load(video_code + fragment_extension + str(sentence_start) + wav_extension)

        mfcc = Binary(pickle.dumps(librosa.feature.mfcc(y=y, sr=sr), protocol=2))
        mel_spectrogram = Binary(pickle.dumps(librosa.feature.melspectrogram(y=y, sr=sr), protocol=2))
        spectral_centroid = Binary(pickle.dumps(librosa.feature.spectral_centroid(y=y, sr=sr), protocol=2))
        spectral_contrast = Binary(pickle.dumps(librosa.feature.spectral_contrast(y=y, sr=sr), protocol=2))
        spectral_rolloff = Binary(pickle.dumps(librosa.feature.spectral_rolloff(y=y, sr=sr), protocol=2))
        poly_features = Binary(pickle.dumps(librosa.feature.poly_features(y=y, sr=sr), protocol=2))
        tonnetz = Binary(pickle.dumps(librosa.feature.tonnetz(y=y, sr=sr), protocol=2))
        zero_crossing_rate = Binary(pickle.dumps(librosa.feature.zero_crossing_rate(y=y), protocol=2))

        audio_feature = {
            'video_code': video_code,
            'start': start,
            'end': end,
            'mfcc': mfcc,
            'mel_spectogram': mel_spectrogram,
            'spectral_centroid': spectral_centroid,
            'spectral_contrast': spectral_contrast,
            'spectral_rolloff': spectral_rolloff,
            'poly_features': poly_features,
            'tonnetz': tonnetz,
            'zero_crossing_rate': zero_crossing_rate
        }

        database.audio_features.insert(audio_feature)

    os.chdir(current_directory)

    print('## AUDIO FEATURES GENERATED WITH SUCCESS! ##')


def audio_fragmentation(sentences, video_code):

    fragments_directory = video_directory + str(video_code) + '/Fragments'
    audio_directory = fragments_directory + '/Audio'

    if not os.path.exists(fragments_directory):
        os.makedirs(fragments_directory)

    if not os.path.exists(audio_directory):
        os.makedirs(audio_directory)
    else:
        return

    current_directory = os.getcwd()

    os.chdir(video_directory + str(video_code))

    sound = AudioSegment.from_mp3(video_code + wav_extension)

    os.chdir(current_directory)
    os.chdir(audio_directory)

    for code, sentence in sentences.items():

        start = int(float(sentence['start']) * 1000)
        end = int(float(sentence['end']) * 1000)

        fragment = sound[start:end]

        fragment.export(video_code + fragment_extension + str(start) + wav_extension, format="wav")

    os.chdir(current_directory)
