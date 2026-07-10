# eridian_translator.py - Hernan Le

# ----------------------------------------------------------------------

from threading import Thread, Lock
from queue import Queue # used for passing data between threads

from realtime_audio import record_word
from audio_dictionary import AudioDictionary

# ----------------------------------------------------------------------

class RecordingThread(Thread):
    def __init__(self, rec_queue:Queue):
        Thread.__init__(self, daemon=True)
        self._rec_queue = rec_queue
    
    def run(self):
        while True:
            recording = record_word()
            self._rec_queue.put(recording)
        
class MatchingThread(Thread):
    def __init__(self, rec_queue:Queue, add_queue:Queue, aud:AudioDictionary, lock:Lock):
        Thread.__init__(self, daemon=True)
        self._rec_queue = rec_queue
        self._add_queue = add_queue
        self._aud = aud
        self._lock = lock
    
    def run(self):
        while True:
            # Dequeue data. Makes thread sleep if no data
            rec = self._rec_queue .get()
            
            with self._lock:
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
    aud = AudioDictionary(data_name="words2", reset=False)
    rec_queue = Queue()
    add_queue = Queue()
    lock = Lock()
    
    recording_thread = RecordingThread(rec_queue)
    matching_thread = MatchingThread(rec_queue, add_queue, aud, lock)
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
                with lock:
                    aud.add_recording(rec, label=new_word)
                    print(f"[{new_word} added]")
                    aud.save()
            else:
                print(f"[{add_queue.qsize()} remain in queue]")
        else:
            print(f"[{add_queue.qsize()} remain in queue]")
        

if __name__ == "__main__":
    main()