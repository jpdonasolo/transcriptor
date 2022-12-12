import vlc

from utils import read_transcript

class AudioPlayer:

    def __init__(self, audio_path, transcript_path):
        self.player = vlc.MediaPlayer(audio_path)
        self.transcript = read_transcript(transcript_path)

    def run(self):
        while self.is_open:
            self.time_nav_mutex.acquire()
            self.update_time()
            self.time_nav_mutex.release()

    def pause_resume(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def stop(self):
        self.player.stop()
    
    def pause(self):
        self.player.pause()
    
    def play(self):
        self.player.play()
    
    def get_time(self):
        return self.player.get_time()
    
    def set_time(self, time):
        self.player.set_time(time)
    
    def is_playing(self):
        return self.player.is_playing()