# bulk_match_speed_test.py - Hernan Le

# Compare speeds of different methods for searching audio matches

# ----------------------------------------------------------------------
import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
# ----------------------------------------------------------------------

import os
import time
import gc # garbage collection
import numpy as np

from realtime_audio import record_word
from audio_analyzer import get_spectrogram, remove_noise
from audio_dtw import dtw, dtw_with_cutoff
from bucket_vp_tree import Bucket_VP_Tree 
from audio_dictionary import AudioDictionary

# ----------------------------------------------------------------------

def flush_cache():
    gc.collect()
    temp = np.ones(10000000)
    _ = temp * 10
    del temp
    gc.collect()

def gen_rand_mat(rng, num_syl):
    mat = None
    for i in range(num_syl):
        syl_len = rng.integers(low=1, high=500//num_syl)
        
        A = np.full((1025, syl_len), 1e-10)
        
        num_notes = int(rng.random()*5) + 1
        freqs = (rng.random(num_notes) * 1025).astype(int)
        mags = rng.random(num_notes) * 10 + 1.5
        for i in range(len(freqs)):
            A[freqs[i] ] = np.full(syl_len, mags[i])

        if mat is None:
            mat = A
        else:
            mat = np.concatenate((mat, A), axis=1)
    return mat

def gen_noise_mat(rng, shape):
    return rng.normal(loc=0.1, scale=0.1, size=shape)

# ----------------------------------------------------------------------

def bulk_match(num_matrices, seed=None, proportion_random=0.95, debug=True):
    flush_cache()
    
    rng = np.random.default_rng(seed=seed)
    
    num_syllables = int(rng.random()*5) + 1
    target_matrix = gen_rand_mat(rng, num_syllables)
    
    best_norm = 0.2
    total_time = 0
    
    for i in range(num_matrices):
        num_syllables = int(rng.random()*5) + 1
        
        comp_matrix = None
        if rng.random() < proportion_random:
            comp_matrix = gen_rand_mat(rng, num_syllables)
        else:
            comp_matrix = gen_noise_mat(rng, target_matrix.shape) + target_matrix
        
        start = time.process_time()
        cost, path, _ = dtw(target_matrix, comp_matrix)
        end = time.process_time()
        
        if cost/len(path) < best_norm:
            best_norm = cost/len(path)
            best = cost
            if debug:
                print()
                print(i+1)
                print()
        if debug:
            print(f"{i+1} done in {end-start}")
            print(f"Cost (normalized): {cost/len(path)}")
        total_time += end-start
        
    print()
    print(f"Total time: {total_time}")
    print(f"Best (normalized): {best_norm}")
    print()
    return total_time

def bulk_match_with_cutoff(num_matrices, seed=None, proportion_random=0.95, debug=True):
    flush_cache()
    
    rng = np.random.default_rng(seed=seed)
    
    num_syllables = int(rng.random()*5) + 1
    target_matrix = gen_rand_mat(rng, num_syllables)
    
    best_norm = 0.2
    total_time = 0
    
    for i in range(num_matrices):
        num_syllables = int(rng.random()*5) + 1
        
        comp_matrix = None
        if rng.random() < proportion_random:
            comp_matrix = gen_rand_mat(rng, num_syllables)
        else:
            comp_matrix = gen_noise_mat(rng, target_matrix.shape) + target_matrix
        
        allowed = best_norm  * (target_matrix.shape[1] + comp_matrix.shape[1] + 1)
        
        start = time.process_time()
        cost, path, _ = dtw_with_cutoff(target_matrix, comp_matrix, cutoff=allowed)
        end = time.process_time()
        
        if path is None:
            path = [0]
        if cost/len(path) < best_norm:
            best_norm = cost/len(path)
            best = cost
            if debug:
                print()
                print(i+1)
                print()
        if debug:
            print(f"{i+1} done in {end-start}")
            print(f"Cost (normalized): {cost/len(path)}")
        total_time += end-start
            
    print()
    print(f"Total time: {total_time}")
    print(f"Best (normalized): {best_norm}")
    print()
    return total_time

def bulk_match_with_bvp(num_matrices, seed=None, proportion_random=0.95, debug=True):
    flush_cache()
    
    rng = np.random.default_rng(seed=seed)
    
    def dist_func(a,b):
        cost, path, _ = dtw(a,b)
        return cost/len(path)
    buckets = 10
    bvp = Bucket_VP_Tree(dist_func=dist_func, bucket_capacity=buckets)
    
    num_syllables = int(rng.random()*5) + 1
    target_matrix = gen_rand_mat(rng, num_syllables)
    
    time_to_add = 0
    
    for i in range(num_matrices):
        num_syllables = int(rng.random()*5) + 1
        
        comp_matrix = None
        if rng.random() < proportion_random:
            comp_matrix = gen_rand_mat(rng, num_syllables)
        else:
            comp_matrix = gen_noise_mat(rng, target_matrix.shape) + target_matrix
        
        start = time.process_time()
        bvp.add(comp_matrix)
        end = time.process_time()
        if debug:
            print(f"{i+1} {end-start}")
        time_to_add += end-start
    
    if debug:
        print("searching")
    start = time.process_time()
    match = bvp.nearest(target_matrix)
    end = time.process_time()
    
    print()
    print(f"Buckets: {buckets}")
    print(f"Time to add: {time_to_add}")
    print(f"Match time: {end-start}")
    print(f"Best (normalized): {match["dist"]}")
    print()
    
    return end-start

# ----------------------------------------------------------------------

def bulk_match_with_aud(num_matrices, seed=None, proportion_random=0.95, debug=True):
    flush_cache()
    
    rng = np.random.default_rng(seed=seed)
    
    time_to_add = 0
    start = time.process_time()
    
    addNew = not os.path.isdir("bulk_spectrograms")
    
    aud = AudioDictionary(data_name="bulk_spectrograms")
    end = time.process_time()
    time_to_add += end-start
    
    num_syllables = int(rng.random()*5) + 1
    target_matrix = gen_rand_mat(rng, num_syllables)
    
    if addNew:
        for i in range(num_matrices):
            num_syllables = int(rng.random()*5) + 1
            
            comp_matrix = None
            if rng.random() < proportion_random:
                comp_matrix = gen_rand_mat(rng, num_syllables)
            else:
                comp_matrix = gen_noise_mat(rng, target_matrix.shape) + target_matrix
            
            start = time.process_time()
            aud.add_spectrogram(comp_matrix)
            end = time.process_time()
            if debug:
                print(f"{i+1} {end-start}")
            time_to_add += end-start
        aud.save()
    if debug:
        print("searching")
    start = time.process_time()
    match = aud.match_spectrogram(target_matrix)
    end = time.process_time()
    
    print()
    print(f"Time to add: {time_to_add}")
    print(f"Match time: {end-start}")
    print(f"Best (normalized): {match["dist"]}")
    print()
    
    return end-start

# ----------------------------------------------------------------------

def main():
    t1 = bulk_match(100, seed=100, debug=True)
    t2 = bulk_match_with_cutoff(100, seed=100, debug=True)
    t3 = bulk_match_with_bvp(100, seed=100, debug=True)
    t4 = bulk_match_with_aud(100, seed=100, debug=True)

if __name__ == "__main__":
    main()