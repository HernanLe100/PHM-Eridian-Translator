# audio_visualizer.py - Hernan Le

# This module contains functions for playing back the audio from audio_analyzer.py 
# and graphing the data.
# ----------------------------------------------------------------------

import sounddevice as sd
import numpy as np
import threading
import math

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

import audio_analyzer as aud
from audio_analyzer import SAMPLE_RATE, FRAME_LEN

# ----------------------------------------------------------------------

# thread to play audio recording produced by aud.record()
# and display graphs if provided 
# LIKELY TO CHANGE IN FUTURE
class AudioPlayThread(threading.Thread):
    def __init__(self, rec, t_sldr= None, f_sldr=None):
        threading.Thread.__init__(self)
        self._recorded_data = rec
        self._time_slider = t_sldr
        self._freq_slider = f_sldr
        self._rd_index = 0
        
    def run(self):
        def callback(outdata, frames, time, status):
            outdata[:] = self._recorded_data[self._rd_index]
            self._rd_index += 1
            if self._time_slider:
                self._time_slider.set_val(self._rd_index * FRAME_LEN / SAMPLE_RATE)
            if self._freq_slider:
                self._freq_slider.set_val(self._rd_index)
        
        with sd.OutputStream(samplerate=SAMPLE_RATE, blocksize=FRAME_LEN, channels=1, callback=callback , latency="low") as stream:
            # WIP 
            while self._rd_index < len(self._recorded_data):
                sd.sleep(math.ceil(1000 * len(np.array(self._recorded_data).flatten())/SAMPLE_RATE))
                
                print("go") # debugging code
            print("end")

# ----------------------------------------------------------------------

# Creates a graph plotting time_axis on x and recording on y
# Returns the figure and time slider 
def create_time_graph(time_axis: list, recording:list):
    RECORDING_TIME = len(recording)/SAMPLE_RATE
    
    MAX_AMP = np.max(recording)
    MIN_AMP = np.min(recording)
    if abs(MIN_AMP) > MAX_AMP:
        MAX_AMP = abs(MIN_AMP)
    
    figure, axis = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    line, = axis.plot(time_axis, recording)
    vert_line,  = axis.plot([0,0], [-MAX_AMP,MAX_AMP])
    
    axis_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
    slider = Slider(axis_slider, "Time", 0, RECORDING_TIME, valstep=0.01)
    slider.set_val(0)
    
    def update(val):
        vert_line.set_xdata([val,val])
        figure.canvas.draw_idle()

    slider.on_changed(update)
    # need to return and store in main so garbage collector does not remove
    return figure, slider 


# Creates a graph plotting frequencies on x and freq_magnitudes on y
# Returns the figure and frame slider 
def create_freq_graph(frequencies: list, freq_magnitudes:list):
    NUM_FRAMES = len(freq_magnitudes)
    LARGEST_FREQ_MAG = float( np.max( np.array(freq_magnitudes).flatten()) )
    
    figure, axis = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    line, = axis.plot(frequencies, freq_magnitudes[0])
    axis.set_xlim(0, 1000) 
    axis.set_ylim(0, LARGEST_FREQ_MAG)
    
    axis_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
    slider = Slider(axis_slider, "Frame", 0, NUM_FRAMES-1, valstep=1)
    slider.set_val(0)
    
    def update(val):
        line.set_ydata(freq_magnitudes[val])
        figure.canvas.draw_idle()

    slider.on_changed(update)
    return figure, slider

# Shows all active figures of plt
def show_graphs():
    plt.show()

# Spawns an AudioPlayThread and runs it
# LIKELY TO CHANGE IN FUTURE
def play(recorded_data: list, t_sldr=None, f_sldr=None):
    audio = AudioPlayThread(recorded_data, t_sldr=t_sldr, f_sldr=f_sldr)
    audio.start()
        
# ----------------------------------------------------------------------

def main():
    recorded_data = aud.record()
    if len(recorded_data) == 0:
        return
    
    time_axis, recording = aud.time_analysis(recorded_data)
    frequencies, freq_magnitudes = aud.freq_analysis(recorded_data)
    
    time_plot, time_slider = create_time_graph(time_axis, recording)
    freq_plot, freq_slider = create_freq_graph(frequencies, freq_magnitudes)
    
    play(recorded_data, t_sldr=time_slider, f_sldr=freq_slider)
    
    show_graphs()
    

if __name__ == "__main__":
    main()