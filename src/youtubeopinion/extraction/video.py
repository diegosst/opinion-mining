import pytube
import os
import glob
from pathlib import Path


def get_video_from_youtube(video_code):

    print('## DOWNLOADING VIDEO FROM YOUTUBE ##')

    video_directory = '../../Data/Videos/' + str(video_code)
    current_directory = os.getcwd()
    file_name = ''
    extension = '.mp4'
    separator = '/'

    file = Path(video_directory + separator + str(video_code) + extension)

    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    if file.is_file():
        print('## VIDEO FILE ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    os.chdir(video_directory)

    # Downloading video direct from youtube.
    pytube.YouTube('http://youtube.com/watch?v=' + str(video_code)).streams.first().download()

    for file in glob.glob('*' + extension):
        file_name = str(file)


    os.rename(file_name, video_code + extension)

    os.chdir(current_directory)

    print('## VIDEO DOWNLOADED WITH SUCCESS! ##')