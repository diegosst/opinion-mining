import urllib.request
import xmltodict
import html

def get_captions(code, language):

    wp = urllib.request.urlopen("http://video.google.com/timedtext?lang=" + str(language) + "&v=" + str(code))
    pw = wp.read()
    wp.close()

    return xmltodict.parse(pw)

def get_sentences(code, language):

    print('## GENERATING SENTENCES DATA ##')

    captions = get_captions(code, language)

    sentences = {}

    index = 0

    for transcript, text in captions.items():
        for part, list in text.items():
            for value in list:

                start = value['@start']
                duration = value['@dur']
                text = html.unescape(value['#text'])
                end = str(round(float(start) + float(duration), 2))

                sentence = {
                    'start' : start,
                    'end': end,
                    'duration' : duration,
                    'text' : text
                }

                sentences[index] = sentence

                index += 1

    print('## SENTENCES DATA GENERATED WITH SUCCESS! ##')

    return sentences