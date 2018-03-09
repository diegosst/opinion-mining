import os
import nltk
import string
import itertools
import youtubeopinion.database.db as db
from pathlib import Path
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')


def generate_text_features(sentences, video_code):
    database = db.get_db()

    if database.text_features.find_one({'video_code': video_code}) is not None:
        print('## TEXT FEATURES ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    print('## GENERATING TEXT FEATURES FILE ##')

    lemmatizer = WordNetLemmatizer()

    database.text_features.remove({'video_code': video_code})

    for code, sentence in sentences.items():
        start = sentence['start']
        end = sentence['end']
        text = sentence['text']

        table = str.maketrans('', '', string.punctuation)
        stop_words = set(stopwords.words('english'))

        words = word_tokenize(text)
        words = [w.translate(table) for w in words]
        words = [w for w in words if not w in stop_words]
        words = [word for word in words if word.isalpha()]
        words = [nltk.stem.porter.PorterStemmer().stem(word) for word in words]
        words = [lemmatizer.lemmatize(word) for word in words]

        bigrams = bigram_word_feats(words)

        text_feature = {
            'video_code': video_code,
            'start': start,
            'end': end,
            'features': bigrams
        }

        database.text_features.insert(text_feature)

    print('## TEXT FEATURES GENERATED WITH SUCCESS! ##')


def bigram_word_feats(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)

    return [ngram for ngram in itertools.chain(words, bigrams)]
