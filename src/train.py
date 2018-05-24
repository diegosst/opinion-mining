import opinion.analysis.svm as svm


video_features_quantity = 19
audio_features_quantity = 8

limit = 150

svm.generate_annotation_data()

video_one_disabled = svm.get_possibilities(video_features_quantity, True)
audio_one_disabled = svm.get_possibilities(audio_features_quantity, True)

video_one_active = svm.get_possibilities(video_features_quantity, False)
audio_one_active = svm.get_possibilities(audio_features_quantity, False)

annotations = svm.get_annotation_data(limit)

# X_video_filtered, y_video_filtered, video_filtered_preparation_time = svm.get_features_data(4, annotations, None, None)
# X_video, y_video, video_preparation_time = svm.get_features_data(0, annotations, None, None)
X_audio, y_audio, audio_preparation_time = svm.get_features_data(1, annotations, None, None)
# X_text, y_text, text_preparation_time = svm.get_features_data(2, annotations, None, None)
# X_multimodal, y_multimodal, multimodal_preparation_time = svm.get_features_data(3, annotations, None, None)

# print('Training filtered video model:')
# svm.training_model(X_video_filtered, y_video_filtered, 4, limit, video_filtered_preparation_time, None, None, False)
#
# print('Training video model:')
# svm.training_model(X_video, y_video, 0, limit, video_preparation_time, None, None, False)

print('Training audio model:')
svm.training_model(X_audio, y_audio, 1, limit, audio_preparation_time, None, None, False)

# print('Training text model:')
# svm.training_model(X_text, y_text, 2, limit, text_preparation_time, None, None, False)

# print('Training multimodal model:')
# svm.training_model(X_multimodal, y_multimodal, 3, limit, multimodal_preparation_time, None, None, False)
