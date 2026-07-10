# eridian_translator.py - Hernan Le

# This script takes in audio and matches recording to words in an AudioDictionary,
# printing the word to the terminal. If no match is found, "???" will be printed. 

# When encountering a "???", assign a word to the audio by entering the 
# word enclosed by angle brackets.
# For example: "<word>"

# The program will continue parsing words, which may visually conflict with 
# user input, but upon submitting the word, only the user inputted text will be processed.

# To skip assigning a word to audio, simply press Enter. A reminder of 
# how many "???" there are left to be assigned a word will be printed.

# Without angle brackets, the program will also skip assigning a word to audio.

# Avoid pressing Enter multiple times for a single "???" because doing so will 
# actually queue input for future "???". 
# For instance, pressing Enter 5 times will queue up inputs (empty inputs: "") for 
# the next 5 "???" and will automatically apply those inputs as the "???" arrive.

# ----------------------------------------------------------------------

from threading import Thread, Lock
from queue import Queue # used for passing data between threads

from realtime_audio import record_word
from audio_dictionary import AudioDictionary

# ----------------------------------------------------------------------

# records words and adds to rec_queue
class RecordingThread(Thread):
    def __init__(self, rec_queue:Queue):
        Thread.__init__(self, daemon=True)
        self._rec_queue = rec_queue
    
    def run(self):
        while True:
            recording = record_word()
            self._rec_queue.put(recording)

# tries to find word in audio dictionary, print word if found, send to add_queue otherwise
class MatchingThread(Thread):
    def __init__(self, rec_queue:Queue, add_queue:Queue, aud:AudioDictionary, aud_lock:Lock):
        Thread.__init__(self, daemon=True)
        self._rec_queue = rec_queue
        self._add_queue = add_queue
        self._aud = aud
        self._aud_lock = aud_lock
    
    def run(self):
        while True:
            # Dequeue data. Makes thread sleep if no data
            rec = self._rec_queue .get()
            
            with self._aud_lock:
                res = self._aud.match_recording(rec)
                
                if res["value"] is not None:
                    word = res["value"]["label"]
                    print(word, end=" ", flush=True)
                else:
                    print("???", end=" ", flush=True)
                    # send to main thread to get input if no match found
                    self._add_queue.put(rec) 
            


# ----------------------------------------------------------------------

# stdin/stdout on main thread
def main():
    aud = AudioDictionary(data_name="rocky_words", reset=False)
    aud_lock = Lock() # prevent race conditions with audio dictionary
    rec_queue = Queue()
    add_queue = Queue()
    
    recording_thread = RecordingThread(rec_queue)
    matching_thread = MatchingThread(rec_queue, add_queue, aud, aud_lock)
    recording_thread.start()
    matching_thread.start()
    
    while True:
        # Dequeue data. Makes thread sleep if no data
        rec = add_queue.get()
        
        # User input in the format of "<word>". 
        # If no angle brackets, input for corresponding "???" is skipped.
        new_input = input()
        if len(new_input) > 0:
            i = new_input.find("<")
            j = new_input.find(">")
            if i != -1 and j != -1:
                new_word = new_input[i+1:j]
                with aud_lock:
                    aud.add_recording(rec, label=new_word)
                    print(f"[{new_word} added]")
                    aud.save()
            else:
                # reminder of how many "???" left to be assigned
                print(f"[{add_queue.qsize()} remain in queue]") 
        else:
            print(f"[{add_queue.qsize()} remain in queue]")

if __name__ == "__main__":
    main()