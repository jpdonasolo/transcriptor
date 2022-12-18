import tkinter as tk

from utils import *    
from AudioController import AudioController


class StaticTranscript(tk.Toplevel):
    def __init__(self, master, transcript_path):
        super().__init__(master)
        self.transcript = read_transcript(transcript_path)

    def setup(self):
        # Vars
        self.is_open = True

        # Screen config
        self.title("Transcript")
        self.geometry("500x400")
        self.resizable(False, False)

        # Protocols
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bindings
        self.bind("<Control-e>", lambda e: self.on_closing())

        # Entry
        tk.Entry(self).pack(anchor=tk.S, fill=tk.X, padx=10, pady=10)
        
        # Initial labels
        self.text_frame = tk.LabelFrame(self)
        self.clean_labels()
        self.pack_labels()
    
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

    def clean_labels(self):
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        self.text_frame.pack_forget()
        self.text_frame.pack(anchor=tk.N, fill=tk.BOTH, padx=10, pady=10)

    def on_closing(self):        
        self.destroy()

class Transcript(StaticTranscript):
    def __init__(self, master, audio_controller: AudioController, transcript_path):
        StaticTranscript.__init__(self, master, transcript_path)
        self.player = audio_controller
    
    def setup(self):
        StaticTranscript.setup(self)

        # Bindings
        self.bind("<Control-b>", lambda e: self.pause_resume())
        
        # Seek to the next or previous sentence
        self.bind("<Up>", lambda e: self.seek(e))
        self.bind("<Down>", lambda e: self.seek(e))

        # Restart current sentence
        self.bind("<Control-r>", lambda e: self.seek(e))

    def update(self, curr_sentence: int):
        self.clean_labels()
        self.pack_labels(curr_sentence)

    def seek(self, event):
        curr_sentence = self.player.curr_sentence

        # Seek to the previous, current or next sentence
        if event.keysym == "Down":
            increment = 1
        elif event.keysym == "Up":
            increment = -1
        elif event.keysym == "r":
            increment = 0
        else:
            return

        new_sentence = curr_sentence + increment

        if not 0 <= new_sentence < len(self.transcript):
            return

        start_timestamp, _, _ = self.transcript[new_sentence]
        self.player.set_sentence_and_time(new_sentence, int(start_timestamp))
    
    def pause_resume(self):
        self.player.pause_resume()
    
    def on_closing(self):
        super().on_closing()
        self.player.stop()