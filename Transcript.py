import os

import threading
from threading import Lock

import tkinter as tk
from tkinter import messagebox

import vlc

from utils import *    
from AudioPlayer import AudioPlayer


class Transcript(tk.Toplevel):
    def __init__(self, master, audio_path, transcript_path):
        
        self.time_nav_mutex = Lock()

        super().__init__(master)
        try:
            self.setup(audio_path, transcript_path)
        except FileNotFoundError:
            return

        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.start()
        
    def setup(self, audio_path, transcript_path):
        # Vars
        self.is_open = True
        self.current_sentence = 0

        # Screen config
        self.title("Transcript")
        self.geometry("500x400")
        self.resizable(False, False)

        # Set up the audio player and transcript
        try:
            self.raise_for_invalid_path(audio_path)
            self.raise_for_invalid_path(transcript_path)
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Invalid path: '{str(e)}'")
            self.destroy()
            raise
        
        self.player = AudioPlayer(audio_path, transcript_path)
        self.transcript = read_transcript(transcript_path)

        # Protocols
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bindings
        self.bind("<Control-b>", lambda e: self.pause_resume())
        self.bind("<Control-e>", lambda e: self.on_closing())

        # Seek to the next or previous sentence
        self.bind("<Up>", lambda e: self.seek(e))
        self.bind("<Down>", lambda e: self.seek(e))

        # Restart current sentence
        self.bind("<Control-r>", lambda e: self.restart(e))

        # Entry
        tk.Entry(self).pack(anchor=tk.S, fill=tk.X, padx=10, pady=10)
        
        # Initial labels
        self.text_frame = tk.LabelFrame(self)
        self.clean_labels()
        self.pack_labels()

    def run(self):
        while self.is_open:
            self.time_nav_mutex.acquire()

            current_time = self.player.get_time() / 1000

            _, end_timestamp, _ = self.transcript[self.current_sentence]
            if current_time + 0.1 >= int(end_timestamp):

                self.current_sentence += 1
                self.clean_labels()
                self.pack_labels()

            self.time_nav_mutex.release()

    def clean_labels(self):
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        self.text_frame.pack_forget()
        self.text_frame.pack(anchor=tk.N, fill=tk.BOTH, padx=10, pady=10)
    
    def pack_labels(self):
        # Pack labels for the current, previous and next 5 sentences
        # If current_sentence is less than 5, pack the first 10 sentences
        # If current_sentence is greater than len(transcript) - 5, pack the last 10 sentences
        if self.current_sentence < 5:
            start_sentence = 0
            end_sentence = 10
        elif self.current_sentence > len(self.transcript) - 5:
            start_sentence = len(self.transcript) - 10
            end_sentence = len(self.transcript)
        else:
            start_sentence = self.current_sentence - 5
            end_sentence = self.current_sentence + 5

        # Pack the sentences and highlight the current one
        for sentence_idx in range(start_sentence, end_sentence):
            start_timestamp, _, sentence = self.transcript[sentence_idx]
            tk.Label(
                self.text_frame, 
                text=f"[{seconds_to_minutes_and_seconds(start_timestamp)}] {sentence}",
                wraplength=450,
                anchor=tk.W,
                font=("Helvetica", 12, "bold") if sentence_idx == self.current_sentence 
                                               else None).pack(anchor=tk.W)

    def seek(self, event):
        self.time_nav_mutex.acquire()

        # Seek to the next or previous sentence
        # Down
        if event.keysym == "Down" and self.current_sentence < len(self.transcript) - 1:
            self.current_sentence += 1
        # Up
        elif event.keysym == "Up" and self.current_sentence > 0:
            self.current_sentence -= 1
        # ctrl + r
        elif event.keysym == "r":
            pass
        else:
            raise ValueError("Invalid key")

        start_timestamp, _, _ = self.transcript[self.current_sentence]
        self.player.set_time(int(start_timestamp) * 1000)

        self.clean_labels()
        self.pack_labels()

        self.time_nav_mutex.release()

    def restart(self, event):
        self.seek(event)
        
    def raise_for_invalid_path(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

    def pause_resume(self):
        self.player.pause_resume()

    def on_closing(self):
        # close thread
        self.is_open = False
        self.run_thread.join()
        
        # Stop player
        self.player.stop()

        # Close window
        self.destroy()
