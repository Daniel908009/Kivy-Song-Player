# kivy_music_player
## What is it?
<p>It is a fully resizable multiplatform music player, made in Kivy.</p>
<p>Player can select the individual files or the entire directory with the music files(mp3, wave)</p>
<p>App has a rewind, forward, next, previous buttons, and a scroll menu where the songs are listed.</p>

## Screenshots
![image](https://github.com/user-attachments/assets/5d69b50c-2d47-4498-8f41-62fad39a81de)


## To do
[X] file and directory loading <br>
[X] menu with rewind, forward, next, previous, and stop buttons<br>
[X] scroll menu with all the songs listed<br>
[X] song progress bar
[] volume bar
[] better UI (more colours)<br>
[] changing how the program finds a song in the playList, because currently you can cause an error by deleting some songs and then pushing the play button directly from the list of songs.
[] cleaner code (there is currently a lot of code that repeats everywhere, so I will need to add functions to clear it out)<br>
[X] more functionalities (repeat list in a loop and similar features)<br>
[X] fixing all possible errors (currently you can rewind, even though there are no songs, will fix soon)<br>
<h1>Download instructions</h1>
*Note the links are instructional images <br>
**Note the images used bellow are from a different Github repository, however the overall procces is allways the same. <br>
<h2>Using graphic UI</h2>
<h3>Downloading source code </h3>
First click on the code button as shown in the picture bellow, then click the option Download ZIP <br>
(https://github.com/user-attachments/assets/801a8deb-b6e5-475e-9b6b-262b56fd6a23) <br>
After its downloaded you can find it on your computer through file explorer. After you have found it right click it, it should display option called "Extract" <br>
Click on it and wait a moment. A new directory should appear containing all the files neccesary for the game.<br>
Now open a console and enter the folowing code: pip install -r /path/to/requirements.txt <br>
*Replace the /path/to/requirements.txt with the actual path. <br>
Enjoy! <br>
<h2>Using command prompt</h2>
<h3>Downloading source code </h3>
Open your command prompt and enter the folowing code without the " letters <br>
"https://github.com/Daniel908009/Kivy-Song-Player.git" <br>
This code adress of the site can also be found if you click the code button inside the github repository UI <br>
If you dont have git than first enter the folowing command: sudo apt install git <br>
Now open a console and enter the folowing code: pip install -r /path/to/requirements.txt <br>
*Replace the /path/to/requirements.txt with the actual path. <br>
Enjoy! <br>
<h2>Using Pypi</h2>
simply open your command prompt and enter this command: pip install kivy_music_player_package <br>
then you can run it with this command:  python3 -m kivy_music_player_package.main
