from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from kivy.clock import Clock
import random

# either mutagen doesnt work here or I am doing something wrong, anyway pygame does the job fine
import pygame
pygame.init()

import os
current_path = os.path.dirname(os.path.realpath(__file__)) # this is used so that the filechooser popup opens in the current directory


class Song_Widget(GridLayout):
    # this is used to pass the info from the popup to the song widget
    def pass_info(self, name, caller):
        self.ids.song_name.text = name.split("/")[-1]
        if name.endswith(".mp3"):
            minutes, seconds = divmod(round(MP3(name).info.length), 60)
            self.ids.song_time.text = str(minutes) + "m " + str(seconds) + "s"
            self.song_time = str(round(MP3(name).info.length, 2))
        else:
            minutes, seconds = divmod(round(WAVE(name).info.length), 60)
            self.ids.song_time.text = str(minutes) + "m " + str(seconds) + "s"
            self.song_time = str(round(WAVE(name).info.length, 2))
        self.song_name = name.split("/")[-1]
        self.song_path = name
        self.caller = caller
        self.position = len(caller.ids.playlist.children)
        self.ids.song_current_playing.active = True
    
    # this is for the include checkbutton inside the song widget (this decides if the song should be played or not when called by some other function)
    def include_song(self):
        if self.song_path not in self.caller.ignoreList:
            self.caller.ignoreList.append(self.song_path)
        else:
            self.caller.ignoreList.remove(self.song_path)
    
    # this is the logic for the remove button inside the song widget
    def remove(self):
        self.parent.remove_widget(self)
        self.caller.ids.playlist.height -= 50
        if self.caller.playList == [] or self.caller.playList[self.caller.current_song] == self.song_path:
            Clock.unschedule(self.caller.update_time)
            self.caller.stopped_time = 0
            self.caller.ids.time_slider.value = 0
            pygame.mixer.music.stop()
            self.caller.ids.play_stop.text = "Play"
            self.caller.ids.play_stop.background_color = [0,1,0,1]
            self.caller.ids.now_playing.text = "Select a song to play"
            self.caller.ids.time_playing.text = ""
        if self.song_path in self.caller.playList:
            self.caller.playList.remove(self.song_path)

    # this is used to play the song, it is called via the play button inside the song widget
    def play(self):
        self.caller.play(self.song_path, self.position)

# this is a popup for adding song files or directories to the playlist
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

