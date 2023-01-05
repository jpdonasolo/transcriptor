import tkinter as tk

from utils import *    
from AudioController import AudioController


class BaseEditorWindow(tk.Toplevel):
    def __init__(self, master, transcript_path):
        tk.Toplevel.__init__(self, master)
        self.transcript_path = transcript_path
        self.transcript = read_transcript(transcript_path)

    def setup(self):
        # Screen config
        self.title("Transcript")
        self.geometry("500x400")
        self.resizable(False, False)

        # Protocols
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Bindings
        self.bind("<Control-e>", lambda e: self._on_closing())

        # Entry
        self.entry = tk.Entry(self)
        self.entry.pack(anchor=tk.S, fill=tk.X, padx=10, pady=10)
        
        # Initial labels
        self.text_frame = tk.LabelFrame(self)
        self.text_frame.pack(anchor=tk.N, fill=tk.BOTH, padx=10, pady=10)        
        self._pack_labels()
    
    def _pack_labels(self):
        # Pack the sentences and highlight the current one
        for sentence_idx in range(10):
            start_timestamp, _, sentence, been_modified = self.transcript[sentence_idx]
            bold = sentence_idx == 0
            self._pack_label(start_timestamp, sentence, been_modified, bold)

    def _pack_label(self, start_timestamp, sentence, been_modified, bold):
        timestamp = f"[{seconds_to_minutes_and_seconds(start_timestamp)}]"
        tk.Label(
                self.text_frame, 
                text=timestamp + sentence,
                bg="red" if been_modified else None,
                wraplength=450,
                anchor=tk.W,
                font=("Helvetica", 12, "bold") if bold else None
            ).pack(anchor=tk.W)

    def _on_closing(self):        
        self.destroy()

class DynamicEditorWindow(BaseEditorWindow):
    def __init__(self, master, audio_controller: AudioController, transcript_path):
        BaseEditorWindow.__init__(self, master, transcript_path)
        self.player = audio_controller
    
    def setup(self):
        BaseEditorWindow.setup(self)

        # Bindings
        self.bind("<Control-b>", lambda e: self.pause_resume())
        
        # Seek to the next or previous sentence
        self.bind("<Up>", lambda e: self.seek(e))
        self.bind("<Down>", lambda e: self.seek(e))

        # Restart current sentence
        self.bind("<Control-r>", lambda e: self.seek(e))

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

        start_timestamp, *_= self.transcript[new_sentence]
        self.player.set_sentence_and_time(new_sentence, start_timestamp)

    def update(self, curr_sentence: int):
        self._clean_labels()
        self._pack_labels(curr_sentence)
    
    def pause_resume(self):
        self.player.pause_resume()

    def _clean_labels(self):
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        self.text_frame.pack_forget()
        self.text_frame.pack(anchor=tk.N, fill=tk.BOTH, padx=10, pady=10)
    
    def _pack_labels(self, curr_sentence=None):
        if curr_sentence is None:
            BaseEditorWindow._pack_labels(self)
            return
        
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
            start_timestamp, _, sentence, been_modified = self.transcript[sentence_idx]
            bold = sentence_idx == curr_sentence
            self._pack_label(start_timestamp, sentence, been_modified, bold)
    
    def _on_closing(self):
        super()._on_closing()
        self.player._exit()

class Editor(DynamicEditorWindow):
    def __init__(self, master, audio_controller: AudioController, transcript_path):
        DynamicEditorWindow.__init__(self, master, audio_controller, transcript_path)
        self.sentence_being_edited = None

    def setup(self):
        DynamicEditorWindow.setup(self)

        # Bindings
        self.bind("<Control-s>", lambda e: self.save_transcript())
        self.bind("<Control-m>", lambda e: self.modify_sentence())
        self.bind("<Control-d>", lambda e: self.delete_sentence())
        
        # Entry
        self.entry.bind("<Control-Return>", lambda e: self.save_sentence(self.player.curr_sentence))

        self.player.start()
    
    def modify_sentence(self):
        self.sentence_being_edited = self.player.curr_sentence
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.transcript[self.sentence_being_edited][2])
        self.entry.focus_set()

    def delete_sentence(self):
        self.modify_sentence()
        self.entry.delete(0, tk.END)
        self.save_sentence()

    def save_sentence(self):
        if self.sentence_being_edited is None:
            return
        
        sentence = self.entry.get()
        
        self.transcript[self.sentence_being_edited][2] = sentence
        self.transcript[self.sentence_being_edited][3] = True
        self.sentence_being_edited = None

        self.update(self.player.curr_sentence)
        
        self.entry.delete(0, tk.END)
        self.focus_set()

    def save_transcript(self):
        save_transcript(self.transcript, self.transcript_path)
    
    def _on_closing(self):
        self.save_transcript()
        DynamicEditorWindow._on_closing(self)