import urllib.request
import xmltodict
import html

def get_captions(code, language):

    wp = urllib.request.urlopen("http://video.google.com/timedtext?lang=" + str(language) + "&v=" + str(code))
    pw = wp.read()
    wp.close()

    return xmltodict.parse(pw)

def get_sentences(code, language):

    captions = get_captions(code, language)

    sentences = {}

    index = 0

    for transcript, text in captions.items():
        for part, list in text.items():
            for value in list:
                print('#####################')

                start = value['@start']
                duration = value['@dur']
                text = html.unescape(value['#text'])

                sentence = {
                    "start": start,
                    "duration": duration,
                    "text": text
                }

                sentences[index] = sentence

                index += 1

                print('Start: ' + start)
                print('Duration: ' + duration)
                print('Text: ' + text)


    return sentences