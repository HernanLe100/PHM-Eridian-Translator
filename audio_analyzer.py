# audio_analyzer.py - Hernan Le

# ----------------------------------------------------------------------

import numpy as np
from scipy.signal import stft, istft

SAMPLE_RATE = 44100 # recording processes 44100 input points per second (44100 Hz)
FRAME_LEN = 2048 # number of points being analyzed at a time frame for FFT
EPSILON = 1e-10

# ----------------------------------------------------------------------

def get_spectrogram(recording : np.array):
    _, _, Z = stft(recording, fs=SAMPLE_RATE, nperseg=FRAME_LEN, noverlap=FRAME_LEN*3//4)
    return np.abs(Z)

def remove_noise(Z, strength=0.15):
    larqest_freq_mag = np.max(Z)
    subtracted = Z - np.array([larqest_freq_mag * strength])
    return np.where(subtracted <= 0, EPSILON, Z)

# ----------------------------------------------------------------------

def main():
    pass

if __name__ == "__main__":
    main()