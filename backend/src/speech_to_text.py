# pip install faster-whisper sounddevice numpy
import queue
import threading
import time
from contextlib import contextmanager

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SR = 16000
CH = 1
DTYPE = "float32"

class SpeechToText:
    def __init__(self):
        self.model = WhisperModel("base", device="auto", compute_type="int8")
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.transcription = None
        self._stream = None
        self._recording_thread = None
        self._stop_event = threading.Event()
        
    def start_recording(self):
        if self.is_recording:
            return
            
        self.is_recording = True
        self.transcription = None
        self._stop_event.clear()
        
        # Clear any old audio data
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        self._recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self._recording_thread.start()
        
    def stop_recording(self):
        if not self.is_recording:
            return self.transcription
            
        self.is_recording = False
        self._stop_event.set()
        
        if self._recording_thread:
            self._recording_thread.join(timeout=5)
            
        # Process collected audio
        self._process_audio()
        return self.transcription
        
    def _record_audio(self):
        def callback(indata, frames, time_info, status):
            if status:
                print(f"Audio input status: {status}")
            if not self._stop_event.is_set():
                try:
                    self.audio_queue.put_nowait(indata.copy())
                except queue.Full:
                    pass
                    
        try:
            with sd.InputStream(
                samplerate=SR, 
                channels=CH, 
                dtype=DTYPE, 
                callback=callback
            ):
                while not self._stop_event.is_set():
                    time.sleep(0.1)
        except Exception as e:
            print(f"Recording error: {e}")
            
    def _process_audio(self):
        if self.audio_queue.empty():
            self.transcription = ""
            return
            
        audio_data = []
        while not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get_nowait()
                audio_data.append(chunk)
            except queue.Empty:
                break
                
        if not audio_data:
            self.transcription = ""
            return
            
        # Combine all audio chunks
        combined_audio = np.concatenate(audio_data, axis=0).flatten()
        
        # Transcribe
        try:
            segments, _ = self.model.transcribe(combined_audio, language="en")
            self.transcription = "".join(s.text for s in segments).strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            self.transcription = ""
