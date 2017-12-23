import urllib.request
import xmltodict
import pytube

# pytube.YouTube('http://youtube.com/watch?v=ELSPFbh67zw').streams.first().download()

wp = urllib.request.urlopen("http://video.google.com/timedtext?lang=en&v=ELSPFbh67zw")
pw = wp.read()
wp.close()

pw = xmltodict.parse(pw)

for transcript, text in pw.items():
    for part, list in text.items():
        for value in list:
            print('#####################')
            print('Start: ' + value['@start'])
            print('Duration: ' + value['@dur'])
            print('Text: ' + value['#text'].encode("utf-8"))