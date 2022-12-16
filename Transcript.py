import os

import threading
from threading import Lock

import tkinter as tk

from utils import *    
from AudioController import AudioController


class Transcript(tk.Toplevel):
    def __init__(self, master, audio_controller: AudioController, transcript_path):

        self.time_nav_mutex = Lock()

        super().__init__(master)
        self.setup(audio_controller, transcript_path)
        
    def setup(self, audio_controller, transcript_path):
        # Vars
        self.is_open = True
        self.current_sentence = 0

        # Screen config
        self.title("Transcript")
        self.geometry("500x400")
        self.resizable(False, False)

        # Set up the audio player and transcript
        self.player = audio_controller
        self.transcript = read_transcript(transcript_path)

        # Protocols
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bindings
        self.bind("<Control-b>", lambda e: self.pause_resume())
        # self.bind("<Control-e>", lambda e: self.on_closing())

        # Seek to the next or previous sentence
        # self.bind("<Up>", lambda e: self.seek(e))
        # self.bind("<Down>", lambda e: self.seek(e))

        # Restart current sentence
        # self.bind("<Control-r>", lambda e: self.seek(e))

        # Entry
        tk.Entry(self).pack(anchor=tk.S, fill=tk.X, padx=10, pady=10)
        
        # Initial labels
        self.text_frame = tk.LabelFrame(self)
        self.clean_labels()
        self.pack_labels()

    def update(self, curr_sentence: int):
        self.clean_labels()
        print("curr_sentence", curr_sentence)
        self.pack_labels(curr_sentence)

    def clean_labels(self):
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        self.text_frame.pack_forget()
        self.text_frame.pack(anchor=tk.N, fill=tk.BOTH, padx=10, pady=10)
    
    def pack_labels(self, curr_sentence=None):
        if curr_sentence is None:
            curr_sentence = 0
        
        # Pack labels for the current, previous and next 5 sentences
        # If current_sentence is less than 5, pack the first 10 sentences
        # If current_sentence is greater than len(transcript) - 5, pack the last 10 sentences
        if curr_sentence < 5:
            start_sentence = 0
            end_sentence = 10
        elif curr_sentence > len(self.transcript) - 5:
            start_sentence = len(self.transcript) - 10
            end_sentence = len(self.transcript)
        else:
            start_sentence = curr_sentence - 5
            end_sentence = curr_sentence + 5

        # Pack the sentences and highlight the current one
        for sentence_idx in range(start_sentence, end_sentence):
            start_timestamp, _, sentence = self.transcript[sentence_idx]
            tk.Label(
                self.text_frame, 
                text=f"[{seconds_to_minutes_and_seconds(start_timestamp)}] {sentence}",
                wraplength=450,
                anchor=tk.W,
                font=("Helvetica", 12, "bold") if sentence_idx == curr_sentence 
                                               else None).pack(anchor=tk.W)

    # def seek(self, event):
    #     self.time_nav_mutex.acquire()

    #     # Seek to the previous, current or next sentence
    #     if event.keysym == "Down":
    #         increment = 1
    #     elif event.keysym == "Up":
    #         increment = -1
    #     elif event.keysym == "r":
    #         increment = 0
    #     else:
    #         self.time_nav_mutex.release()
    #         return

    #     if not 0 <= self.current_sentence + increment < len(self.transcript):
    #         self.time_nav_mutex.release()
    #         return

    #     self.current_sentence += increment

    #     start_timestamp, _, _ = self.transcript[self.current_sentence]
    #     self.player.set_time(int(start_timestamp))

    #     self.clean_labels()
    #     self.pack_labels()

    #     self.time_nav_mutex.release()

    def pause_resume(self):
        self.player.pause_resume()

    def on_closing(self):        
        # Stop player
        self.player.stop()

        # Close window
        self.destroy()
