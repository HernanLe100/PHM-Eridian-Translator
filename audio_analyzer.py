# audio_analyzer.py - Hernan Le

# ----------------------------------------------------------------------

import numpy as np
from scipy.signal import stft

SAMPLE_RATE = 44100 # recording processes 44100 input points per second (44100 Hz)

# number of raw frequency "buckets" per time frame used in Fourier Transform.
# number of output frequency buckets = (RAW_FREQS_PER_FRAME // 2) + 1
# higher -> more detailed spectrogram along frequency domain
RAW_FREQS_PER_FRAME = 2048 

# amount of overlap between time frames
# higher -> more detailed spectrogram along time domain
FRAME_OVERLAP = RAW_FREQS_PER_FRAME * 3 // 4

EPSILON = 1e-10 # "zero" value, prevents some functions from breaking with 0 

# ----------------------------------------------------------------------

# Returns spectrogram of recording as m by n matrix
# with m frequencies and n time frames
def get_spectrogram(recording : np.array):
    _, _, Z = stft(recording, fs=SAMPLE_RATE, nperseg=RAW_FREQS_PER_FRAME, noverlap=FRAME_OVERLAP)
    return np.abs(Z)

# Returns spectrogram with frequencies lower than (strength * max magnitude) zeroed out (to epsilon)
def remove_noise(Z, strength=0.15):
    larqest_freq_mag = np.max(Z)
    subtracted = Z - np.array([larqest_freq_mag * strength])
    return np.where(subtracted < 0, EPSILON, Z)

# ----------------------------------------------------------------------

def main():
    pass

if __name__ == "__main__":
    main()