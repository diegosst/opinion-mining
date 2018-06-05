import opinion.analysis.svm as svm


def train(limit, save):

    # Used for training specific and evaluating specific features combinations:
    #
    # video_features_quantity = 19
    # audio_features_quantity = 8
    # svm.generate_annotation_data()
    # video_one_disabled = svm.get_possibilities(video_features_quantity, True)
    # audio_one_disabled = svm.get_possibilities(audio_features_quantity, True)
    # video_one_active = svm.get_possibilities(video_features_quantity, False)
    # audio_one_active = svm.get_possibilities(audio_features_quantity, False)

    splits = 5
    annotations = svm.get_test_and_train_annotations(limit, splits)

    print('STEP 1/7 (LIMIT %d)' % limit)
    train_video_average(annotations, limit, 1)
    print('STEP 2/7 (LIMIT %d)' % limit)
    train_audio(annotations, limit, 2)
    print('STEP 3/7 (LIMIT %d)' % limit)
    train_text(annotations, limit, 3)
    print('STEP 4/7 (LIMIT %d)' % limit)
    train_bimodal_va_average(annotations, limit, 4)
    print('STEP 5/7 (LIMIT %d)' % limit)
    train_bimodal_vt_average(annotations, limit, 5)
    print('STEP 6/7 (LIMIT %d)' % limit)
    train_bimodal_at(annotations, limit, 6)
    print('STEP 7/7 (LIMIT %d)' % limit)
    train_multimodal_average(annotations, limit, 7, save)


def train_multimodal_average(annotations, limit, code, save):
    multimodal_filtered_datas, multimodal_filtered_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training multimodal + video filtered model:')
    svm.training_model(multimodal_filtered_datas, code, limit, multimodal_filtered_preparation_time, None, None, save)


def train_multimodal(annotations, limit, code, save):
    multimodal_datas, multimodal_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training multimodal model:')
    svm.training_model(multimodal_datas, code, limit, multimodal_preparation_time, None, None, save)


def train_bimodal_at(annotations, limit, code):
    bimodal_at_datas, bimodal_at_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training bimodal audio + text model:')
    svm.training_model(bimodal_at_datas, code, limit, bimodal_at_preparation_time, None, None, False)


def train_bimodal_vt_average(annotations, limit, code):
    bimodal_vt_filtered_datas, bimodal_vt_filtered_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training bimodal video filtered + text model:')
    svm.training_model(bimodal_vt_filtered_datas, code, limit, bimodal_vt_filtered_preparation_time, None, None, False)


def train_bimodal_vt(annotations, limit, code):
    bimodal_vt_datas, bimodal_vt_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training bimodal video + text model:')
    svm.training_model(bimodal_vt_datas, code, limit, bimodal_vt_preparation_time, None, None, False)


def train_bimodal_va_average(annotations, limit, code):
    bimodal_va_filtered_datas, bimodal_va_filtered_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training bimodal video filtered + text model:')
    svm.training_model(bimodal_va_filtered_datas, code, limit, bimodal_va_filtered_preparation_time, None, None, False)


def train_bimodal_va(annotations, limit, code):
    bimodal_va_datas, bimodal_va_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training bimodal video + audio model:')
    svm.training_model(bimodal_va_datas, code, limit, bimodal_va_preparation_time, None, None, False)


def train_text(annotations, limit, code):
    text_datas, text_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training text model:')
    svm.training_model(text_datas, code, limit, text_preparation_time, None, None, False)


def train_audio(annotations, limit, code):
    audio_datas, audio_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training audio model:')
    svm.training_model(audio_datas, code, limit, audio_preparation_time, None, None, False)


def train_video_average(annotations, limit, code):
    video_filtered_datas, video_filtered_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training filtered video model:')
    svm.training_model(video_filtered_datas, code, limit, video_filtered_preparation_time, None, None, False)


def train_video(annotations, limit, code):
    video_datas, video_preparation_time = svm.get_train_and_test_data(code, annotations, None, None)
    print('Training video model:')
    svm.training_model(video_datas, code, limit, video_preparation_time, None, None, False)


train(15, False)
train(30, False)
train(50, False)
train(75, False)
train(100, False)
train(150, False)
