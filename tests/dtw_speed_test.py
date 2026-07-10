

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

import fastdtw # slower with shorter matrices
# librosa - too slow
# dtaidistance - only fast for 1D data
import dtw as dtw_python # dtw-python - still slower

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
    
    print(f"DTW avg CPU time:        {dtw_speed_test(s1,s2)}")
    print(f"FastDTW avg CPU time:    {fastdtw_speed_test(s1,s2)}")
    print(f"DTW-Python avg CPU time: {dtw_python_speed_test(s1,s2)}")
    
    print(f"Recording 1 length: {len(r1)/44100} seconds")
    print(f"Recording 2 length: {len(r2)/44100} seconds")
    print(f"Spectrogram 1: {s1.shape}")
    print(f"Spectrogram 2: {s2.shape}")
    
    print(f"DTW score:        {dtw(s1, s2)[0]}")
    print(f"FastDTW score:    {fastdtw.fastdtw(s1.T, s2.T, dist=cosine)[0]}")
    print(f"DTW-Python score: {dtw_python.dtw(s1.T, s2.T, dist_method="cosine").distance}")
    
# ----------------------------------------------------------------------

    
def main():
    speed_comparison()

if __name__ == "__main__":
    main()