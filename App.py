import tkinter as tk
from tkinter import filedialog

from Transcript import Transcript

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.setup()
        
        self.mainloop()

    def setup(self):
        self.title("Transcript Generator")
        self.geometry("500x200")
        self.resizable(False, False)

        # Vars
        audio_path = tk.StringVar(self)
        transcript_path = tk.StringVar(self)

        # Audio browse menu
        audio_label = tk.Label(self, text="Audio File")
        audio_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        audio_entry = tk.Entry(self, textvariable=audio_path)
        audio_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        audio_button = tk.Button(self, text="Browse",
                command=lambda: audio_path.set(self.ask_file(
                    filetypes=(
                        ("Audio Files", "*.mp3 *.wav *.m4a *.mp4"),
                        ("All Files", "*.*")
                    )
                ))
            )
        audio_button.grid(row=0, column=3, padx=10, pady=10)
            
        # Transcript browse menu
        tcpt_label = tk.Label(self, text="Transcript File")
        tcpt_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        tcpt_entry = tk.Entry(self, textvariable=transcript_path)
        tcpt_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        
        tcpt_button = tk.Button(self, text="Browse",
                command=lambda: transcript_path.set(self.ask_file(
                    filetypes=(
                        ("Text Files", "*.txt"),
                        ("All Files", "*.*")
                    )
                ))
            )
        tcpt_button.grid(row=1, column=3, padx=10, pady=10)

        # Generate transcript button
        gen_tcpt_button = tk.Button(self, text="Generate\nTranscript",
            command=lambda: self.transcript(audio_path.get(), transcript_path.get()))
        gen_tcpt_button.grid(row=2, column=0, padx=10, pady=20)


    def ask_file(self, **kwargs):
        return filedialog.askopenfilename(**kwargs)

    def transcript(self, audio_path, transcript_path):
        Transcript(self, audio_path, transcript_path)

if __name__ == "__main__":
    app = App()
    app.mainloop()
