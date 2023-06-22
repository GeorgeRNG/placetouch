# placetouch
Python script for wayland to make your touchpad static.  
This means, whereever you touch on your touchpad, your mouse will go.  
Touch the bottom right, your mouse will go to the bottom right. The middle? ditto.

## Install
This was made and tested on ubuntu desktop 23.04  
Install all the dependencies:  
`sudo apt install git python3 python3-evdev python3-uinput python3-tk`  
Then clone the repository:  
`git clone https://github.com/GeorgeRNG/placetouch`  

## Use
Open the folder in a terminal, and run  
`sudo python3 main.py`  
Disable your touchpad in settings. 