import numpy as np
import hashlib
from scipy.signal import find_peaks


import audio_analyzer as aud
from audio_analyzer import SAMPLE_RATE, FRAME_LEN

# ----------------------------------------------------------------------

# Gets the highest magnitude frequencies from the array returned by aud.freq_analysis()
# Returns list of (time point, frequency)
def get_peaks(freq_magnitudes:list[list]) -> list:
    HEIGHT_THRESHOLD_RATIO = 0.2
    first_peak_t = -1
    peaks_list = []
    
    max_mag = float( np.max( np.array(freq_magnitudes).flatten()) )
    h = max_mag * HEIGHT_THRESHOLD_RATIO
    
    for t in range(len(freq_magnitudes)):
        # get the peaks at each time frame
        peaks, _ = find_peaks(freq_magnitudes[t], height= h) # sorted
        
        # add the time and freq of each peak
        for f in peaks:
            if first_peak_t == -1:
                first_peak_t = t
            
            peaks_list.append( (t-first_peak_t, f) ) # shift audio forward so that first peak is at t=0
            # by the time this runs, first_peak_t is no longer -1
        
    return peaks_list

# Generate the list of hashes from a given peaks list
# Returns a list of (hash value, time point)
def generate_hashes(peaks:list) -> list:
    PAIR_RANGE_BOUND = 5
    MAX_TIME_DELTA = 200
    
    hashes = []
    
    for i in range(len(peaks)):
        t1, f1 = peaks[i]
        
        # pair up with (PAIR_RANGE_BOUND-1) nearby peaks
        for j in range(1, PAIR_RANGE_BOUND):
            if i + j < len(peaks):
                t2, f2 = peaks[i + j]
                dt = t2 - t1 # get time delta
                
                if 0 < dt and dt <= MAX_TIME_DELTA:
                    # hashes in form (f1, f2, dt)
                    h = hashlib.sha256(f"{f1},{f2},{dt}".encode()).hexdigest() # deterministic hashing 
                    hashes.append((h, t1))
    return hashes

# ----------------------------------------------------------------------

def main():
    recorded_data = aud.record()
    frequencies, freq_magintudes = aud.freq_analysis(recorded_data)
    peaks = get_peaks( freq_magintudes )
    hashes = generate_hashes(peaks)
    
    

if __name__ == "__main__":
    main()