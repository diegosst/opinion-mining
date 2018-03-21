import os
import youtubeopinion.extraction.audio as AudioExtraction
import youtubeopinion.extraction.text as TextExtraction
import youtubeopinion.extraction.video as VideoExtraction
import youtubeopinion.transcription.caption as Caption

videos = ["PX23ue3vxEA",
          "GkVwG53bG8I",
          "wswb3xhHQmg"]

project_path = '/home/diegosantos/Projeto/Opinion Mining/src'
sentences_limit = 100

for video_code in videos:
    VideoExtraction.get_video_from_youtube(video_code)

    sentences = Caption.get_captions(video_code, sentences_limit)

    TextExtraction.generate_text_features(sentences, video_code)
    AudioExtraction.generate_audio_features(sentences, video_code)
    VideoExtraction.generate_video_features(sentences, video_code)
