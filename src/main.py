import youtubeopinion.extraction.audio as AudioExtraction
import youtubeopinion.extraction.text as TextExtraction
import youtubeopinion.extraction.video as VideoExtraction
import youtubeopinion.transcription.caption as Caption

def main():

    video_code = "ELSPFbh67zw"
    language = "en"

    sentences = Caption.get_sentences(video_code, language)

    TextExtraction.generate_polarity_for_sentences(sentences, video_code)
    VideoExtraction.get_video_from_youtube(video_code)
    AudioExtraction.generate_audio_features(sentences, video_code)


main()