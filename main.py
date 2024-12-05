from kivy.uix.actionbar import partial
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.uix.filechooser import FileChooserListView
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from kivy.clock import Clock

# either mutagen doesnt work here or I am doing something wrong, anyway pygame does the job fine
import pygame
pygame.init()
pygame.mixer.init()
import os
current_path = os.path.dirname(os.path.realpath(__file__))


class Song_Widget(GridLayout):
    def pass_info(self, name, caller):
        self.ids.song_name.text = name.split("/")[-1]
        if name.endswith(".mp3"):
            self.ids.song_time.text = str(round(MP3(name).info.length, 2)) + "s"
            self.song_time = str(round(MP3(name).info.length, 2))
        else:
            self.ids.song_time.text = str(round(WAVE(name).info.length, 2)) + "s"
            self.song_time = str(round(WAVE(name).info.length, 2))
        self.song_name = name.split("/")[-1]
        self.song_path = name
        self.caller = caller
    
    def remove(self):
        self.parent.remove_widget(self)
        self.caller.ids.playlist.height -= 50
        if self.caller.playList == [] or self.caller.playList[self.caller.current_song] == self.song_path:
            Clock.unschedule(self.caller.update_time)
            self.caller.stopped_time = 0
            pygame.mixer.music.stop()
            self.caller.ids.play_stop.text = "Play"
            self.caller.ids.play_stop.background_color = [0,1,0,1]
            self.caller.ids.now_playing.text = "Select a song to play"
            self.caller.ids.time_playing.text = ""
        self.caller.playList.remove(self.song_path)

    def play(self):
        self.caller.play(self.song_path)

class AddPopup(Popup):
    def pass_info(self, caller):
        self.ids.filechooser.path = current_path
        self.caller = caller
    def add_song(self):
        if self.ids.filechooser.selection != []:
            i = 0 # this is just to prevent a bug that would change the labes text even though there are no songs added
            if os.path.isfile(self.ids.filechooser.selection[0]): # checking if the thing selected is a file or a directory
                self.caller.playList.append(self.ids.filechooser.selection[0])
                wid = Song_Widget()
                wid.pass_info(self.ids.filechooser.selection[0], self.caller)
                self.caller.ids.playlist.add_widget(wid)
                self.caller.ids.playlist.height += 50
                i = 1
            else:
                for k in os.listdir(self.ids.filechooser.selection[0]):
                    if k.endswith(".mp3") or k.endswith(".wav"):
                        file_path = self.ids.filechooser.selection[0] + "/" + k
                        self.caller.playList.append(file_path)
                        wid = Song_Widget()
                        wid.pass_info(file_path, self.caller)
                        self.caller.ids.playlist.add_widget(wid)
                        self.caller.ids.playlist.height += 50
                        i = 1
            if i == 1:
                self.caller.ids.Scroll_text_label.clear_widgets()
                self.caller.ids.Scroll_text_label.cols = 3
                self.caller.ids.Scroll_text_label.add_widget(Label(text="Song Name", color=[0,0,1,1]))
                self.caller.ids.Scroll_text_label.add_widget(Label(text="Duration", color=[0,0,1,1]))
                self.caller.ids.Scroll_text_label.add_widget(Label(text="Controls", color=[0,0,1,1]))
        self.dismiss()

