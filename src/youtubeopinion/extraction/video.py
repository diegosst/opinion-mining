import pytube
import cv2
import os
import glob
from pathlib import Path
from moviepy.tools import subprocess_call
from moviepy.config import get_setting


video_extension = '.mp4'
frame_extension = '.jpg'
fragment_extension = '-fragment-'

def get_video_from_youtube(video_code):

    print('## DOWNLOADING VIDEO FROM YOUTUBE ##')

    videos_directory = '../../Data/Videos/' + str(video_code)
    current_directory = os.getcwd()
    file_name = ''
    separator = '/'

    file = Path(videos_directory + separator + str(video_code) + video_extension)

    if not os.path.exists(videos_directory):
        os.makedirs(videos_directory)

    if file.is_file():
        print('## VIDEO FILE ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    os.chdir(videos_directory)

    # Downloading video direct from youtube.
    pytube.YouTube('http://youtube.com/watch?v=' + str(video_code)).streams.first().download()

    for file in glob.glob('*' + video_extension):
        file_name = str(file)


    os.rename(file_name, video_code + video_extension)

    os.chdir(current_directory)

    print('## VIDEO DOWNLOADED WITH SUCCESS! ##')


def generate_video_features(sentences, video_code):

    video_fragmentation(sentences, video_code)
    frames_fragmentation(sentences, video_code)

    print('## GENERATING VIDEO FEATURES ##')



    print('## VIDEO FEATURES GENERATED WITH SUCCESS! ##')


def video_fragmentation(sentences, video_code):

    videos_directory = '../../Data/Videos/' + str(video_code)
    fragments_directory = videos_directory + '/Fragments'
    video_directory = fragments_directory + '/Video'

    if not os.path.exists(fragments_directory):
        os.makedirs(fragments_directory)

    if not os.path.exists(video_directory):
        os.makedirs(video_directory)
    else:
        return

    current_directory = os.getcwd()

    os.chdir(videos_directory)

    for code, sentence in sentences.items():

        start = float(sentence['start'])
        end = float(sentence['end'])

        fragment_name = (video_code + fragment_extension + str(int(start * 1000)) + video_extension)

        extract_subclip((video_code + video_extension), start, end, 30, 6000, targetname=(fragment_name))

        os.rename(fragment_name, 'Fragments/Video/' + fragment_name)

    os.chdir(current_directory)


def frames_fragmentation(sentences, video_code):

    videos_directory = '../../Data/Videos/' + str(video_code)
    fragments_directory = videos_directory + '/Fragments'
    video_directory = fragments_directory + '/Video'
    frames_directory = fragments_directory + '/Frames'

    if not os.path.exists(fragments_directory):
        os.makedirs(fragments_directory)

    if not os.path.exists(frames_directory):
        os.makedirs(frames_directory)
    else:
        return

    current_directory = os.getcwd()

    os.chdir(video_directory)

    print('## STARTING VIDEO FRAME EXTRACTION ##')

    for code, sentence in sentences.items():

        start = int(float(sentence['start']) * 1000)
        end = int(float(sentence['end']) * 1000)

        print('## GENERATING FRAMES FOR VIDEO WITH START TIME ' + str(start) + ' ##')

        fragment_name = (video_code + fragment_extension + str(start) + video_extension)
        frame_name = (video_code + fragment_extension + str(start) + frame_extension)

        frame_folder = '../Frames/' + str(start)

        if not os.path.exists(frame_folder):
            os.makedirs(frame_folder)

        vidcap = cv2.VideoCapture(fragment_name)

        count = 0
        success = True
        while success:

            success, image = vidcap.read()

            if success:

                print('## FRAMES ' + str(start) + '-' + str(count) + ' GENERATED! ##')

                file_name = (video_code + fragment_extension + str(start) + '-' + str(count) + frame_extension)
                cv2.imwrite(file_name, image)
                os.rename(file_name, frame_folder + '/' + file_name)
                count += 1

    os.chdir(current_directory)


def extract_subclip(filename, t1, t2, fps, bv, targetname=None):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000 * t) for t in [t1, t2]]
        targetname = name + "%sSUB%d_%d.%s"(name, T1, T2, ext)

    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-ss", "%0.2f" % t1,
           "-i", filename,
           "-vcodec", "copy", "-acodec", "copy",
           "-to", "%0.2f" % (t2 - t1),
           targetname]

    subprocess_call(cmd)