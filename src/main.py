import pytube
import youtubeopinion.extraction.text as TextExtraction
import youtubeopinion.transcription.caption as Caption

def main():

    # Downloading video direct from youtube.
    # pytube.YouTube('http://youtube.com/watch?v=ELSPFbh67zw').streams.first().download()

    video_code = "ELSPFbh67zw"
    language = "en"

    sentences = Caption.get_sentences(video_code, language)


main()