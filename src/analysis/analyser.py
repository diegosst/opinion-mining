import _pickle as pickle
import pymongo
import numpy as np
from pymongo import MongoClient
from opinion.analysis.svm import get_multimodal_features
import opinion.extraction.extractor as extractor
import opinion.helper.util as util

# Model codes:
# 0 - Video
# 1 - Audio
# 2 - Text
# 3 - Multimodal

model_code = 3


def analyse(video_code):

    print('Starting video analysis for code: %s' % video_code)

    start_time = util.current_milli_time()

    extractor.extract(video_code)

    client = MongoClient('localhost', 27017)

    database = client.opinion_database

    model = pickle.loads(list(database.models.find({'code': model_code}).sort('version', pymongo.DESCENDING))[0]['model'])

    sentences = database.sentences.find({'video_code': video_code}).sort('start', pymongo.ASCENDING)

    results = []
    indexes = []

    sentiment = dict()

    for i in range(0, sentences.count()):

        for result in get_multimodal_features(video_code, sentences[i], database):

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

            sentiments.append(sum/len(sentences_predict[i]))

        except KeyError:

            continue

    sentiments_sum = 0

    for sentiment in sentiments:

        sentiments_sum += sentiment

    result = (int(sentiments_sum)/len(sentiments))

    print('Sentences sentiment mean: %0.2f' % result)

    if result < -0.15:

        print('Polarity is negative.')

    elif result > 0.15:

        print('Polarity is positive.')

    else:

        print('Polarity is neutral.')

    end_time = util.current_milli_time()

    print('Finished analysing video for code: %s | Execution time: %d ms' % (video_code, end_time - start_time))
