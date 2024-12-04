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

import os
current_path = os.path.dirname(os.path.realpath(__file__))


class Song_Widget(GridLayout):
    def pass_info(self, name, caller):
        self.ids.song_name.text = name.split("/")[-1]
        self.ids.song_time.text = str(round(MP3(name).info.length, 2)) + "s"
        self.song_name = name.split("/")[-1]
        self.song_path = name
        self.song_time = str(round(MP3(name).info.length, 2))
        self.caller = caller
    
    def remove(self):
        self.caller.playList.remove(self.song_path)
        self.parent.remove_widget(self)

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
                        #print(k + " is being addegfdsfsgdddddddddddddddddddddddddddddddddddddddddddddd") # I needed to see it in the terminal between all the kivy stuff
                        #print(file_path)
                        wid.pass_info(file_path, self.caller)
                        self.caller.ids.playlist.add_widget(wid)
                        self.caller.ids.playlist.height += 50
                        i = 1
            if i == 1:
                self.caller.ids.Scroll_text_label.clear_widgets()
                self.caller.ids.Scroll_text_label.cols = 3
                self.caller.ids.Scroll_text_label.add_widget(Label(text="Song Name", color=[0,0,1,1])) # all of these will maybe be done through a specific class later on
                self.caller.ids.Scroll_text_label.add_widget(Label(text="Duration", color=[0,0,1,1])) # the colour theme could later be rechangeable
                self.caller.ids.Scroll_text_label.add_widget(Label(text="Controls", color=[0,0,1,1]))
            print(self.caller.playList)
        self.dismiss()



class MainGrid(GridLayout):
    def add(self):
        popup = AddPopup()
        popup.pass_info(self)
        popup.open()


class Music_playerApp(App):
    def build(self):
        return MainGrid()
    
if __name__ == "__main__":
    Music_playerApp().run()