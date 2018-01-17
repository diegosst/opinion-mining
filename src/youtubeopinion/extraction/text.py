import os
from textblob import TextBlob
from pathlib import Path


def get_sentence_polarity(text):

    blob = TextBlob(text)

    if blob.sentiment.polarity > 0:
        return 'positive'
    elif blob.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


def generate_polarity_for_sentences(sentences, video_code):

    print('## GENERATING TEXT POLARITY FILE ##')

    directory = '../../Data/Videos/' + str(video_code) + '/Polarities/'
    complement = '_sentences_polarity.txt'

    file = Path(directory + str(video_code) + complement)

    if not os.path.exists(directory):
        os.makedirs(directory)

    if file.is_file():
        print('## TEXT POLARITY FILE ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    file = open(directory + str(video_code) + complement, 'w')

    polarity_separator = str('|')
    duration_separator = str('-')

    for code, sentence in sentences.items():

        start = sentence['start']
        end = sentence['end']
        duration = sentence['duration']
        text = sentence['text']

        content = (start + duration_separator + end + polarity_separator + get_sentence_polarity(text) + '\n')

        file.write(content)

    file.close()

    print('## TEXT POLARITY FILE GENERATED WITH SUCCESS! ##')