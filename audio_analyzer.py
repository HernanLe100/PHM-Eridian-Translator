import sounddevice as sd
import numpy as np
from scipy.signal import stft

SAMPLE_RATE = 44100 
FRAME_LEN = 2048



# ----------------------------------------------------------------------

# Takes audio input until user presses Enter
# Returns the array of recorded_data - list of arrays of length FRAME_LEN
def record() -> list:
    recorded_data = []
    def callback(indata, frames, time, status):
        if status:
            print(status)
        recorded_data.append(indata.copy())
        
    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=FRAME_LEN, callback=callback, channels=1):
        print("Recording... Press Enter to stop.")
        input()
        print("Stopping...")
        
    return recorded_data

# ----------------------------------------------------------------------

def time_analysis(recorded_data: list) -> tuple[list, list]:
    recording = np.array(recorded_data).flatten()
    RECORDING_TIME = len(recording)/SAMPLE_RATE
    time_axis = np.linspace(0., RECORDING_TIME, len(recording), endpoint=False)
    
    return time_axis, recording
    
def freq_analysis(recorded_data: list) -> tuple[list, list]:
    
    f, t, Z = stft(np.array(recorded_data).flatten(), fs=SAMPLE_RATE, nperseg=FRAME_LEN, noverlap=0)
    # f is list of frequencies
    # t is list of timestamps of frame
    # Z (row, col) is (frequency, time)
    mag_Z = np.abs(Z)
    
    frequencies = f
    freq_magnitudes = []
    for i in range(Z.shape[1]):
        freq_magnitudes.append(mag_Z[:,i])
    
    return frequencies, freq_magnitudes

# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
def main():
    recorded_data = record()
    if len(recorded_data) == 0:
        return
    
    time_axis, recording = time_analysis(recorded_data)
    frequencies, freq_magnitudes = freq_analysis(recorded_data)
    
    time_arr = np.arange(SAMPLE_RATE)
    wave1 = np.sin(2 * np.pi * 440 * time_arr/ SAMPLE_RATE)
    wave2 = wave1 + np.sin(2 * np.pi * 349 * time_arr/ SAMPLE_RATE) 
    wave3 = wave2 + np.sin(2 * np.pi * 262 * time_arr/ SAMPLE_RATE) 
    wave4 = np.sin(2 * np.pi * 880 * time_arr/ SAMPLE_RATE) + np.sin(2 * np.pi * 698 * time_arr/ SAMPLE_RATE) + np.sin(2 * np.pi * 524 * time_arr/ SAMPLE_RATE) 
    wave5 = np.sin(2 * np.pi * 880 * time_arr/ SAMPLE_RATE) + np.sin(2 * np.pi * 698 * time_arr/ SAMPLE_RATE) 
    _, f1 = freq_analysis(wave1)
    _, f2 = freq_analysis(wave2)
    _, f3 = freq_analysis(wave3)
    _, f4 = freq_analysis(wave4)
    _, f5 = freq_analysis(wave5)
    
    
    
    

    
    

if __name__ == "__main__":
    main()