#! /usr/bin/env python3
import os
import json
import argparse
import requests
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, Number, VoiceResponse
from datetime import datetime, timedelta, timezone
import re
from openai import OpenAI
import time
from event import createEvent
import tqdm
from transcription import downloadFile, getMetadata, transcriptionExists, encodeTranscriptionIntoAudio,readTranscriptionFromAudio
from halo import Halo
ai = OpenAI()


 
def setupTwilioClient():
    """Setup and return Twilio client using environment variables."""
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    return Client(account_sid, auth_token)

def uaCall(check=True, depth=0):
    phone1 = os.environ['TEST_PHONE_NUMBER']
    phone2 = os.environ['TEST_PHONE_NUMBER_2']
    sentry = os.environ['SENTRY_ID_NUMBER']
    try:
        if check:
            uaCheck(recordings)
        response = VoiceResponse()
        dial = Dial()
        if(phone1):
            dial.number(phone1)
        else:
            raise ValueError("Phone number not in environment variables")
        if phone2:
            dial.number(phone2)
        response.play(f'wwww1w{sentry}#wwwwwwww1wwwwwww{sentry}#wwwwww{sentry}wwwww1')
        response.record(timeout=0)
        response.append(dial)
    
        client = setupTwilioClient()

        call = client.calls.create(
            record=True,
            send_digits=f'wwww1w{sentry}#wwwwwwww1wwwwwww{sentry}#wwwwww{sentry}#wwwww1#',
            twiml=str(response),
            to=phone1,
            from_=os.environ['TWILIO_PHONE_NUMBER']
        )
        print(json.dumps(call.subresource_uris))
        print(str(response))
        recordings = client.recordings.list(call_sid=call.sid)
        print("waiting for 60 seconds")
        for i in tqdm.tqdm(range(55)):
            time.sleep(1)  # Sleep for 1 second per iteration
        uaCheck(None, depth+1)
        
    except Exception as e:
        print(e)

def match(regex, text):
    match = regex.search(text)
    if match:
        return match.group()
    return None
client = setupTwilioClient()
def uaCheck(recordings=None, depth=1):
    spinner = Halo(text="Loaing recordings list", spinner='dots')
    try:
        spinner.start()
        if recordings is None:
            recordings = client.recordings.list(date_created_after=datetime.now(timezone.utc).replace(hour=5, minute=0, second=0, microsecond=0))

        if not recordings:
            print("No recordings found")
            uaCall(False)
            return False

        matches = []
        transcriptions = []
        index = 0
        for recording in recordings:
            index += 1
            spinner.start(text=f'Processing recordings {index}/({len(recordings)})')
            recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
            filename = f"./calls/{recording.date_created.astimezone().strftime('%Y-%m-%d-%I-%M-%S')}_{recording.sid}.mp3"
            downloadFile(recording_url, filename)
            spinner.text = f'Checking for existing data {index}/({len(recordings)})'
            transcription = readTranscriptionFromAudio(filename)

            if transcription is None:
                spinner.text = f'encoding transcription {index}/({len(recordings)})'
                with open(filename, "rb") as audio_file:
                    transcription = ai.audio.transcriptions.create(model="whisper-1", file=audio_file).text
                    encodeTranscriptionIntoAudio(filename, transcription)
                
            spinner.start(text=f'Analyzing transcription {index}/({len(recordings)})')
            # print(f"{recording.date_created.astimezone().strftime('%I:%M%p %m/%d').lower()}: {transcription}")
            spinner.succeed()

            transcriptions.append(transcription)
            testToday = match(re.compile(r'you are required to test today', re.IGNORECASE), transcription)
            noTestToday = match(re.compile(r'do not test today', re.IGNORECASE), transcription)
            if testToday or noTestToday:
                matches.append(testToday if testToday else noTestToday)
        spinner.succeed()
        # print(json.dumps(matches))
        lowercase = [match.lower() for match in matches]
        spinner.start(text="Checking for calendar events")
        if "you are required to test today" in lowercase: 
            createEvent(True, None)
            spinner.succeed()
            return True
        elif "do not test today" in lowercase: return createEvent(False, None)
        else: 
            createEvent(False, '\n'.join(transcriptions))
            return uaCall(False, depth+1) if depth < 4 else False
    except Exception as e:
        print(e)

def main():
    parser = argparse.ArgumentParser(description='Command Line Interface for UA operations')
    subparsers = parser.add_subparsers(dest='command')

    callParser = subparsers.add_parser('call', help='Dial numbers and play extension tones')
    checkParser = subparsers.add_parser('check', help='Download recordings and check transcriptions. If a transcription matches the required pattern, create a calendar event, otherwise call and check again')

    args = parser.parse_args()

    if args.command == 'call':
        uaCall()
    elif args.command == 'check':
        uaCheck()

if __name__ == '__main__':
    main()
