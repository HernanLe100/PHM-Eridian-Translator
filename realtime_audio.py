# realtime_audio.py - Hernan Le

# This module contains functions for recording audio and parsing "words" 
# in realtime.

# Let's assume that each word is separated by a brief gap of silence.
# Reasonable assumption, as Rocky likely knows to slow down his speech for the translator. 

# ----------------------------------------------------------------------

import sounddevice as sd
import numpy as np

SAMPLE_RATE = 44100 # recording processes 44100 input points per second (44100 Hz)
BLOCK_SIZE = 441 # stream sends data in blocks of 441, each block takes 0.01 seconds

# if root mean square (RMS) of a block is less than this, 
# the block is considered silent, denoting the end of a word
SILENCE_THRESHOLD = 0.025

# A word should be at least 5 blocks (0.05 seconds) long.
# This 1) prevents script from processing silence as words 
# and 2) gives recording enough time to collect input without being cut by silence.
MIN_WORD_BLOCK_LEN = 5  

# ----------------------------------------------------------------------

# Records audio until silence, returns the recording.
# If encountering silence while the audio is shorter than MIN_WORD_BLOCK_LEN,
# this function effectively restarts until the recorded word is long enough.
def record_word():
    recorded_data = []
    streaming = [True] # setting boolean inside an array so that callback function can access
    
    # appends blocks to recorded_data
    def callback(indata, frames, time, status):
        if status:
            print(status)
        
        recorded_data.append(indata.copy())
        
        # RMS will act as our measurment of audio volume
        rms = np.sqrt( np.mean( recorded_data[-1]**2 ) )
        
        #print(len(recorded_data))
        #print(rms)
        
        if rms < SILENCE_THRESHOLD :
            if len(recorded_data) >= MIN_WORD_BLOCK_LEN:
                streaming[0] = False # stops the input stream
            else:
                recorded_data.clear() # remove the contents of recorded_data to start again
    
    # each block lasts 0.01 seconds
    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, callback=callback, channels=1):
        while streaming[0]:
            pass
    
    recording = np.array(recorded_data).flatten()    
    return recording

# ----------------------------------------------------------------------

def main():
    while True:
        recording = record_word()
        print(len(recording) // BLOCK_SIZE )

if __name__ == "__main__":
    main()