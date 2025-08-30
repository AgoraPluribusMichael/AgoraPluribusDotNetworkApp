#!/usr/bin/env python3

import time
from speech_to_text import SpeechToText

def test_speech_to_text():
    print("Testing refactored SpeechToText class...")
    
    # Create instance
    stt = SpeechToText()
    print("✓ Instance created successfully")
    
    # Test multiple recordings
    for i in range(2):
        print(f"\n--- Recording {i+1} ---")
        print("Starting recording... (speak for 3 seconds)")
        
        stt.start_recording()
        time.sleep(3)  # Record for 3 seconds
        
        transcription = stt.stop_recording()
        print(f"Transcription: '{transcription}'")
        
        # Test immediate restart
        print("Testing immediate restart...")
        stt.start_recording()
        time.sleep(1)
        transcription = stt.stop_recording()
        print(f"Quick transcription: '{transcription}'")
    
    print("\n✓ All tests completed successfully!")

if __name__ == "__main__":
    test_speech_to_text()