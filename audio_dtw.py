# audio_dtw.py - Hernan Le

# This module contains functions to perform dynamic time warping (DTW).
# The DTW algorithm use cosine similarity instead of Euclidian distance 
# so that frame vectors are compared by frequency composition rather than volume. 

# ----------------------------------------------------------------------

import numpy as np

# ----------------------------------------------------------------------

# Performs DTW on matrices A and B, returning the final cost, path, and cost matrix.
# A and B have shape (frequencies, frames).
def dtw(A, B):
    if A.shape[0] != B.shape[0]:
        raise ValueError(
            f"Frequency dimension mismatch: A: {A.shape[0]}, B: {B.shape[0]}"
        )
    frames_A = A.shape[1]
    frames_B = B.shape[1]
    
    # normalize columns to their unit lengths for faster cosine similarity via dot product
    # assume column vectors are nonzero
    norm_A = np.linalg.norm(A, axis=0, keepdims=True)
    norm_B = np.linalg.norm(B, axis=0, keepdims=True)
    A_normalized = A / norm_A
    B_normalized = B / norm_B
    # dot the normalized column vectors of A and B
    # shape is (frames_A, frames_B)
    cos_sim_matrix = A_normalized.T @ B_normalized
    # convert to cost
    local_cost_matrix = 1 - cos_sim_matrix

    # dtw_matrix[i, j] stores the minimum accumulated alignment cost for 
    # matching first i A frames (0 to i-1) and first j B frames (0 to j-1)
    dtw_matrix = np.full((frames_A+1, frames_B+1), np.inf)
    dtw_matrix[0, 0] = 0
    
    # fill matrix
    for i in range(1, frames_A+1):
        # get the costs for the entire row (one frame of A dot with each frame of B)
        costs_for_row = local_cost_matrix[i-1, :]

        for j in range(1, frames_B+1):
            dtw_matrix[i, j] = costs_for_row[j-1] + min(
                dtw_matrix[i-1, j-1], # match
                dtw_matrix[i-1, j], # insertion
                dtw_matrix[i, j-1] # deletion
            )

    # backtrack optimal path
    i, j = frames_A, frames_B
    path = []

    while i > 0 and j > 0:
        path.append((i-1, j-1))

        choices = [
            (dtw_matrix[i-1, j-1], i-1, j-1), # match
            (dtw_matrix[i-1, j], i-1, j), # insertion
            (dtw_matrix[i, j-1], i, j-1), # deletion
        ]
        # move to whichever predecessor had the smallest accumulated cost
        _, i, j = min(choices, key=lambda x: x[0])
    
    path.reverse()

    return dtw_matrix[frames_A, frames_B], path, dtw_matrix[1:, 1:]

# ----------------------------------------------------------------------

# Performs DTW on matrices A and B, returning the final cost, path, and cost matrix.
# A and B have shape (frequencies, frames).
# As the algorithm runs, if minimum cost exceeds cutoff, the function ends 
# and returns (np.inf, None, None).
def dtw_with_cutoff(A, B, cutoff=np.inf):
    if A.shape[0] != B.shape[0]:
        raise ValueError(
            f"Frequency dimension mismatch: A: {A.shape[0]}, B: {B.shape[0]}"
        )
    # make the outer loop the longer of the two to allow cutoff to save more time
    if B.shape[1] > A.shape[1]:
        temp = A
        A = B
        B = temp
        
    frames_A = A.shape[1]
    frames_B = B.shape[1]
    
    # normalize columns to their unit lengths for faster cosine similarity via dot product
    # assume column vectors are nonzero
    norm_A = np.linalg.norm(A, axis=0, keepdims=True)
    norm_B = np.linalg.norm(B, axis=0, keepdims=True)
    A_normalized = A / norm_A
    B_normalized = B / norm_B
    # dot the normalized column vectors of A and B
    # shape is (frames_A, frames_B)
    cos_sim_matrix = A_normalized.T @ B_normalized
    # convert to cost
    local_cost_matrix = 1 - cos_sim_matrix

    # dtw_matrix[i, j] stores the minimum accumulated alignment cost for 
    # matching first i A frames (0 to i-1) and first j B frames (0 to j-1)
    dtw_matrix = np.full((frames_A+1, frames_B+1), np.inf)
    dtw_matrix[0, 0] = 0
    
    # fill matrix
    for i in range(1, frames_A+1):
        # get the costs for the entire row (one frame of A dot with each frame of B)
        costs_for_row = local_cost_matrix[i-1, :]

        for j in range(1, frames_B+1):
            dtw_matrix[i, j] = costs_for_row[j-1] + min(
                dtw_matrix[i-1, j-1], # match
                dtw_matrix[i-1, j], # insertion
                dtw_matrix[i, j-1] # deletion
            )
            
        # if the minimum cost for first i A frames across all B frames is 
        # more than the cutoff amount, then end the function early
        if i%5==0 and np.min(dtw_matrix[i, 1:]) > cutoff: # check every 5 frames
            print(f"cutoff at i={i+1} of {frames_A}")
            return np.inf, None, None

    # backtrack optimal path
    i, j = frames_A, frames_B
    path = []

    while i > 0 and j > 0:
        path.append((i-1, j-1))

        choices = [
            (dtw_matrix[i-1, j-1], i-1, j-1), # match
            (dtw_matrix[i-1, j], i-1, j), # insertion
            (dtw_matrix[i, j-1], i, j-1), # deletion
        ]
        # move to whichever predecessor had the smallest accumulated cost
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
    print(f"s1: {s1.shape}")
    print(f"s2: {s2.shape}")
    print(f"s3: {s3.shape}")
    print()
    
    score2, p2, _ = dtw(s1, s2)
    score3, p3, _ = dtw(s1, s3)
    
    print("recording 2 DTW cost:", score2)
    print("recording 3 DTW cost:", score3)
    print()
    print("recording 2 DTW path length:", len(p2))
    print("recording 3 DTW path length:", len(p3))
    print()
    print("recording 2 DTW scaled cost:", score2/len(p2))
    print("recording 3 DTW scaled cost:", score3/len(p3))
    
    print()
    print("Testing cutoff:")
    best = np.inf
    score1, _, _ = dtw_with_cutoff(s1, s1, cutoff=best)
    if score1 < best:
        best = score1
    score2, _, _ = dtw_with_cutoff(s1, s2, cutoff=best)
    if score2 < best:
        best = score2
    score3, _, _ = dtw_with_cutoff(s1, s3, cutoff=best)
    
    print(score1)
    print(score2)
    print(score3)

if __name__ == "__main__":
    main()