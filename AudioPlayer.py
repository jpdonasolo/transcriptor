import vlc

from threading import Lock

from utils import read_transcript


class Subject:

    def __init__(self):
        self._observers = []

    def notify(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(self, *args, **kwargs)
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
        

class AudioPlayer(Subject):

    def __init__(self, audio_path, transcript_path):
        super().__init__()

        self.player = vlc.MediaPlayer(audio_path)
        self.transcript = read_transcript(transcript_path)

        self.time_nav_mutex = Lock()
        self.curr_sentence_mutex = Lock()

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
        self.time_nav_mutex.acquire()
        time = self.player.get_time()
        self.time_nav_mutex.release()
        return time
    
    def set_time(self, time):
        self.time_nav_mutex.acquire()
        self.player.set_time(time)
        self.time_nav_mutex.release()
        self.notify()
    
    def is_playing(self):
        return self.player.is_playing()