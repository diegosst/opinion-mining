import _pickle as pickle
import os
import random

import numpy as np
import pandas
import pymongo
from pymongo import MongoClient
from sklearn.metrics import recall_score, precision_score
from sklearn.svm import LinearSVC

import opinion.helper.util as util

video_features_quantity = 19
audio_features_quantity = 8


def training_model(datas, code, limit, preparation_time, option, one_disabled, save):

    start_time = util.current_milli_time()

    client = MongoClient('localhost', 27017)

    database = client.opinion_database

    scores = cross_validation(datas)

    if save:
        svc = LinearSVC()
        for data in datas:
            svc.fit(data['x'], data['y'])

    precision = np.average(scores['precision'])
    recall = np.average(scores['recall'])

    print("Precision: %0.2f" % precision)
    print("Recall: %0.2f" % recall)

    if one_disabled is None:
        features_selection = 'all'
    elif one_disabled:
        features_selection = 'one_disabled'
    else:
        features_selection = 'one_active'

    version = database.models.find({'code': code, 'features_selection': features_selection, 'option': option}).count() + 1
    splits = 5

    end_time = util.current_milli_time()

    model = {'code': code,
             'model': pickle.dumps(svc) if save else '',
             'type': 'tree',
             'precision': precision,
             'recall': recall,
             'limit': limit,
             'kfold': splits,
             'version': version,
             'train_time': end_time - start_time,
             'preparation_time': preparation_time,
             'option': '' if option is None else option,
             'features_selection': features_selection
             }

    database.models.insert(model)

    client.close()


def cross_validation(datas):

    scores = dict()
    scores['precision'] = []
    scores['recall'] = []

    for i in range(0, len(datas)):

        svc = LinearSVC()

        for j in range(0, len(datas)):
            if j != i:
                x_train = datas[j]['x']
                y_train = datas[j]['y']
                svc.fit(x_train, y_train)

        test = datas[i]

        x_test = test['x']
        y_test = test['y']

        y_score = svc.predict(x_test)

        scores['precision'].append(precision_score(y_test, y_score, average="micro"))
        scores['recall'].append(recall_score(y_test, y_score, average="micro"))

    return scores


def generate_annotation_data():

    annotations_directory = '../data/annotations/'
    current_directory = os.getcwd()
    annotation_file = '-sentiment-annotation.xlsx'

    os.chdir(annotations_directory)

    client = MongoClient('localhost', 27017)

    database = client.opinion_database

    for file in os.listdir():

        video_code = file.split(annotation_file)[0]

        if database.annotations.find_one({'video_code': video_code}) is not None:
            print('## ANNOTATION ALREADY EXTRACTED, SKIPPING THIS STEP. ##')
            continue

        database.annotations.remove({'video_code': video_code})

        df = pandas.read_excel(video_code + annotation_file)

        starts = df['start']
        ends = df['end']
        sentiments = df['sentiment']

        annotations = []

        for i in range(0, len(starts)):
            annotation = {
                'video_code': video_code,
                'start': str(starts[i]),
                'end': str(ends[i]),
                'sentiment': int(sentiments[i])
            }

            annotations.append(annotation)

        database.annotations.insert(annotations)

    os.chdir(current_directory)

    client.close()


def get_test_and_train_annotations(limit, k):

    annotations = get_annotation_data(limit)

    size = len(annotations)

    division = size // k
    rest = size % k

    start = 0
    end = division

    splits = []

    for i in range(0, k):
        splits.append(annotations[start:end])
        start = end
        end += division

    if rest != 0:
        splits[len(splits) - 1] = splits[len(splits) - 1] + annotations[(start + division):len(annotations)]

    return splits


def get_annotation_data(limit):

    client = MongoClient('localhost', 27017)

    database = client.opinion_database

    annotations_negative = get_annotation(database, -1, limit)
    annotations_neutral = get_annotation(database, 0, limit)
    annotations_positive = get_annotation(database, 1, limit)

    print('ANNOTATIONS:')
    print('Negative: %d' % len(annotations_negative))
    print('Neutral: %d' % len(annotations_neutral))
    print('Positive: %d' % len(annotations_positive))

    annotations = annotations_positive + annotations_neutral + annotations_negative

    random.shuffle(annotations)

    client.close()

    return annotations