# this is the main app grid
class MainGrid(GridLayout):

    # this is used to open the filechooser popup
    def add(self):
        popup = AddPopup()
        popup.pass_info(self) # no clue if this the most efficient way, however it works
        popup.open()

    # this is used to play and stop music, it is called via the main play/stop button in the middle of the screen
    def play_stop(self):
        if self.playList != []:
            if self.ids.play_stop.text == "Play" or self.ids.play_stop.text == "Resume":
                while self.playList[self.current_song] in self.ignoreList:
                    self.current_song += 1
                    if self.current_song == len(self.playList) and self.repeat_check():
                        self.current_song = 0
                    elif self.current_song == len(self.playList):
                        self.playlist_ended()
                        return
                self.ids.play_stop.text = "Stop"
                self.ids.play_stop.background_color = [1,0,0,1]
                self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
                self.time_playing_text()
                self.ids.time_slider.max = self.music_entire_time
                if self.stopped_time != 0:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.load(self.playList[self.current_song])
                if pygame.mixer.music.get_busy() == False:
                    pygame.mixer.music.play()
                Clock.schedule_interval(self.update_time, 1)
            else:
                self.ids.play_stop.text = "Resume"
                self.ids.play_stop.background_color = [0,1,0,1]
                Clock.unschedule(self.update_time)
                pygame.mixer.music.pause()

    # this is used to update the time slider and time info labels, and also changes a song if it has reached the end
    # it is called once a second
    def update_time(self, dt):
        self.stopped_time += dt
        self.ids.time_slider.value = self.stopped_time
        if self.stopped_time >= self.music_entire_time:
            if self.shuffle_check() and len(self.playList) > 1:
                rand = random.randint(0, len(self.playList) - 1)
                self.current_song = rand
            else:
                self.current_song += 1
                if self.current_song < len(self.playList): # all of these are a bit confusing, because its literally everywhere, but they are all here to prevent the playList to go out of range
                    while self.playList[self.current_song] in self.ignoreList:
                        self.current_song += 1
                        if self.current_song == len(self.playList) and self.repeat_check():
                            self.current_song = 0
                        elif self.current_song == len(self.playList):
                            self.playlist_ended()
                            return
            if self.current_song == len(self.playList) and self.repeat_check():
                self.current_song = 0
                while self.playList[self.current_song] in self.ignoreList:
                    self.current_song += 1
                    if self.current_song == len(self.playList):
                        self.playlist_ended()
                        return
            self.stopped_time = 0
            pygame.mixer.music.stop()
            if self.current_song < len(self.playList):
                pygame.mixer.music.load(self.playList[self.current_song])
                pygame.mixer.music.play()
                self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
                self.time_playing_text()
                self.ids.time_slider.value = 0
                self.ids.time_slider.max = self.music_entire_time
            else:
                self.playlist_ended()
    
    # this is used for showing the duration of the song on the info labels
    def time_playing_text(self):
        if self.playList[self.current_song].endswith(".mp3"):
            minutes, seconds = divmod(round(MP3(self.playList[self.current_song]).info.length), 60)
            self.ids.time_playing.text = str(minutes) + "m " + str(seconds) + "s"
            self.music_entire_time = MP3(self.playList[self.current_song]).info.length
        else:
            minutes, seconds = divmod(round(WAVE(self.playList[self.current_song]).info.length), 60)
            self.ids.time_playing.text = str(minutes) + "m " + str(seconds) + "s"
            self.music_entire_time = WAVE(self.playList[self.current_song]).info.length

    # this is used to play a specific song, it is called via the play button inside the .kv file (inside the song widget)
    def play(self, path, position):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.stopped_time = 0
        self.current_song = position
        Clock.unschedule(self.update_time) # this is to prevent the multiple calls of the update_time function in one second
        Clock.schedule_interval(self.update_time, 1)
        self.ids.play_stop.text = "Stop"
        self.ids.play_stop.background_color = [1,0,0,1]
        self.ids.now_playing.text = path.split("/")[-1]
        self.time_playing_text()
        self.ids.time_slider.value = 0
        self.ids.time_slider.max = self.music_entire_time

    # this is used to stopping the playlist if it has reached the end, and the repeat is not on
    def playlist_ended(self):
        self.current_song = 0
        self.stopped_time = 0
        Clock.unschedule(self.update_time)
        self.ids.play_stop.text = "Play"
        self.ids.play_stop.background_color = [0,1,0,1]
        self.ids.now_playing.text = "You have reached the end of the playlist"
        self.ids.time_playing.text = "Select a song to play"

    # this is used to play the previous song (before the current one), it is called via a button inside the .kv file
    def previous(self):
        if self.playList != []:
            if self.current_song == 0:
                self.current_song = len(self.playList) - 1
            else:
                self.current_song -= 1
                while self.playList[self.current_song] in self.ignoreList:
                    self.current_song -= 1
                    if self.current_song < 0:
                        self.current_song = len(self.playList) - 1
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.playList[self.current_song])
            pygame.mixer.music.play()
            self.stopped_time = 0
            if Clock.get_time() == 0:
                Clock.schedule_interval(self.update_time, 1)
            self.ids.play_stop.text = "Stop"
            self.ids.play_stop.background_color = [1,0,0,1]
            self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
            self.time_playing_text()
        
    # this is used to skip to the next song, it is called via a button inside the .kv file
    # looks complicated, but it has to check all the different conditions and settings
    def next(self):
        if self.playList != []:
            self.current_song += 1
            while self.playList[self.current_song] in self.ignoreList:
                self.current_song += 1
                if self.current_song == len(self.playList) and self.repeat_check():
                    self.current_song = 0
                elif self.current_song == len(self.playList):
                    self.playlist_ended()
                    return
            if self.current_song == len(self.playList) - 1 and self.repeat_check():
                self.current_song = 0
            else:
                pass
            pygame.mixer.music.stop()
            if self.current_song == len(self.playList) - 1 and self.repeat_check() == False:
                self.playlist_ended()
            else:
                pygame.mixer.music.load(self.playList[self.current_song])
                pygame.mixer.music.play()
                if Clock.get_time() == 0: # this is to prevent the update_time function from being called twice a second
                    Clock.schedule_interval(self.update_time, 1)
                self.stopped_time = 0
                self.ids.play_stop.text = "Stop"
                self.ids.play_stop.background_color = [1,0,0,1]
                self.ids.now_playing.text = self.playList[self.current_song].split("/")[-1]
                self.time_playing_text()
                self.ids.time_slider.value = 0
                if self.playList[self.current_song].endswith(".mp3"):
                    self.music_entire_time = MP3(self.playList[self.current_song]).info.length
                else:
                    self.music_entire_time = WAVE(self.playList[self.current_song]).info.length
                self.ids.time_slider.max = self.music_entire_time
    
    # this is used to rewind the song by 10 seconds
    def rewind(self):
        if self.ids.now_playing.text != "Select a song to play":
            pygame.mixer.music.set_pos(self.stopped_time - 10)
            self.stopped_time = 0
    
    # this is used to move the song forward by 10 seconds
    def forward(self):
        if self.ids.now_playing.text != "Select a song to play":
            pygame.mixer.music.set_pos(self.stopped_time + 10)
            self.stopped_time += 10

    # this is used for shuffling the playlist, if this returns true, the next song will be random
    def shuffle_check(self):
        return self.ids.shuffle.active

    # this is used in case the playlist reaches the end to check if it should repeat, if this returns true, the playlist will repeat
    def repeat_check(self):
        return self.ids.repeat.active
    
    # this is used to change the volume of the music, it is called via the volume slider
    def volume(self):
        self.song_volume = self.ids.volume_slider.value
        pygame.mixer.music.set_volume(self.song_volume)

# the main app class
class Music_playerApp(App):
    def build(self):
        return MainGrid()

# opening the app
if __name__ == "__main__":
    Music_playerApp().run()