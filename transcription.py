import subprocess
import os
import json
from openai import OpenAI
import requests




def downloadFile(url, filename):
    if os.path.exists(filename): return
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully: {filename}")
    else:
        print(f"Failed to download the file: {url}. Status code: {response.status_code}")
def getMetadata(filename):
    result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', filename], capture_output=True, text=True)
    return json.loads(result.stdout)

def encodeTranscriptionIntoAudio(filename, transcription):
    metadata_option = f"metadata=s:description='{transcription}'"
    output_filename = filename.replace('.mp3', '_transcribed.mp3')
    subprocess.run(['ffmpeg', '-i', filename, '-c', 'copy', '-map', '0', '-metadata', metadata_option, output_filename], check=True, capture_output=True)
    os.replace(output_filename, filename)

def transcriptionExists(metadata):
    try:
        return 'description' in metadata['format']['tags'] and metadata['format']['tags']['description']
    except KeyError:
        return False
def readTranscriptionFromAudio(filename):
    metadata = getMetadata(filename)
    try:
        return metadata['format']['tags']['description']
    except KeyError:
        return None  # No description found
    
#ai = OpenAI()
#for recording in recordings:
#    recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
#    filename = f"./calls/{recording.date_created.strftime('%Y-%m-%d')}_{recording.sid}.mp3"
##    downloadFile(recording_url, filename)

#    metadata = getMetadata(filename)
   # if not transcriptionExists(metadata):
   #     with open(filename, "rb") as audio_file:
   #         transcription = ai.audio.transcriptions.create(
   #             model="whisper-1", 
   #             file=audio_file
   #         )
   #     encodeTranscriptionIntoAudio(filename, transcription['text'])