def get_annotation(database, polarity, limit):

    annotations = database.annotations.find({'sentiment': polarity}).sort([['video_code', pymongo.ASCENDING], ['start', pymongo.ASCENDING]])

    results = []

    indexes = list(range(0, annotations.count()))

    random.shuffle(indexes)

    for index in indexes:

        features = get_text_features(annotations[index], database)

        if features is not None:

            results.append(annotations[index])

        if len(results) == limit:

            return results


def append_results(results, annotations):

    for annotation in annotations:

        video_code = annotation['video_code']

        try:
            results[video_code]
        except KeyError:
            results[video_code] = []

        results[video_code].append(annotation)


def get_train_and_test_data(code, splits, video_options, audio_options):

    start_time = util.current_milli_time()

    datas = []

    for annotations in splits:

        x, y = get_features_data(code, annotations, video_options, audio_options)

        datas.append({'x': x, 'y': y})

    end_time = util.current_milli_time()

    return datas, end_time - start_time


# Code represents the type of analysis.
# Note: * means frames average for video modality
#
# 1         : video*
# 2         : audio
# 3         : text
# 4         : multimodal: video* + audio
# 5         : multimodal: video* + text
# 6         : multimodal: audio + text
# 7         : multimodal: audio + text + video*
# 8         : video
# 9         : multimodal: video + audio
# 10        : multimodal: video + text
# 11        : multimodal: audio + video + text
def get_features_data(code, annotations, video_options, audio_options):

    x = []
    y = []

    client = MongoClient('localhost', 27017)

    database = client.opinion_database

    positives = []
    neutrals = []
    negatives = []

    for annotation in annotations:

        if code is 1:

            results = get_video_features_filtered(annotation, database, video_options)

        elif code is 2:

            results = get_audio_features(annotation, database, audio_options)

        elif code is 3:

            results = get_text_features(annotation, database)

        elif code is 4:

            results = get_bimodal_va_features(annotation, database, True)

        elif code is 5:

            results = get_bimodal_vt_features(annotation, database, True)

        elif code is 6:

            results = get_bimodal_at_features(annotation, database)

        elif code is 7:

            results = get_multimodal_features(annotation, database, True)

        elif code is 8:

            results = get_video_features(annotation, database, video_options)

        elif code is 9:

            results = get_bimodal_va_features(annotation, database, False)

        elif code is 10:

            results = get_bimodal_vt_features(annotation, database, False)

        elif code is 11:

            results = get_multimodal_features(annotation, database, False)

        else:

            print('Could not find model type for code %d.' % code)
            return

        for result in results:

            if annotation['sentiment'] == 1:

                positives.append(result)

            elif annotation['sentiment'] == -1:

                negatives.append(result)

            else:

                neutrals.append(result)

        positives_np = np.array(positives)
        negatives_np = np.array(negatives)
        neutrals_np = np.array(neutrals)

        ones = np.full(np.shape(positives_np)[0], 1)
        minus_ones = np.full(np.shape(negatives_np)[0], -1)
        zeros = np.full(np.shape(neutrals_np)[0], 0)

        X = positives_np

        if negatives_np.size != 0:

            try:
                X = np.append(X, negatives_np, axis=0)
            except ValueError:
                X = negatives_np

        if neutrals_np.size != 0:

            try:
                X = np.append(X, neutrals_np, axis=0)
            except ValueError:
                X = neutrals_np

        Y = ones

        if minus_ones.size != 0:
            try:
                Y = np.append(Y, minus_ones, axis=0)
            except ValueError:
                Y = minus_ones
        if zeros.size != 0:
            try:
                Y = np.append(Y, zeros, axis=0)
            except ValueError:
                Y = zeros

        if len(x) == 0:
            x = X
        else:
            x = np.concatenate([x, X], axis=0)

        if len(y) == 0:
            y = Y
        else:
            y = np.concatenate([y, Y], axis=0)

    return x, y


