import os
import json
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, Number, VoiceResponse
from event import event
def download_file(url, filename):
    """Download a file from a URL and save it to a local file."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        print(f"File downloaded successfully: {filename}")
    else:
        print(f"Failed to download the file: {url}. Status code: {response.status_code}")
try:
    response = VoiceResponse()
    dial = Dial()
    dial.number('303-552-0646')
    dial.number('303-552-0624')
    response.play("wwww1w95698599#wwwwwwww1wwwwwww95698599#wwwwwwww1")
    response.record(timeout=10, transcribe=True)
    response.append(dial)

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    call = client.calls.create(
                            record=True,
                            send_digits='wwww1w95698599#wwwwwwww1wwwwwww95698599#wwwwwwww1',
                            twiml=response,
                            to='303-552-0646',
                            from_='+17853844775'
                        )
    print(json.dumps(call.subresource_uris))

    # Fetch call recordings
    recordings = client.recordings.list(call_sid=call.sid)
    for recording in recordings:
        recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
        download_file(recording_url, f"{recording.sid}.mp3")
        print(f"Downloaded recording: {recording.sid}.mp3")

    # Fetch transcriptions
    transcriptions = client.transcriptions.list()
    for transcription in transcriptions:
        print(f"Transcription SID: {transcription.sid}, Text: {transcription.transcription_text}")
        
    print(response)

except Exception as e:
    print(e)