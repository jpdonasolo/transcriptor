import vlc

from threading import RLock
from threading import Thread

from utils import read_transcript


class Subject:

    def __init__(self, *args, **kwargs):
        self._observers = []

    def notify(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(*args, **kwargs)
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
        
class AudioPlayer:
    def __init__(self, audio_path):
        self.player = vlc.MediaPlayer(audio_path)
        self.time_nav_mutex = RLock()

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
        time = self.player.get_time() / 1000
        self.time_nav_mutex.release()
        return time
    
    def set_time(self, time):
        self.time_nav_mutex.acquire()
        self.player.set_time(time * 1000)
        self.time_nav_mutex.release()
    
    def is_playing(self):
        return self.player.is_playing()

class AudioController(AudioPlayer, Subject):

    def __init__(self, audio_path, transcript_path):
        Subject.__init__(self)
        AudioPlayer.__init__(self, audio_path)

        self.transcript = read_transcript(transcript_path)

        self.curr_sentence_mutex = RLock()
        self._curr_sentence = 0

        self.is_running_mutex = RLock()
        self.is_running = False
        self.thread = None

        self.start()

    @property
    def curr_sentence(self):
        self.curr_sentence_mutex.acquire()
        curr_sentence = self._curr_sentence
        self.curr_sentence_mutex.release()
        return curr_sentence

    @curr_sentence.setter
    def curr_sentence(self, sentence):
        self.curr_sentence_mutex.acquire()
        self._curr_sentence = sentence
        self.curr_sentence_mutex.release()
        self.notify(sentence)
    
    def set_sentence_and_time(self, new_sentence, time):
        self.pause()
        self.set_time(time)
        self.curr_sentence = new_sentence
        self.play()
    
    def start(self):

        self.stop_thread()

        def _run():
            while self.is_running:
                self.time_nav_mutex.acquire()
                time = self.get_time()

                end_timestamp = self.transcript[self.curr_sentence][1]

                if time + .05 >= end_timestamp:
                    self.curr_sentence += 1
                self.time_nav_mutex.release()
        
        self.thread = Thread(target=_run)
        self.start_thread()

    def stop(self):
        self.stop_thread()
        AudioPlayer.stop(self)

    def start_thread(self):
        self.is_running_mutex.acquire()
        self.is_running = True
        self.is_running_mutex.release()
        self.thread.start()

    def stop_thread(self):
        self.is_running_mutex.acquire()
        self.is_running = False
        self.is_running_mutex.release()
        if self.thread:
            self.thread.join()