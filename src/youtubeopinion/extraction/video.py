import pytube
import cv2
import os
import glob
import dlib
import numpy as np
import youtubeopinion.database.db as db
from pathlib import Path
from moviepy.tools import subprocess_call
from moviepy.config import get_setting


cascPath = "../data/haarcascade_frontalface_default.xml"
PREDICTOR_PATH = "../data/shape_predictor_68_face_landmarks.dat/data"

video_extension = '.mp4'
frame_extension = '.jpg'
fragment_extension = '-fragment-'

#LEFT_EYE = 0
#RIGHT_EYE = 1
LEFT_EYE_INNER_CORNER = 40
LEFT_EYE_OUTER_CORNER = 37
LEFT_EYE_LOWER_LINE = 41
LEFT_EYE_UPPER_LINE = 38
#LEFT_EYE_LEFT_IRIS_CORNER = 29
#LEFT_EYE_RIGHT_IRIS_CORNER = 30
RIGHT_EYE_INNER_CORNER = 25
RIGHT_EYE_OUTER_CORNER = 26
RIGHT_EYE_LOWER_LINE = 48
RIGHT_EYE_UPPER_LINE = 45
#RIGHT_EYE_LEFT_IRIS_CORNER = 33
#RIGHT_EYE_RIGHT_IRIS_CORNER = 34
LEFT_EYEBROW_INNER_CORNER = 22
LEFT_EYEBROW_MIDDLE = 20
LEFT_EYEBROW_OUTER_CORNER = 18
RIGHT_EYEBROW_INNER_CORNER = 23
RIGHT_EYEBROW_MIDDLE = 25
RIGHT_EYEBROW_OUTER_CORNER = 27
MOUTH_TOP = 52
MOUTH_BOTTOM = 58


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

    for sentence in sentences:

        start = int(sentence['start'])
        end = int(sentence['end'])

        os.chdir(frames_directory + '/' + str(start))

        print('## GENERATING FEATURE FOR SENTENCE ' + str(start) + ' ##')

        for file in os.listdir():

            # Read the image
            image = cv2.imread(file)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=5,
                minSize=(100, 100),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Converting the OpenCV rectangle coordinates to Dlib rectangle
                dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

                landmarks = np.matrix([[p.x, p.y]
                                       for p in predictor(image, dlib_rect).parts()])

                #right_eye_left_eye = landmarks[RIGHT_EYE] - landmarks[LEFT_EYE]
                inner_outer_corner_left_eye = landmarks[LEFT_EYE_INNER_CORNER] - landmarks[LEFT_EYE_OUTER_CORNER]
                upper_lower_line_left_eye = landmarks[LEFT_EYE_UPPER_LINE] - landmarks[LEFT_EYE_LOWER_LINE]
                #left_iris_corner_right_iris_corner_left_eye = landmarks[LEFT_EYE_LEFT_IRIS_CORNER] - landmarks[LEFT_EYE_RIGHT_IRIS_CORNER]
                inner_outer_corner_right_eye = landmarks[RIGHT_EYE_INNER_CORNER] - landmarks[RIGHT_EYE_OUTER_CORNER]
                upper_lower_line_right_eye = landmarks[RIGHT_EYE_UPPER_LINE] - landmarks[RIGHT_EYE_LOWER_LINE]
                #left_iris_corner_right_iris_corner_right_eye = landmarks[RIGHT_EYE_LEFT_IRIS_CORNER] - landmarks[RIGHT_EYE_RIGHT_IRIS_CORNER]
                left_eyebrow_inner_outer_corner = landmarks[LEFT_EYEBROW_INNER_CORNER] - landmarks[LEFT_EYEBROW_OUTER_CORNER]
                right_eyebrow_inner_outer_corner = landmarks[RIGHT_EYEBROW_INNER_CORNER] - landmarks[RIGHT_EYEBROW_OUTER_CORNER]
                top_mouth_bottom_mouth = landmarks[MOUTH_TOP] - landmarks[MOUTH_BOTTOM]

                video_feature = {
                    'video_code': video_code,
                    'start': start,
                    'end': end,
                    #'right_eye_left_eye': get_formatted_distance(right_eye_left_eye),
                    'inner_outer_corner_left_eye': get_formatted_distance(inner_outer_corner_left_eye),
                    'upper_lower_line_left_eye': get_formatted_distance(upper_lower_line_left_eye),
                    #'left_iris_corner_right_iris_corner_left_eye': get_formatted_distance(left_iris_corner_right_iris_corner_left_eye),
                    'inner_outer_corner_right_eye': get_formatted_distance(inner_outer_corner_right_eye),
                    'upper_lower_line_right_eye': get_formatted_distance(upper_lower_line_right_eye),
                    #'left_iris_corner_right_iris_corner_right_eye': get_formatted_distance(left_iris_corner_right_iris_corner_right_eye),
                    'left_eyebrow_inner_outer_corner': get_formatted_distance(left_eyebrow_inner_outer_corner),
                    'right_eyebrow_inner_outer_corner': get_formatted_distance(right_eyebrow_inner_outer_corner),
                    'top_mouth_bottom_mouth': get_formatted_distance(top_mouth_bottom_mouth)
                }

                database.video_features.insert(video_feature)

        os.chdir(current_directory)


def get_formatted_distance(matrix):
    return '(' + str(matrix[(0, 0)]) + ', ' + str(matrix[(0, 1)]) + ')'
