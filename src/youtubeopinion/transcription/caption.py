import os
import pandas
import time
import pafy
import selenium
import pymongo
from selenium import webdriver
from random import randrange
from pathlib import Path
import youtubeopinion.database.db as db


def get_captions(code, sentences_limit):
    database = db.get_db()

    if database.sentences.find_one({'video_code': code}) is not None:
        print('## SENTENCES ALREADY EXTRACTED, SKIPPING THIS STEP. ##')
        result = database.sentences.find({'video_code': code}).sort('start', pymongo.ASCENDING)
        generate_excel(result, code)
        return result

    driver = webdriver.Chrome()

    driver.get('https://www.youtube.com/watch?v=' + code)
    time.sleep(10)

    database.sentences.remove({'video_code': code})

    try:

        driver.execute_script("document.getElementsByClassName('videoAdUiSkipButton')[0].click()")
        time.sleep(2)

    except selenium.common.exceptions.WebDriverException:

        print('Skipping video advertising skip.')

    driver.execute_script("document.getElementsByClassName('ytp-play-button')[0].click()")
    time.sleep(1)

    driver.execute_script("document.getElementsByClassName('dropdown-trigger')[0].click()")
    time.sleep(1)

    driver.execute_script("document.querySelector('ytd-menu-service-item-renderer[tabindex=\"-1\"]').click()")
    time.sleep(1)

    result = driver.execute_script("var list = document.getElementsByClassName('cue-group');"
                                   "var sentences = [];"
                                   "for (var i = 0; i < list.length; i++){"
                                   "var start = list[i].getElementsByClassName('cue-group-start-offset')[0].innerHTML;"
                                   "var message = list[i].getElementsByClassName('cues')[0]"
                                   ".getElementsByClassName('cue')[0].innerHTML;"
                                   "sentence = {'message': message,'start': start};"
                                   "sentences.push(sentence)"
                                   "};"
                                   "return sentences")

    driver.close()

    sentences = get_random_sentences(captions_format(result, code), sentences_limit)

    database.sentences.insert(sentences)

    generate_excel(sentences, code)

    return sentences


def captions_format(result, code):
    sentences = []

    url = "http://www.youtube.com/watch?v=" + code
    video = pafy.new(url)

    duration = video.length * 1000

    formatted_duration = video.duration.split(':')[1] + ':' + video.duration.split(':')[2]

    last_index = -1

    for item in result:

        message = item['message'].replace('\n', '').replace('              ', '').replace('            ', '')
        start = item['start'].replace('\n', '').replace('          ', '').replace('        ', '')

        minutes = int(start.split(':')[0]) * 60000
        seconds = int(start.split(':')[1]) * 1000

        milliseconds = minutes + seconds

        sentence = {'video_code': code,
                    'text': message,
                    'start': milliseconds,
                    'timestampStart': start}

        if last_index == len(result):

            sentence.update({'end': duration})
            sentence.update({'timestampEnd': formatted_duration})
            sentence.update({'duration': int(duration) - int(start)})

        elif last_index > -1:

            sentences[last_index].update({'end': milliseconds})
            sentences[last_index].update({'timestampEnd': start})

            last_end = int(sentences[last_index]['end'])
            last_start = int(sentences[last_index]['start'])

            sentences[last_index].update({'duration': last_end - last_start})

        sentences.append(sentence)

        last_index += 1

    return sentences


def get_random_sentences(sentences, sentences_limit):
    size = len(sentences)

    start = randrange(0, size)

    if (start + sentences_limit) < size:

        end = (start + sentences_limit)

    elif (start - 100) > 0:

        end = (start - 100)

    else:

        return sentences

    result = []

    for x in range(start, end):
        result.append(sentences[x])

    return result


def generate_excel(sentences, video_code):
    videos_directory = '../data/videos/' + str(video_code)
    current_directory = os.getcwd()
    separator = '/'
    annotation_file = '-sentiment-annotation.xlsx'

    file = Path(videos_directory + separator + str(video_code) + annotation_file)

    if not os.path.exists(videos_directory):
        os.makedirs(videos_directory)

    if file.is_file():
        print('## ANNOTATION FILE ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    os.chdir(videos_directory)

    starts = []
    ends = []
    texts = []
    sentiments = []

    for sentence in sentences:
        starts.append(sentence['timestampStart'])
        ends.append(sentence['timestampEnd'])
        texts.append(sentence['text'])
        sentiments.append('')

    df = pandas.DataFrame({'Sentence': texts,
                           'Start': starts,
                           'End': ends,
                           'Sentiment': sentiments})

    df.to_csv(video_code + '-sentiment-annotation.xlsx', sep='\t', header=True, columns=['Sentence', 'Start',
                                                                                         'End', 'Sentiment'])
    os.chdir(current_directory)
