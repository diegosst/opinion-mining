import youtubeopinion.extraction.audio as AudioExtraction
import youtubeopinion.extraction.text as TextExtraction
import youtubeopinion.extraction.video as VideoExtraction
import youtubeopinion.transcription.caption as Caption

video_code = "ELSPFbh67zw"
language = "en"

sentences = Caption.get_sentences(video_code, language)

VideoExtraction.get_video_from_youtube(video_code)
TextExtraction.generate_text_features(sentences, video_code)
AudioExtraction.generate_audio_features(sentences, video_code)
VideoExtraction.generate_video_features(sentences, video_code)
