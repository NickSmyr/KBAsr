import sys

from utils.main import transcribe_directory_of_wav_files

try:
    path = sys.argv[1]
    output_file = sys.argv[2]
    transcribe_directory_of_wav_files(path, output_file, cuda=True)
except:
    print(
        "Transcribe directory containing audio files, files must be in the format file_xxx.wav \n"
        "First parameter must be the diretory of the audio files and second the output filename"
    )
