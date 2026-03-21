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
        self._data : dict[str, list[tuple[str,int]]] = {} # maps hashes to their words and time points
        self._num_words :int= 0
        self._shortest = float("inf")
        self._longest = 0
    
    def add_hashes(self, word:str, hashes:list):
        for h, t in hashes:
            if self._data.get(h, None) == None:
                self._data[h] = [(word, t)]
            else:
                self._data[h].append( (word, t) )
        self._num_words += 1
        # the last hash should have the last time point
        final_t = hashes[-1][1]
        if final_t < self._shortest:
            self._shortest = final_t
        if final_t > self._longest:
            self._longest = final_t
            
    def find_match(self, hashes:list ) -> str|None:
        # store the match counts of different time offsets of audios
        offsets : dict[tuple[str,int], int] = {} 
        
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
        # item is ((word, time delta), count)
        # get the offsets item with the best count 
        best_match = max(offsets.items(), key=lambda item: item[1]) 
        if best_match[1] >= MATCH_THRESHOLD:
            return best_match[0][0] # return string word
        
        return None
    
    def get_dict(self) -> dict[str, list[tuple[str,int]]] :
        return self._data
    def get_num_words(self) -> int:
        return self._num_words
    
    #
    def add_recording(self,  word: str, recorded_data : list[list[float]]):
        _, freq_magintudes = aud.freq_analysis(recorded_data)
        peaks = get_peaks( freq_magintudes )
        hashes = generate_hashes(peaks)
        self.add_hashes(word, hashes)
        
    def match_recording(self, recorded_data:list[list[float]]) -> str:
        _, freq_magintudes = aud.freq_analysis(recorded_data)
        peaks = get_peaks( freq_magintudes )
        hashes = generate_hashes(peaks)
        return self.find_match(hashes)
    
    def __str__(self) -> str:
        return_string = ""
        
        for hash, word_time in self._data.items():
            return_string += f"\n{hash}: {word_time}"
        
        return return_string
            

# ----------------------------------------------------------------------

def main():
    data = FingerprintData()
    
    recorded_data = aud.record()
    data.add_recording( "audio1" , recorded_data,)
    
    print("\nPress Enter to record.")
    input()
    
    recorded_data = aud.record()
    data.add_recording("audio2", recorded_data)
    
    print("\nPress Enter to record.")
    input()
    
    recorded_data = aud.record()
    
    match = data.match_recording(recorded_data)
    if match:
        print(f"Match: {match}")
    else:
        print("No match")
        
    #print(data)
    
    import json
    str_data = json.dumps(data.get_dict())
    data2 = json.loads(str_data)
    # need to convert some lists to tuples! 
    for hash, item_list in data2.items():
        for i in range(len(item_list)):
            item_list[i] = tuple(item_list[i])
    print(f"dicts match after json: {data.get_dict() == data2}")
    print(f"Number of words: {data.get_num_words()}")
    
    

if __name__ == "__main__":
    main()