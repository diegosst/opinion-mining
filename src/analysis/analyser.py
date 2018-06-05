import _pickle as pickle

import pymongo
from pymongo import MongoClient

import opinion.extraction.extractor as extractor
import opinion.helper.util as util
import opinion.transcription.caption as caption
from opinion.analysis.svm import get_multimodal_features

# Model code represents the type of analysis.
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

model_code = 7


def analyse(video_code):

    print('Starting video analysis for code: %s' % video_code)

    start_time = util.current_milli_time()

    extractor.extract(video_code)

    client = MongoClient('localhost', 27017)

    database = client.opinion_database

    try:

        model = pickle.loads(list(database.models.find({'code': model_code, 'model': {"$exists": True, "$ne": ""}}).sort('test_precision', pymongo.DESCENDING))[0]['model'])

    except IndexError:

        print('No model found for code %d.' % model_code)

        return

    sentences = database.sentences.find({'video_code': video_code}).sort('start', pymongo.ASCENDING)

    results = []
    indexes = []

    for i in range(0, sentences.count()):

        for result in get_multimodal_features(video_code, sentences[i], database, True):

            results.append(result)
            indexes.append(i)

    predictions = model.predict(results)

    sentences_predict = dict()

    for i in range(0, len(predictions)):

        try:

            sentences_predict[indexes[i]]

        except KeyError:

            sentences_predict[indexes[i]] = []

        sentences_predict[indexes[i]].append(predictions[i])

    sentiments = []

    for i in range(0, len(sentences_predict)):

        sum = 0

        try:

            for sentiment in sentences_predict[i]:

                sum += sentiment

            print('Sentence: %50s | Sentiment: %5.2f' % (sentences[i]['text'], sum/len(sentences_predict[i])))

            var = dict()
            var['sentence'] = sentences[i]['text']
            var['start'] = sentences[i]['timestampStart']
            var['end'] = sentences[i]['timestampEnd']
            var['sentiment'] = sum/len(sentences_predict[i])

            sentiments.append(var)

        except KeyError:

            continue

    end_time = util.current_milli_time()

    print('Finished analysing video for code: %s | Execution time: %d ms' % (video_code, end_time - start_time))

    caption.generate_excel(sentences, video_code, sentiments, 2)

    return sentiments
