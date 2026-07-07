# realtime_audio.py - Hernan Le

# This module contains functions for recording audio and parsing "words" 
# in realtime.

# Let's assume that each word is separated by a brief gap of silence.
# Reasonable assumption, as Rocky likely knows to slow down his speech for the translator. 

# ----------------------------------------------------------------------

import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 44100 # recording processes 44100 input points per second (44100 Hz)
BLOCK_SIZE = 441 # stream sends data in blocks of 441, each block takes 0.01 seconds

# A word should be at least 5 blocks (0.05 seconds) long.
# This 1) prevents script from processing silence as words 
# and 2) gives recording enough time to collect input without being cut by silence.
MIN_WORD_BLOCK_LEN = 5  

# ----------------------------------------------------------------------

# Records audio until silence, returns the recording.
# If encountering silence while the audio is shorter than MIN_WORD_BLOCK_LEN,
# this function effectively restarts until the recorded word is long enough.
def record_word(silence_threshold=0.025):
    recorded_data = []
    
    # each block lasts 0.01 seconds
    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=1) as stream:
        while True:
            if stream.read_available >= BLOCK_SIZE:
                indata, _ = stream.read(BLOCK_SIZE)
                # append blocks to recorded_data
                recorded_data.append(indata)
                
                # RMS will act as our measurment of audio volume
                rms = np.sqrt( np.mean( indata**2 ) )
                
                # if root mean square (RMS) of a block is less than this, 
                # the block is considered silent, denoting the end of a word
                if rms < silence_threshold :
                    if len(recorded_data) >= MIN_WORD_BLOCK_LEN:
                        break # stop the input stream
                    else:
                        recorded_data.clear() # remove the contents of recorded_data to start again
            else:
                time.sleep(0.002) # give stream time to get more data
                # 2ms of sleep - loop checks on input data up to 5 times before block is filled
    
    recording = np.concatenate(recorded_data).flatten()    
    return recording

# ----------------------------------------------------------------------

def main():
    while True:
        recording = record_word()
        print(len(recording) // BLOCK_SIZE )

if __name__ == "__main__":
    main()