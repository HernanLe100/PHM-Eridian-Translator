# audio_dtw.py - Hernan Le

# This module contains functions to perform dynamic time warping (DTW).
# The DTW algorithm use cosine similarity instead of Euclidian distance 
# so that frame vectors are compared by frequency composition rather than volume. 

# ----------------------------------------------------------------------

import numpy as np

# ----------------------------------------------------------------------

# Compares how similar vectors a and b are
# Assume a and b are nonzero
def cos_sim(a, b):
    # (a * b) / (|a| |b|)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Performs DTW on matrices A and B, returning the final cost, path, and cost matrix.
# A and B have shape (frequencies, frames).
def dtw(A, B):
    if A.shape[0] != B.shape[0]:
        raise ValueError(
            f"Frequency dimension mismatch: A: {A.shape[0]}, B: {B.shape[0]}"
        )
    frames_A = A.shape[1]
    frames_B = B.shape[1]

    # dtw_matrix[i, j] stores the minimum accumulated alignment cost for 
    # matching first i A frames (0 to i-1) and first j B frames (0 to j-1)
    dtw_matrix = np.full((frames_A+1, frames_B+1), np.inf)
    dtw_matrix[0, 0] = 0

    # Fill matrix
    for i in range(1, frames_A+1):
        a_frame = A[:, i-1]

        for j in range(1, frames_B+1):
            b_frame = B[:, j-1]

            # cost lower -> more similar
            cost = 1 - cos_sim(a_frame, b_frame) 

            dtw_matrix[i, j] = cost + min(
                dtw_matrix[i-1, j-1], # match
                dtw_matrix[i-1, j], # insertion
                dtw_matrix[i, j-1] # deletion
            )

    # Backtrack optimal path
    i, j = frames_A, frames_B
    path = []

    while i > 0 and j > 0:
        path.append((i-1, j-1))

        choices = [
            (dtw_matrix[i-1, j-1], i-1, j-1), # match
            (dtw_matrix[i-1, j], i-1, j), # insertion
            (dtw_matrix[i, j-1], i, j-1), # deletion
        ]
        # Move to whichever predecessor had the smallest accumulated cost.
        _, i, j = min(choices, key=lambda x: x[0])
    
    path.reverse()

    return dtw_matrix[frames_A, frames_B], path, dtw_matrix[1:, 1:]

# ----------------------------------------------------------------------

def main():
    from realtime_audio import record_word
    from audio_analyzer import get_spectrogram, remove_noise
    
    input("press Enter when ready")
    print("recording...")
    r1 = record_word()
    print("recording complete")
    input("press Enter when ready")
    print("recording...")
    r2 = record_word()
    print("recording complete")
    input("press Enter when ready")
    print("recording...")
    r3 = record_word()
    print("recording complete")
    print()
    
    s1 = remove_noise(get_spectrogram(r1))
    s2 = remove_noise(get_spectrogram(r2))
    s3 = remove_noise(get_spectrogram(r3))
    
    score2, p2, _ = dtw(s1, s2)
    score3, p3, _ = dtw(s1, s3)
    
    print("recording 2 DTW cost:", score2)
    print("recording 3 DTW cost:", score3)
    print()
    print("recording 2 DTW scaled cost:", score2/len(p2))
    print("recording 3 DTW scaled cost:", score3/len(p3))

if __name__ == "__main__":
    main()