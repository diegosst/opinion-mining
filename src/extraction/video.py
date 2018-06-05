import pytube
import cv2
import os
import glob
import dlib
import math
import numpy as np
import opinion.database.db as db
from pathlib import Path
from moviepy.tools import subprocess_call
from moviepy.config import get_setting


cascPath = "../data/haarcascade_frontalface_default.xml"
PREDICTOR_PATH = "../data/shape_predictor_68_face_landmarks.dat/data"

video_extension = '.mp4'
frame_extension = '.jpg'
fragment_extension = '-fragment-'

LEFT_EYE_TOP_MIDDLE = 37
LEFT_EYE_BOTTOM_MIDDLE = 41
LEFT_EYE_RIGHT_POINT = 39
LEFT_EYE_LEFT_POINT = 36

RIGHT_EYE_TOP_MIDDLE = 44
RIGHT_EYE_BOTTOM_MIDDLE = 46
RIGHT_EYE_RIGHT_POINT = 45
RIGHT_EYE_LEFT_POINT = 42

MOUTH_TOP_MIDDLE = 51
MOUTH_BOTTOM_MIDDLE = 57
MOUTH_RIGHT_POINT = 54
MOUTH_LEFT_POINT = 48

RIGHT_EYEBROW_MIDDLE = 24
RIGHT_EYEBROW_RIGHT_POINT = 26
RIGHT_EYEBROW_LEFT_POINT = 22

LEFT_EYEBROW_MIDDLE = 19
LEFT_EYEBROW_RIGHT_POINT = 21
LEFT_EYEBROW_LEFT_POINT = 17

NOSE_BOTTOM_POINT = 33


def get_video_from_youtube(video_code):

    print('## DOWNLOADING VIDEO FROM YOUTUBE ##')

    videos_directory = '../data/videos/' + str(video_code)
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

    feature_extraction(sentences, video_code)

    print('## VIDEO FEATURES GENERATED WITH SUCCESS! ##')


def video_fragmentation(sentences, video_code):

    videos_directory = '../data/videos/' + str(video_code)
    fragments_directory = videos_directory + '/fragments'
    video_directory = fragments_directory + '/video'

    if not os.path.exists(fragments_directory):
        os.makedirs(fragments_directory)

    if not os.path.exists(video_directory):
        os.makedirs(video_directory)
    else:
        return

    current_directory = os.getcwd()

    os.chdir(videos_directory)

    for sentence in sentences:

        start = int(sentence['start'])
        end = int(sentence['end'])

        fragment_name = (video_code + fragment_extension + str(start) + video_extension)

        if (start - end) == 0:
            continue

        extract_subclip((video_code + video_extension), start/1000, end/1000, 30, 6000, targetname=(fragment_name))

        os.rename(fragment_name, 'fragments/video/' + fragment_name)

    os.chdir(current_directory)


def frames_fragmentation(sentences, video_code):

    videos_directory = '../data/videos/' + str(video_code)
    fragments_directory = videos_directory + '/fragments'
    video_directory = fragments_directory + '/video'
    frames_directory = fragments_directory + '/frames'

    if not os.path.exists(fragments_directory):
        os.makedirs(fragments_directory)

    if not os.path.exists(frames_directory):
        os.makedirs(frames_directory)
    else:
        return

    current_directory = os.getcwd()

    os.chdir(video_directory)

    print('## STARTING VIDEO FRAME EXTRACTION ##')

    for sentence in sentences:

        start = int(sentence['start'])

        print('## GENERATING FRAMES FOR VIDEO WITH START TIME ' + str(start) + ' ##')

        fragment_name = (video_code + fragment_extension + str(start) + video_extension)

        frame_folder = '../frames/' + str(start)

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


