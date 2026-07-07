# eridian_translator.py - Hernan Le

# ----------------------------------------------------------------------

from threading import Thread
from queue import Queue # used for passing data between threads

from realtime_audio import record_word
from audio_dictionary import AudioDictionary


# ----------------------------------------------------------------------

class AudioMatchingThread(Thread):
    def __init__(self, aud:AudioDictionary, rec_queue:Queue, add_queue:Queue):
        Thread.__init__(self, daemon=True)
        self._aud = aud
        self._rec_queue = rec_queue
        self._add_queue = add_queue
    
    def run(self):
        while True:
            # Dequeue data. Makes thread sleep if no data
            rec = self._rec_queue.get()
                
            res = self._aud.match_recording(rec)
            
            if res["value"] is not None:
                word = res["value"]["label"]
                print(word, end=" ", flush=True)
            else:
                print("???", end=" ", flush=True)
                self._add_queue.put(rec) # send to other thread if no match found
                    
                    

class AudioAddingThread(Thread):
    def __init__(self, aud:AudioDictionary, add_queue):
        Thread.__init__(self, daemon=True)
        self._aud = aud
        self._add_queue = add_queue
    
    def run(self):
        while True:
            # Dequeue data. Makes thread sleep if no data
            rec = self._add_queue.get() 
            
            # User input in the format of "<word>". 
            # If no angle brackets, input for respective word is skipped.
            new_input = input()
            
            if len(new_input) > 0:
                i = new_input.find("<")
                j = new_input.find(">")
                if i != -1 and j != -1:
                    new_word = new_input[i+1:j]
                    self._aud.add_recording(rec, label=new_word)
                    self._aud.save()

# ----------------------------------------------------------------------

def main():
    aud = AudioDictionary(data_name="words", reset=False)
    rec_queue = Queue()
    add_queue = Queue()
    
    match_thread = AudioMatchingThread(aud, rec_queue, add_queue)
    add_thread = AudioAddingThread(aud,add_queue)
    match_thread.start()
    add_thread.start()
    
    while True:
        recording = record_word() # blocking until audio return
        rec_queue.put(recording)
        
        
        
        

if __name__ == "__main__":
    main()