class MainGrid(GridLayout):

    def add(self):
        popup = AddPopup()
        popup.pass_info(self)
        popup.open()

    def play_stop(self):
        if self.playList != []:
            if self.ids.play_stop.text == "Play" or self.ids.play_stop.text == "Resume":
                self.ids.play_stop.text = "Stop"
                self.ids.play_stop.background_color = [1,0,0,1]
                self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
                if self.playList[self.current_song].endswith(".mp3"):
                    self.ids.time_playing.text = str(round(MP3(self.playList[self.current_song]).info.length, 2)) + "s"
                else:
                    self.ids.time_playing.text = str(round(WAVE(self.playList[self.current_song]).info.length, 2)) + "s"
                if self.stopped_time != 0:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.load(self.playList[0])
                if pygame.mixer.music.get_busy() == False:
                    pygame.mixer.music.play()
                Clock.schedule_interval(self.update_time, 1)
            else:
                self.ids.play_stop.text = "Resume"
                self.ids.play_stop.background_color = [0,1,0,1]
                Clock.unschedule(self.update_time)
                pygame.mixer.music.pause()

    def update_time(self, dt):
        self.stopped_time += dt
        if self.stopped_time >= float(self.ids.time_playing.text[:-1]):
            print("changing song")
            self.current_song += 1
            self.stopped_time = 0
            pygame.mixer.music.stop()
            if self.current_song < len(self.playList):
                pygame.mixer.music.load(self.playList[self.current_song])
                pygame.mixer.music.play()
                self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
                if self.playList[self.current_song].endswith(".mp3"):
                    self.ids.time_playing.text = str(round(MP3(self.playList[self.current_song]).info.length, 2)) + "s"
                else:
                    self.ids.time_playing.text = str(round(WAVE(self.playList[self.current_song]).info.length, 2)) + "s"
            else:
                self.current_song = 0
                self.stopped_time = 0
                Clock.unschedule(self.update_time)
                self.ids.play_stop.text = "Play"
                self.ids.play_stop.background_color = [0,1,0,1]
                self.ids.now_playing.text = "You have reached the end of the playlist"
                self.ids.time_playing.text = "Select a song to play"

    def play(self, path):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.stopped_time = 0
        self.current_song = self.playList.index(path)
        Clock.schedule_interval(self.update_time, 1)
        self.ids.play_stop.text = "Stop"
        self.ids.play_stop.background_color = [1,0,0,1]
        self.ids.now_playing.text = path.split("/")[-1]
        if path.endswith(".mp3"):
            self.ids.time_playing.text = str(round(MP3(path).info.length, 2)) + "s"
        else:
            self.ids.time_playing.text = str(round(WAVE(path).info.length, 2)) + "s"

    def previous(self):
        if self.current_song == 0:
            self.current_song = len(self.playList) - 1
        else:
            self.current_song -= 1
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playList[self.current_song])
        pygame.mixer.music.play()
        self.stopped_time = 0
        Clock.schedule_interval(self.update_time, 1)
        self.ids.play_stop.text = "Stop"
        self.ids.play_stop.background_color = [1,0,0,1]
        self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
        if self.playList[self.current_song].endswith(".mp3"):
            self.ids.time_playing.text = str(round(MP3(self.playList[self.current_song]).info.length, 2)) + "s"
        else:
            self.ids.time_playing.text = str(round(WAVE(self.playList[self.current_song]).info.length, 2)) + "s"
        
    def next(self):
        if self.current_song == len(self.playList) - 1:
            self.current_song = 0
        else:
            self.current_song += 1
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playList[self.current_song])
        pygame.mixer.music.play()
        self.stopped_time = 0
        Clock.schedule_interval(self.update_time, 1)
        self.ids.play_stop.text = "Stop"
        self.ids.play_stop.background_color = [1,0,0,1]
        self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
        if self.playList[self.current_song].endswith(".mp3"):
            self.ids.time_playing.text = str(round(MP3(self.playList[self.current_song]).info.length, 2)) + "s"
        else:
            self.ids.time_playing.text = str(round(WAVE(self.playList[self.current_song]).info.length, 2)) + "s"
    
    def rewind(self):
        pygame.mixer.music.set_pos(self.stopped_time - 10)
        self.stopped_time = 0
    
    def forward(self):
        pygame.mixer.music.set_pos(self.stopped_time + 10)
        self.stopped_time += 10

class Music_playerApp(App):
    def build(self):
        return MainGrid()
    
if __name__ == "__main__":
    Music_playerApp().run()