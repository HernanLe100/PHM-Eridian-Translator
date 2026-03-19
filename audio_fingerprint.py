# audio_fingerprint.py - Hernan Le

# This module 
# ----------------------------------------------------------------------

import numpy as np
import hashlib
from scipy.signal import find_peaks

import audio_analyzer as aud
from audio_analyzer import SAMPLE_RATE, FRAME_LEN

MATCH_THRESHOLD = 0 #

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
        
        # pair up with (PAIR_RANGE_BOUND-1) future peaks
        for j in range(1, PAIR_RANGE_BOUND):
            if i + j < len(peaks):
                t2, f2 = peaks[i + j]
                dt = t2 - t1 # get time delta
                
                if 0 < dt and dt <= MAX_TIME_DELTA:
                    # hashes in form (f1, f2, dt)
                    h = hashlib.sha256(f"{f1},{f2},{dt}".encode()).hexdigest() # deterministic hashing 
                    hashes.append((h, t1)) # add (hash, time point) to list
    return hashes

# ----------------------------------------------------------------------

class FingerprintData:
    def __init__(self):
        self._data : {str, list[tuple(str,int)]} = {} # maps hashes to their words and time points
    
    def add_hashes(self, word:str, hashes:list):
        for h, t in hashes:
            if self._data.get(h, None) == None:
                self._data[h] = [(word, t)]
            else:
                self._data[h].append( (word, t) )
    
    def find_match(self, hashes:list ) -> str|None:
        # store the match counts of different time offsets of audios
        offsets : {tuple(str,int), int} = {} 
        
        # for each hash in the hashes list, find items in data with same hash
        for h, t in hashes:
            if h in self._data:
                # for each (word, time point) of item, compare and match with queried info
                for word, t_word in self._data[h]:
                    offset_key = (word, t_word - t) # use the offset between time points 
                    # count the number of matches for a given (word, time delta)
                    if offsets.get( offset_key, None ) == None:
                        offsets[offset_key] = 1
                    else:
                        offsets[offset_key] += 1
        
        if len(offsets) == 0:
            return None
        # item is ((word, time point), count)
        # get the offsets item with the best count 
        best_match = max(offsets.items(), key=lambda item: item[1]) 
        if best_match[1] >= MATCH_THRESHOLD:
            return best_match[0][0] # return string word
        
        return None
            

# ----------------------------------------------------------------------

def main():
    data = FingerprintData()
    
    recorded_data = aud.record()
    frequencies, freq_magintudes = aud.freq_analysis(recorded_data)
    peaks = get_peaks( freq_magintudes )
    hashes = generate_hashes(peaks)
    data.add_hashes("audio1", hashes)
    
    print("\nPress Enter to record.")
    input()
    
    recorded_data = aud.record()
    frequencies, freq_magintudes = aud.freq_analysis(recorded_data)
    peaks = get_peaks( freq_magintudes )
    hashes = generate_hashes(peaks)
    data.add_hashes("audio2", hashes)
    
    print("\nPress Enter to record.")
    input()
    
    recorded_data = aud.record()
    frequencies, freq_magintudes = aud.freq_analysis(recorded_data)
    peaks = get_peaks( freq_magintudes )
    hashes = generate_hashes(peaks)
    
    match = data.find_match(hashes)
    if match:
        print(f"Match: {match}")
    else:
        print("No match")
    

if __name__ == "__main__":
    main()