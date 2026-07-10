# audio_dictionary.py - Hernan Le

# This module stores spectrograms in a VP tree and uses DTW to find matches.

# Spectrograms are automatically stored in a .h5 file as they are added 
# to the data structure and accessed by their "key".

# ----------------------------------------------------------------------

import numpy as np
import os
import json
import h5py

from audio_analyzer import get_spectrogram, remove_noise
from audio_dtw import dtw, dtw_with_cutoff
from bucket_vp_tree import Bucket_VP_Tree 

SPECTROGRAM_FILE = "spectrograms.h5"
STRUCTURE_FILE = "structure.json"
BUCKET_CAPACITY = 10
NEAREST_BOUND = 0.15
QUERY_KEY = "query"

# ----------------------------------------------------------------------

class AudioDictionary:
    
    # data_name specifies the name of the subdirectory that stores the data of this AudioDictionary.
    # If reset is True, the named subdirectory will be cleared if it does not already exist.
    def __init__(self, data_name="spectrograms", reset=False):
        self._data_name = data_name
        self._spectrogram_file = f"{data_name}/{SPECTROGRAM_FILE}"
        self._structure_file = f"{data_name}/{STRUCTURE_FILE}"
        
        self._set_use_cutoff(False) # do not use dtw_with_cutoff() by default
        
        # Spectrograms A and B are accessed by their keys, a and b
        # Returns the normalized DTW cost (normalized cost = total cost / path length)
        def dist_func(a,b):
            with h5py.File(self._spectrogram_file, "r") as f:
                A = f[str(a["key"])][:]
                B = f[str(b["key"])][:]
                
                if self._use_cutoff:
                    cost, path, _ = dtw_with_cutoff(
                        A,B, cutoff= self._best_cost_norm * (A.shape[1] + B.shape[1] + 1)
                    )
                    if path is None: # if early cutoff, just return the current best
                        return self._best_cost_norm
                    
                    cost_norm = cost/len(path)
                    if cost_norm < self._best_cost_norm: # if found better cost, update best
                        self._best_cost_norm = cost_norm
                    return cost_norm
                else:
                    cost, path, _ = dtw(A,B)
                    return cost/len(path)
        
        # num keeps track of number of spectrograms in the .h5 file
        # will be used to set key of new spectrograms being added
        self._num = 0
        
        data = None
        
        if not os.path.isdir(data_name) or reset:
            # create folder if does not exist yet
            # or if resetting
            os.makedirs(data_name, exist_ok=True)
            with h5py.File(self._spectrogram_file, "w") as f:
                pass 
            with open(self._structure_file, "w") as f:
                json.dump({}, f)
        else:
            # otherwise, get data from the files
            try:
                with h5py.File(self._spectrogram_file, "a") as f:
                    if QUERY_KEY in f:
                        del f[QUERY_KEY]
                    self._num = len(f.keys())
                
                with open(self._structure_file, "r") as f:
                    data = json.load(f)   
                    
            except Exception as e:
                raise e
        
        # create the VP tree with pregenerated structure if data is given
        self._audio_dict = Bucket_VP_Tree(dist_func, bucket_capacity=BUCKET_CAPACITY, data=data)
    
    # helper method to set whether to use dtw_with_cutoff() or just dtw()
    def _set_use_cutoff(self, status:bool):
        self._use_cutoff = status
        self._best_cost_norm = NEAREST_BOUND # reset the best normalized cost
    
    # adds recording to the data structure
    def add_recording(self, recording, label=""):
        spec = remove_noise(get_spectrogram(recording))
        self.add_spectrogram(spec, label)
    
    # add spectrogram to the data structure
    def add_spectrogram(self, spec, label=""):
        with h5py.File(self._spectrogram_file, "a") as f:
            f.create_dataset(str(self._num), data=spec, compression="gzip")
        self._set_use_cutoff(False)
        self._audio_dict .add({"key": self._num, "label": label})    
        self._num += 1
    
    # saves the structure of the current VP tree to a .json file
    def save(self):
        with open(self._structure_file, "w") as f:
            json.dump(self._audio_dict.to_dict(), f, indent=4)
        
    # finds best match for recording
    def match_recording(self, recording):
        spec = remove_noise(get_spectrogram(recording))
        return self.match_spectrogram(spec)
    
    # finds best match for spectrogram
    def match_spectrogram(self, spec):
        with h5py.File(self._spectrogram_file, "a") as f:
            if QUERY_KEY in f:
                del f[QUERY_KEY]
            f.create_dataset(QUERY_KEY, data=spec, compression="gzip")
            
            self._set_use_cutoff(True) # use dtw_with_cutoff()
            match = self._audio_dict.nearest({"key": QUERY_KEY}, bound=NEAREST_BOUND)
            del f[QUERY_KEY] # remove query
            self._set_use_cutoff(False) # and reset 
            return match

# ----------------------------------------------------------------------

def main():
    import realtime_audio
    aud = AudioDictionary(reset=True)

    for i in range(5):
        input("Press Enter when ready:")
        print("Recording...")
        rec = realtime_audio.record_word()
        print(f"Recording {i+1} complete.\n")
        aud.add_recording(rec)

    aud.save()
    
    input("Press Enter when ready:")
    print("Recording...")
    rec = realtime_audio.record_word()
    print(f"Recording complete.\n")
    
    print(aud.match_recording(rec))
   
    
    

if __name__ == "__main__":
    main()