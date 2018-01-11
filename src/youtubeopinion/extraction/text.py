from textblob import TextBlob

def get_sentence_polarity(text):

    blob = TextBlob(text)

    if blob.sentiment.polarity > 0:
        return 'positive'
    elif blob.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'