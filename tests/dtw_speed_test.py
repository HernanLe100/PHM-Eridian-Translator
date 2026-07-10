# dtw_speed_test.py - Hernan Le

# Compare speeds of different DTW algorithm implementations

# ----------------------------------------------------------------------
import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
# ----------------------------------------------------------------------

import time
import gc # garbage collection
import numpy as np
from scipy.spatial.distance import cosine # function for cosine distance

import librosa # too slow
import fastdtw # slower with shorter matrices
from dtaidistance import dtw_ndim as dtai_dtw # only fast for 1D data
import dtw as dtw_python # still slower

from realtime_audio import record_word
from audio_analyzer import get_spectrogram, remove_noise
from audio_dtw import dtw

# ----------------------------------------------------------------------

def flush_cache():
    gc.collect()
    temp = np.ones(10000000)
    _ = temp * 10
    del temp
    gc.collect()

# ----------------------------------------------------------------------

def record_test_clips(num_clips):
    clips = []
    for i in range(num_clips):
        input("Press Enter when ready:")
        print("Recording...")
        rec = record_word()
        print(f"Recording {i+1} complete.\n")
        clips.append(rec)
    return clips
    
# ----------------------------------------------------------------------

def dtw_speed_test(A, B, num_iter=10):
    flush_cache()
    sum = 0
    for i in range(num_iter):
        start = time.process_time()
        dtw(A, B)
        end = time.process_time()
        sum += end-start
    return sum / num_iter

def librosa_speed_test(A, B, num_iter=10):
    flush_cache()
    sum = 0
    for i in range(num_iter):
        start = time.process_time()
        librosa.sequence.dtw(A, B, metric="cosine")
        end = time.process_time()
        sum += end-start
    return sum / num_iter

def fastdtw_speed_test(A, B, num_iter=10):
    flush_cache()
    A = A.T
    B = B.T
    sum = 0
    for i in range(num_iter):
        start = time.process_time()
        fastdtw.fastdtw(A, B, dist=cosine)
        end = time.process_time()
        sum += end-start
    return sum / num_iter

def dtai_speed_test(A, B, num_iter=10):
    flush_cache()
    A = A.T
    B = B.T
    # no cosine distance parameter
    norm_A = A / np.linalg.norm(A, axis=1, keepdims=True)
    norm_B = B / np.linalg.norm(B, axis=1, keepdims=True)
    
    sum = 0
    for i in range(num_iter):
        start = time.process_time()
        dtai_dtw.distance(norm_A, norm_B)
        end = time.process_time()
        sum += end-start
    return sum / num_iter

def dtw_python_speed_test(A, B, num_iter=10):
    flush_cache()
    A = A.T
    B = B.T
    sum = 0
    for i in range(num_iter):
        start = time.process_time()
        dtw_python.dtw(A, B, dist_method="cosine")
        end = time.process_time()
        sum += end-start
    return sum / num_iter

# ----------------------------------------------------------------------

def speed_comparison():
    r1, r2 = record_test_clips(2)
    s1 = remove_noise(get_spectrogram(r1))
    s2 = remove_noise(get_spectrogram(r2))
    
    print(f"Recording 1 length: {len(r1)/44100} seconds")
    print(f"Recording 2 length: {len(r2)/44100} seconds")
    print(f"Spectrogram 1: {s1.shape}")
    print(f"Spectrogram 2: {s2.shape}")
    print()
    print(f"DTW avg CPU time:          {dtw_speed_test(s1,s2)}")
    print(f"Librosa avg CPU time:      {librosa_speed_test(s1,s2)}")
    print(f"FastDTW avg CPU time:      {fastdtw_speed_test(s1,s2)}")
    print(f"DTAIDistance avg CPU time: {dtai_speed_test(s1,s2)}")
    print(f"DTW-Python avg CPU time:   {dtw_python_speed_test(s1,s2)}")
    print()
    print(f"DTW score:          {dtw(s1, s2)[0]}")
    print(f"Librosa score:      {librosa.sequence.dtw(s1, s2, metric="cosine")[0][-1,-1]}")
    print(f"FastDTW score:      {fastdtw.fastdtw(s1.T, s2.T, dist=cosine)[0]}")
    print(f"DTAIDistance score: {dtai_dtw.distance(s1.T / np.linalg.norm(s1.T, axis=1, keepdims=True), s2.T / np.linalg.norm(s2.T, axis=1, keepdims=True))}")
    print(f"DTW-Python score:   {dtw_python.dtw(s1.T, s2.T, dist_method="cosine").distance}")
    
# ----------------------------------------------------------------------

    
def main():
    speed_comparison()

if __name__ == "__main__":
    main()