def feature_extraction(sentences, video_code):
    database = db.get_db()

    if database.video_features.find_one({'video_code': video_code}) is not None:
        print('## VIDEO FEATURES ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    videos_directory = '../data/videos/' + str(video_code)
    fragments_directory = videos_directory + '/fragments'
    frames_directory = fragments_directory + '/frames'

    current_directory = os.getcwd()

    faceCascade = cv2.CascadeClassifier(cascPath)

    predictor = dlib.shape_predictor(PREDICTOR_PATH)

    frames_size = 0

    faces_zero = 0
    faces_one = 0
    faces_more_than_one = 0

    for sentence in sentences:

        start = int(sentence['start'])
        end = int(sentence['end'])

        os.chdir(frames_directory + '/' + str(start))

        print('## GENERATING FEATURE FOR SENTENCE ' + str(start) + ' ##')

        frames_size += len(os.listdir())

        for file in os.listdir():

            # Read the image
            image = cv2.imread(file)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=20,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) < 1:
                faces_zero += 1
            elif len(faces) == 1:
                faces_one += 1
            else:
                faces_more_than_one += 1

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Converting the OpenCV rectangle coordinates to Dlib rectangle
                dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

                landmarks = np.matrix([[p.x, p.y]
                                       for p in predictor(image, dlib_rect).parts()])

                mouth_horizontal = calculate_distance(landmarks[MOUTH_RIGHT_POINT], landmarks[MOUTH_LEFT_POINT])
                mouth_vertical = calculate_distance(landmarks[MOUTH_TOP_MIDDLE], landmarks[MOUTH_BOTTOM_MIDDLE])
                nose_to_mouth_left = calculate_distance(landmarks[NOSE_BOTTOM_POINT], landmarks[MOUTH_LEFT_POINT])
                nose_to_mouth_right = calculate_distance(landmarks[NOSE_BOTTOM_POINT], landmarks[MOUTH_RIGHT_POINT])
                nose_to_right_eyebrow_left = calculate_distance(landmarks[NOSE_BOTTOM_POINT], landmarks[RIGHT_EYEBROW_LEFT_POINT])
                nose_to_right_eyebrow_right = calculate_distance(landmarks[NOSE_BOTTOM_POINT], landmarks[RIGHT_EYEBROW_RIGHT_POINT])
                nose_to_left_eyebrow_right = calculate_distance(landmarks[NOSE_BOTTOM_POINT], landmarks[LEFT_EYEBROW_RIGHT_POINT])
                nose_to_left_eyebrow_left = calculate_distance(landmarks[NOSE_BOTTOM_POINT], landmarks[LEFT_EYEBROW_LEFT_POINT])
                left_eye_horizontal = calculate_distance(landmarks[LEFT_EYE_LEFT_POINT], landmarks[LEFT_EYE_RIGHT_POINT])
                left_eye_vertical = calculate_distance(landmarks[LEFT_EYE_TOP_MIDDLE], landmarks[LEFT_EYE_BOTTOM_MIDDLE])
                left_eye_right_to_mouth_left = calculate_distance(landmarks[LEFT_EYE_RIGHT_POINT], landmarks[MOUTH_LEFT_POINT])
                right_eye_horizontal = calculate_distance(landmarks[RIGHT_EYE_LEFT_POINT], landmarks[RIGHT_EYE_RIGHT_POINT])
                right_eye_vertical = calculate_distance(landmarks[RIGHT_EYE_TOP_MIDDLE], landmarks[RIGHT_EYE_BOTTOM_MIDDLE])
                right_eye_left_to_mouth_right = calculate_distance(landmarks[RIGHT_EYE_LEFT_POINT], landmarks[MOUTH_RIGHT_POINT])
                eyebrows_distance = calculate_distance(landmarks[LEFT_EYEBROW_RIGHT_POINT], landmarks[RIGHT_EYEBROW_LEFT_POINT])
                right_eyebrow_middle_to_right_eye_top = calculate_distance(landmarks[RIGHT_EYEBROW_MIDDLE], landmarks[RIGHT_EYE_TOP_MIDDLE])
                right_eyebrow_middle_to_right_eye_bottom = calculate_distance(landmarks[RIGHT_EYEBROW_MIDDLE], landmarks[RIGHT_EYE_BOTTOM_MIDDLE])
                left_eyebrow_middle_to_left_eye_top = calculate_distance(landmarks[LEFT_EYEBROW_MIDDLE], landmarks[LEFT_EYE_TOP_MIDDLE])
                left_eyebrow_middle_to_left_eye_bottom = calculate_distance(landmarks[LEFT_EYEBROW_MIDDLE], landmarks[LEFT_EYE_BOTTOM_MIDDLE])

                video_feature = {
                    'video_code': video_code,
                    'start': start,
                    'end': end,
                    'mouth_horizontal': mouth_horizontal,
                    'mouth_vertical': mouth_vertical,
                    'nose_to_mouth_left': nose_to_mouth_left,
                    'nose_to_mouth_right': nose_to_mouth_right,
                    'nose_to_right_eyebrow_left': nose_to_right_eyebrow_left,
                    'nose_to_right_eyebrow_right': nose_to_right_eyebrow_right,
                    'nose_to_left_eyebrow_right': nose_to_left_eyebrow_right,
                    'nose_to_left_eyebrow_left': nose_to_left_eyebrow_left,
                    'left_eye_horizontal': left_eye_horizontal,
                    'left_eye_vertical': left_eye_vertical,
                    'left_eye_right_to_mouth_left': left_eye_right_to_mouth_left,
                    'right_eye_horizontal': right_eye_horizontal,
                    'right_eye_vertical': right_eye_vertical,
                    'right_eye_left_to_mouth_right': right_eye_left_to_mouth_right,
                    'eyebrows_distance': eyebrows_distance,
                    'right_eyebrow_middle_to_right_eye_top': right_eyebrow_middle_to_right_eye_top,
                    'right_eyebrow_middle_to_right_eye_bottom': right_eyebrow_middle_to_right_eye_bottom,
                    'left_eyebrow_middle_to_left_eye_top': left_eyebrow_middle_to_left_eye_top,
                    'left_eyebrow_middle_to_left_eye_bottom': left_eyebrow_middle_to_left_eye_bottom
                }

                database.video_features.insert(video_feature)

        os.chdir(current_directory)

    print('No faces per frame accurancy: ' + str(faces_zero / frames_size))
    print('One face per frame accurancy: ' + str(faces_one / frames_size))
    print('More than one face per frame accurancy: ' + str(faces_more_than_one / frames_size))


def calculate_distance(x, y):

    return math.sqrt((math.pow(x[(0, 0)] - y[(0, 0)], 2) + math.pow(x[(0, 1)] - y[(0, 1)], 2)))
