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

    directory = '../../Data/Polarities/'
    complement = '_sentences_polarity.txt'

    file = Path(directory + str(video_code) + complement)

    if not os.path.exists(directory):
        os.makedirs(directory)

    if file.is_file():
        return

    file = open(directory + str(video_code) + complement, 'w')

    for code, sentence in sentences.items():

        start = sentence['start']
        duration = sentence['duration']
        text = sentence['text']

        file.write(start + '-' + str(round(float(start) + float(duration), 2)) + ':' + get_sentence_polarity(text) + '\n')

    file.close()