def get_video_features(annotation, database, video_options):

    sentences = database.video_features.find({'video_code': annotation['video_code'], 'start': int(annotation['start']), 'end': int(annotation['end'])}).sort('start', pymongo.ASCENDING)

    if video_options is None:
        video_options = np.full(video_features_quantity, 1)

    results = []

    for sentence in sentences:

        result = []

        if video_options[0]:
            result.append(sentence['mouth_horizontal'])
        if video_options[1]:
            result.append(sentence['mouth_vertical'])
        if video_options[2]:
            result.append(sentence['nose_to_mouth_left'])
        if video_options[3]:
            result.append(sentence['nose_to_mouth_right'])
        if video_options[4]:
            result.append(sentence['nose_to_right_eyebrow_left'])
        if video_options[5]:
            result.append(sentence['nose_to_right_eyebrow_right'])
        if video_options[6]:
            result.append(sentence['nose_to_left_eyebrow_right'])
        if video_options[7]:
            result.append(sentence['nose_to_left_eyebrow_left'])
        if video_options[8]:
            result.append(sentence['left_eye_horizontal'])
        if video_options[9]:
            result.append(sentence['left_eye_vertical'])
        if video_options[10]:
            result.append(sentence['left_eye_right_to_mouth_left'])
        if video_options[11]:
            result.append(sentence['right_eye_horizontal'])
        if video_options[12]:
            result.append(sentence['right_eye_vertical'])
        if video_options[13]:
            result.append(sentence['right_eye_left_to_mouth_right'])
        if video_options[14]:
            result.append(sentence['eyebrows_distance'])
        if video_options[15]:
            result.append(sentence['right_eyebrow_middle_to_right_eye_top'])
        if video_options[16]:
            result.append(sentence['right_eyebrow_middle_to_right_eye_bottom'])
        if video_options[17]:
            result.append(sentence['left_eyebrow_middle_to_left_eye_top'])
        if video_options[18]:
            result.append(sentence['left_eyebrow_middle_to_left_eye_bottom'])

        results.append(result)

    return results


def get_video_features_filtered(annotation, database, video_options):

    results = get_video_features(annotation, database, video_options)

    filtereds = list()

    filtereds.append(np.average(np.array(results), axis=0).tolist())

    return [filtered for filtered in filtereds if type(filtered) == list]


def get_audio_features(annotation, database, audio_options):

    sentences = database.audio_features.find({'video_code': annotation['video_code'], 'start': int(annotation['start']), 'end': int(annotation['end'])}).sort('start', pymongo.ASCENDING)

    # answer to life the universe and everything plus 1
    sec_size = 42 + 1

    if audio_options is None:
        audio_options = np.full(audio_features_quantity, 1)

    results = []

    for sentence in sentences:

        time_last_index = pickle.loads(sentence['mfcc']).shape[-1] - 1
        time_size = int(time_last_index / sec_size)

        mfccs = np.hsplit(np.delete(pickle.loads(sentence['mfcc']), time_last_index, 1), time_size)
        mels = np.hsplit(np.delete(pickle.loads(sentence['mel_spectogram']), time_last_index, 1), time_size)
        sces = np.hsplit(np.delete(pickle.loads(sentence['spectral_centroid']), time_last_index, 1), time_size)
        scos = np.hsplit(np.delete(pickle.loads(sentence['spectral_contrast']), time_last_index, 1), time_size)
        sros = np.hsplit(np.delete(pickle.loads(sentence['spectral_rolloff']), time_last_index, 1), time_size)
        polys = np.hsplit(np.delete(pickle.loads(sentence['poly_features']), time_last_index, 1), time_size)
        tones = np.hsplit(np.delete(pickle.loads(sentence['tonnetz']), time_last_index, 1), time_size)
        zeros = np.hsplit(np.delete(pickle.loads(sentence['zero_crossing_rate']), time_last_index, 1), time_size)

        for i in range(0, time_size):
            mfcc = mfccs[i].flatten()
            mel = mels[i].flatten()
            sce = sces[i].flatten()
            sco = scos[i].flatten()
            sro = sros[i].flatten()
            poly = polys[i].flatten()
            tone = tones[i].flatten()
            zero = zeros[i].flatten()

            result = []

            if audio_options[0]:
                result = np.concatenate([result, mfcc], axis=0)
            if audio_options[1]:
                result = np.concatenate([result, mel], axis=0)
            if audio_options[2]:
                result = np.concatenate([result, sce], axis=0)
            if audio_options[3]:
                result = np.concatenate([result, sco], axis=0)
            if audio_options[4]:
                result = np.concatenate([result, sro], axis=0)
            if audio_options[5]:
                result = np.concatenate([result, poly], axis=0)
            if audio_options[6]:
                result = np.concatenate([result, tone], axis=0)
            if audio_options[7]:
                result = np.concatenate([result, zero], axis=0)

            results.append(result)

    return results


