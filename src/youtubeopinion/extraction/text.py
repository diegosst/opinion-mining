import os
import nltk
import string
from textblob import TextBlob
from pathlib import Path
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')


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

    directory = '../../Data/Videos/' + str(video_code) + '/Extractions/'
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

    lemmatizer = WordNetLemmatizer()

    for code, sentence in sentences.items():

        start = sentence['start']
        end = sentence['end']
        duration = sentence['duration']
        text = sentence['text']

        table = str.maketrans('', '', string.punctuation)
        stop_words = set(stopwords.words('english'))

        words = word_tokenize(text)
        words = [w.translate(table) for w in words]
        words = [w for w in words if not w in stop_words]
        words = [word for word in words if word.isalpha()]
        words = [nltk.stem.porter.PorterStemmer().stem(word) for word in words]
        words = [lemmatizer.lemmatize(word) for word in words]

        tags = nltk.pos_tag(words)

        content = (start + duration_separator + end + polarity_separator + str([word for word in [tag for tag in tags]]) + '\n')

        file.write(content)

    file.close()

    print('## TEXT POLARITY FILE GENERATED WITH SUCCESS! ##')


