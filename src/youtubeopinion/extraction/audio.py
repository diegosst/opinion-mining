import librosa
import os
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


def generate_audio_features(video_code):

    get_audio_from_video(video_code)

    print('## GENERATING AUDIO FEATURES ##')

    audio_features = {}

    current_directory = os.getcwd()

    os.chdir(video_directory + str(video_code))

    y, sr = librosa.load(video_code + wav_extension)

    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    poly_features = librosa.feature.poly_features(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y)

    os.chdir(current_directory)

    audio_features = {
        'mfcc' : mfcc,
        'mel_spectrogram' : mel_spectrogram,
        'spectral_centroid' : spectral_centroid,
        'spectral_contrast' : spectral_contrast,
        'spectral_rolloff' : spectral_rolloff,
        'poly_features' : poly_features,
        'tonnetz' : tonnetz,
        'zero_crossing_rate' : zero_crossing_rate
    }

    print('## AUDIO FEATURES GENERATED WITH SUCCESS! ##')

    return audio_features

# TODO: USE THIS TO GENERATE FRAGMENTED AUDIOS
# EXAMPLE OF AUDIO FRAGMENTATION
# files_path = 'a'
# file_name = 'a'
#
# startMin = 9
# startSec = 50
#
# endMin = 13
# endSec = 30
#
# # Time to miliseconds
# startTime = startMin*60*1000+startSec*1000
# endTime = endMin*60*1000+endSec*1000
#
# # Opening file and extracting segment
# song = AudioSegment.from_mp3( files_path+file_name+'.mp3' )
# extract = song[startTime:endTime]
#
# # Saving
# extract.export( file_name+'-extract.mp3', format="mp3")