

import threading

import realtime_audio
from audio_dictionary import AudioDictionary

# ----------------------------------------------------------------------


class AudioAnalysisThread(threading.Thread):
    
    def __init__(self, aud:AudioDictionary, rec, num):
        threading.Thread.__init__(self)
        self._aud = aud
        self._rec = rec
        self._num = num
        
    def run(self):
        res = self._aud.match_recording(self._rec)
        if res["value"] is not None:
            word = res["value"]["label"]
            print(word)
        else:
            new_word = input(">>> unknown: ")
            self._aud.add_recording(self._rec, label=new_word)
            self._aud.save()
            print(new_word)
            #print(self._num)
            
    

# ----------------------------------------------------------------------

def main():
    aud = AudioDictionary(data_name="words", reset=False)
    num = 0
    
    while True:
        recording = realtime_audio.record_word() # blocking until audio return
        translate = AudioAnalysisThread(aud, recording, num)
        translate.start()
        
        num += 1
        
        
        
        

if __name__ == "__main__":
    main()