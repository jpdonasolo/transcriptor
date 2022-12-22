import vlc

from threading import Thread, RLock, Event

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

        self.paused_or_resumed = Event()
        self.is_running = Event()

    def pause_resume(self):
        self.paused_or_resumed.set()
        if self.is_running.is_set():
            self.is_running.clear()
            self.player.pause()
        else:
            self.is_running.set()
            self.player.play()

    def exit(self):
        self.player.stop()
    
    def pause(self):
        self.is_running.clear()
        self.player.pause()
    
    def play(self):
        self.is_running.set()
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

class AudioController(AudioPlayer, Subject):

    def __init__(self, audio_path, transcript_path):
        Subject.__init__(self)
        AudioPlayer.__init__(self, audio_path)

        self.transcript = read_transcript(transcript_path)

        self.curr_sentence_mutex = RLock()
        self._curr_sentence = 0

        self.is_thread_alive = False
        self.thread = None

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
        self.paused_or_resumed.set()
        self.pause()
        self.set_time(time)
        self.curr_sentence = new_sentence
        self.play()
    
    def start(self):
        def _run():
            while self.is_thread_alive:
                self.is_running.wait()
                
                time = self.get_time()
                end_timestamp = self.transcript[self.curr_sentence][1]

                if self.paused_or_resumed.wait(end_timestamp - time):
                    self.paused_or_resumed.clear()
                    continue
                self.curr_sentence += 1
        
        self.thread = Thread(target=_run)
        self.start_thread()

    def exit(self):
        self.kill_thread()
        AudioPlayer.exit(self)

    def start_thread(self):
        self.is_thread_alive = True
        self.thread.start()

    def kill_thread(self):
        self.is_thread_alive = False
        self.is_running.set()
        self.paused_or_resumed.set()
        if self.thread:
            self.thread.join()
