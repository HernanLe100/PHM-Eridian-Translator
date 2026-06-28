import sounddevice as sd
import numpy as np
from scipy.signal import stft, istft

SAMPLE_RATE = 44100
FRAME_LEN = 2048 # number of points being analyzed at a time frame for FFT
MAX_BUFFER_LEN = 2*SAMPLE_RATE

SILENCE_THRESHOLD = 0.025
MIN_BLOCK_LEN = 5

def record_word():
    recorded_data = []
    streaming = [True]
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        recorded_data.append(indata.copy())
        rms = np.sqrt( np.mean( recorded_data[-1]**2 ) )
        
        #print(len(recorded_data))
        #print(rms)
        if rms < SILENCE_THRESHOLD :
            if len(recorded_data) >= MIN_BLOCK_LEN:
                streaming[0] = False
            else:
                recorded_data.clear()
            
        return
    
        if len(recorded_data) >= MIN_BLOCK_LEN and rms < 0.02 :
            streaming[0] = False
        
            
    # each block lasts 0.01 seconds
    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=SAMPLE_RATE//100, callback=callback, channels=1):
        while streaming[0]:
            pass
    
    recording = np.array(recorded_data).flatten()    
    return recording


def record_interval(seconds = 0.5):
    recording = sd.rec(int(SAMPLE_RATE * seconds), samplerate=SAMPLE_RATE, channels=1).flatten()
    sd.wait()
    return recording

def get_spectrogram(recording : np.array):
    _, _, Z = stft(recording, fs=SAMPLE_RATE, nperseg=FRAME_LEN, noverlap=FRAME_LEN*3//4)
    return np.abs(Z)


def main():
    while True:
        recording = record_word()
        if len(recording) >= MIN_BLOCK_LEN * SAMPLE_RATE//100:
            #print(len(recording))
            print(len(recording) * 100 // SAMPLE_RATE )

if __name__ == "__main__":
    main()