import itertools
import string

import nltk
from nltk import word_tokenize
from nltk.collocations import BigramCollocationFinder
from nltk.corpus import stopwords
from nltk.metrics import BigramAssocMeasures
from nltk.stem.wordnet import WordNetLemmatizer

import opinion.database.db as db

nltk.download('maxent_ne_chunker')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('words')


def generate_text_features(sentences, video_code):
    database = db.get_db()

    if database.text_features.find_one({'video_code': video_code}) is not None:
        print('## TEXT FEATURES ALREADY GENERATED, SKIPPING THIS STEP. ##')
        return

    print('## GENERATING TEXT FEATURES FILE ##')

    lemmatizer = WordNetLemmatizer()

    database.text_features.remove({'video_code': video_code})

    for sentence in sentences:
        start = sentence['start']
        end = sentence['end']
        text = sentence['text']

        table = str.maketrans('', '', string.punctuation)
        stop_words = set(stopwords.words('portuguese'))

        words = word_tokenize(text, language='portuguese')
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

    try:
        bigrams = bigram_finder.nbest(score_fn, n)
        return [ngram for ngram in itertools.chain(words, bigrams)]
    except ZeroDivisionError:
        print('Could not find bigram for words: ', *words)
        return None


def extract_entities(sentences, video_code):

    database = db.get_db()

    if database.text_entities.find_one({'video_code': video_code}) is not None:
        print('## ENTITIES FROM SENTENCES ALREADY EXTRACTED, SKIPPING THIS STEP. ##')
        return

    print('## EXTRACTING ENTITIES FROM SENTENCES ##')

    sentences = [sentence['text'] for sentence in sentences]

    tokenized_sentences = [nltk.word_tokenize(sentence, language='portuguese') for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence, lang='por') for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    entity_names = []
    for tree in chunked_sentences:

        entity_names.extend(extract_entity_names(tree))

    print
    set(entity_names)


def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names
