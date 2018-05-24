from opinion.extraction.video import generate_video_features, get_video_from_youtube
from opinion.extraction.audio import generate_audio_features
from opinion.extraction.text import generate_text_features, extract_entities
import opinion.transcription.caption as Caption
import opinion.helper.util as util

sentences_limit = 100


def extract(video_code):

    print("STARTING EXTRACTION FOR VIDEO: %s" % video_code)

    start_time = util.current_milli_time()

    get_video_from_youtube(video_code)

    sentences = Caption.get_captions(video_code, sentences_limit)

    extract_entities(sentences, video_code)
    # generate_text_features(sentences, video_code)
    # generate_audio_features(sentences, video_code)
    # generate_video_features(sentences, video_code)

    end_time = util.current_milli_time()

    print("FINISHED EXTRACTION FOR VIDEO: %s | EXECUTION TIME: %d ms" % (video_code, end_time - start_time))
