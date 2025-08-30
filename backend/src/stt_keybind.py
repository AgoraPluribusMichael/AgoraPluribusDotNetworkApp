"""
From https://github.com/mpaepper/vibevoice/
Command-line interface for vibevoice
"""

import os
import subprocess

import requests
import sounddevice as sd
from dotenv import load_dotenv
from pynput.keyboard import Controller as KeyboardController, Key, Listener

def main():
    load_dotenv()
    key_label = os.environ.get("VOICEKEY", "ctrl_r")
    RECORD_KEYBIND = Key[key_label]

    recording = False
    sample_rate = 16000
    keyboard_controller = KeyboardController()

    def on_press(key):
        nonlocal recording
        if key == RECORD_KEYBIND and not recording:
            recording = True
            response = requests.get('http://127.0.0.1:8000/api/v1/plugins/stt/recording/start')
            response.raise_for_status()
            print("Recording...")

    def on_release(key):
        nonlocal recording
        if recording and key == RECORD_KEYBIND:
            recording = False
            print("Transcribing...")

            try:
                response = requests.get('http://127.0.0.1:8000/api/v1/plugins/stt/recording/stop')
                response.raise_for_status()
                transcript = response.json()['transcription']
                print(transcript)
                keyboard_controller.type(transcript)
            except requests.exceptions.RequestException as e:
                print(f"Error sending request to local API: {e}")
            except Exception as e:
                print(f"Error processing transcript: {e}")

    print("Listening for vibevoice keybind...")
    with Listener(on_press=on_press, on_release=on_release) as listener:
        with sd.InputStream(callback=None, channels=1, samplerate=sample_rate):
            listener.join()

if __name__ == "__main__":
    main()
