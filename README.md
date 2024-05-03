# Twilio Automated Calling and Transcription System

## Description
This project utilizes Twilio's APIs to automate the process of making phone calls, recording them, and transcribing the recordings.
The system checks transcriptions for specific keywords and manages calendar events based on the transcription content. It also integrates with OpenAI's Whisper model for improved transcription accuracy.
The transcriptions get transcoded into the mp3 files with ffmpeg, your calls are only transcribed once to save on API costs.


## Requirements
- Python 3.8+
- Twilio account and API credentials
- OpenAI API credentials
- tqdm
- halo
- requests

## Installation
1. Clone the repository:
2. Create a venv
    ```
    python3 -m venv venv
    ```
3. Activate the venv
    ```
    source venv/bin/activate
    ```
4. Install the required packages
    ```
    pip install -r requirements.txt
    ```
5. Copy the example env
    ```
    cp .env.example .env
    ```
6. Add a google cloud credentials.json file to the root directory for calendar integration

7. Optionally update your crontab once the script is working as expected
    ```
    crontab -e
    ```
    ```
    12 2-11 * * 1-5 /usr/bin/bash -c "cd /home/alice/code/ua-twilio/ && source ./ua check"
    ```
    this runs the script every hour from 2am to 11am on weekdays
## Usage
Run the bash wrapper which temporarily activates the venv and runs the script.
    ```
    ./ua check
    ```
