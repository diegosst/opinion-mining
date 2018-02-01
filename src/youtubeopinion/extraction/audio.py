import librosa
import os
import numpy
import imageio
imageio.plugins.ffmpeg.download()
import moviepy.editor as MovieEditor
import matplotlib as plt
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

    print('## GENERATING AUDIO FEATURES ##')

    directory = '../../Data/Videos/' + str(video_code) + '/Extractions/'
    complement = '_audio_features.txt'

    file = Path(directory + str(video_code) + complement)

    if not os.path.exists(directory):
        os.makedirs(directory)

    if file.is_file():
        print('## AUDIO FEATURES FILE ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    file = open(directory + str(video_code) + complement, 'w')

    current_directory = os.getcwd()

    os.chdir(video_directory + str(video_code) + '/Fragments/Audio')

    message = ''

    for code, sentence in sentences.items():

        sentence_start = sentence['start']
        sentence_end = sentence['end']

        start = int(float(sentence['start']) * 1000)

        y, sr = librosa.load(video_code + fragment_extension + str(start) + wav_extension)

        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        poly_features = librosa.feature.poly_features(y=y, sr=sr)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y)

        # [START-END]MFCC(MIN);MFCC(MAX)|MEL_SPEC(MIN);MEL_SPEC(MAX)|...

        message += '[' + sentence_start + duration_separator + sentence_end + ']'
        message += message_constructor(mfcc, 1)
        message += message_constructor(mel_spectrogram, 1)
        message += message_constructor(spectral_centroid, 1)
        message += message_constructor(spectral_contrast, 1)
        message += message_constructor(spectral_rolloff, 1)
        message += message_constructor(poly_features, 1)
        message += message_constructor(tonnetz, 1)
        message += message_constructor(zero_crossing_rate, 0)


    file.write(message)
    file.close()

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


def message_constructor(value, add_separator):

    return str(round(float(numpy.amin(value)), 2)) + values_separator + \
           str(round(float(numpy.amax(value)), 2)) + (feature_separator if bool(add_separator) else '\n')