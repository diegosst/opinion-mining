import os
from pathlib import Path
from pydub import AudioSegment


def get_audio_from_video(video_code):

    video_directory = '../../Data/Videos/' + str(video_code)
    current_directory = os.getcwd()
    file_name = ''
    video_extension = '.mp4'
    audio_extesion = '.mp3'
    separator = '/'

    file = Path(video_directory + separator + str(video_code) + audio_extesion)

    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    if file.is_file():
        return

    os.chdir(video_directory)

    # TODO: In progress - Diego
    # mp3_file = AudioSegment.from_file(video_code + video_extension, 'mp3')

    # mp3_file.export(video_code + audio_extesion, format="mp3")

    os.chdir(current_directory)


# EXAMPLE OF AUDIO FRAGMENTATION
# files_path = 'a'
# file_name = 'a'
#
# startMin = 9
# startSec = 50
#
# endMin = 13
# endSec = 30
#
# # Time to miliseconds
# startTime = startMin*60*1000+startSec*1000
# endTime = endMin*60*1000+endSec*1000
#
# # Opening file and extracting segment
# song = AudioSegment.from_mp3( files_path+file_name+'.mp3' )
# extract = song[startTime:endTime]
#
# # Saving
# extract.export( file_name+'-extract.mp3', format="mp3")