def get_text_features(annotation, database):

    sentences = database.text_features.find({'video_code': annotation['video_code'], 'start': int(annotation['start']), 'end': int(annotation['end'])}).sort('start', pymongo.ASCENDING)

    words = []
    ngrams = []

    for sentence in sentences:

        features = sentence['features']

        if features is None:
            continue

        for feature in features:

            if type(feature) == list:

                ngram = []

                for word in feature:

                    ngram.append(get_word_id(database, word))

                ngrams.append(ngram)

            else:

                words.append([get_word_id(database, feature)])

    return ngrams


def get_multimodal_features(annotation, database, filtered):

    videos = get_video_features(annotation, database, None) if not filtered \
        else get_video_features_filtered(annotation, database, None)

    audios = get_audio_features(annotation, database, None)
    texts = get_text_features(annotation, database)

    results = []

    for v in range(0, len(videos)):

        video = np.array(videos)[v, ]

        for a in range(0, len(audios)):

            audio = np.array(audios)[a, ]

            for t in range(0, len(texts)):

                text = np.array(texts)[t, ]
                result = np.concatenate([text, audio, video], axis=0)

                results.append(result)

    return results


def get_bimodal_va_features(annotation, database, filtered):

    videos = get_video_features(annotation, database, None) if not filtered \
        else get_video_features_filtered(annotation, database, None)

    audios = get_audio_features(annotation, database, None)

    results = []

    for v in range(0, len(videos)):

        video = np.array(videos)[v, ]

        for a in range(0, len(audios)):

            audio = np.array(audios)[a, ]

            result = np.concatenate([audio, video], axis=0)

            results.append(result)

    return results


def get_bimodal_vt_features(annotation, database, filtered):

    videos = get_video_features(annotation, database, None) if not filtered \
        else get_video_features_filtered(annotation, database, None)

    texts = get_text_features(annotation, database)

    results = []

    for v in range(0, len(videos)):

        video = np.array(videos)[v, ]

        for t in range(0, len(texts)):

            text = np.array(texts)[t, ]
            result = np.concatenate([text, video], axis=0)

            results.append(result)

    return results


def get_bimodal_at_features(annotation, database):

    audios = get_audio_features(annotation, database, None)
    texts = get_text_features(annotation, database)

    results = []

    for a in range(0, len(audios)):

        audio = np.array(audios)[a, ]

        for t in range(0, len(texts)):

            text = np.array(texts)[t, ]
            result = np.concatenate([text, audio], axis=0)

            results.append(result)

    return results


def get_word_id(database, word):

    try:

        return database.bag_of_words.find({'word': word})[0]['value']

    except IndexError:

        try:

            result = database.bag_of_words.find({}).sort('value', pymongo.DESCENDING)[0]['value']

        except IndexError:

            database.bag_of_words.insert({'word': word, 'value': 0})

            return 0

        value = result + 1

        database.bag_of_words.insert({'word': word, 'value': value})

    return value


def get_possibilities(n, disable_one):

    results = []
    zero_index = 0

    for i in range(0, n):

        result = np.full(n, 1 if disable_one else 0)

        result[zero_index] = 0 if disable_one else 1

        results.append(result)

        zero_index += 1

        if zero_index == n:

            return results

    return results
