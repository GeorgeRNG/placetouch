import evdev
import time
import uinput
import threading
import tkinter as tk

touchPad = 0

options = list(map(lambda n: evdev.InputDevice(n), evdev.list_devices()))
optionNames = list(map(lambda n: n.path + ": " + n.name, options))
for (i, device) in enumerate(options):
    if("touchpad" in device.name.lower()):
        touchPad = i


touchHeight = 0
touchWidth = 0

screenHeight = 530
screenWidth = 970

leftBorder = 200
rightBorder = 400
topBorder = 100
bottomBorder = 100

fingerI = 0
x = 0
y = 0
clicking = False

touchPadThread = None

window = tk.Tk()
xText = tk.StringVar()
xText.set("X: -")
yText = tk.StringVar()
yText.set("Y: -")
clickingText = tk.StringVar()
clickingText.set("Clicking: False")
selectedEvent = tk.StringVar()
selectedEvent.set(optionNames[touchPad])
def mainWindow():
    title = tk.Label(text="placetouch")
    title.pack()
    touchpadSelection = tk.OptionMenu(window,selectedEvent,*optionNames)
    touchpadSelection.pack()
    xLabel = tk.Label(textvariable=xText)
    xLabel.pack()
    yLabel = tk.Label(textvariable=yText)
    yLabel.pack()
    clickingLable = tk.Label(textvariable=clickingText)
    clickingLable.pack()
    exitButton = tk.Button(text="Exit",command=exit)
    exitButton.pack()
    window.mainloop()

def touchpad():

    events = (
        uinput.REL_X,
        uinput.REL_Y,
        uinput.BTN_LEFT,
        uinput.BTN_RIGHT,
    )

    with uinput.Device(events) as device:

        time.sleep(1)

        for event in options[touchPad].read_loop():
            get_xy_coords(event,device)

def get_xy_coords(e,device):
    global fingerI
    if e.code == 47: # finger index
        fingerI = e.value

    if e.code == 57: # some touch index thing
        if(e.value == -1):
            fingerI = 0

    if fingerI == 0:
        if e.code == 53:
            global touchWidth
            global x
            x = e.value
            if(e.value > touchWidth):
                touchWidth = e.value
            xText.set("Touch X: " + str(x) + " / " + str(touchWidth))

            pointInTouchPad = (e.value - leftBorder) / (touchWidth - (leftBorder + rightBorder))

            device.emit(uinput.REL_X, -10000)
            device.emit(uinput.REL_X, int(pointInTouchPad * screenWidth))
        if e.code == 54:
            global touchHeight
            global y
            y = e.value
            if(e.value > touchHeight):
                touchHeight = e.value
            yText.set("Touch Y: " + str(y) + " / " + str(touchHeight))

            pointInTouchPad = (e.value - topBorder) / (touchHeight - (topBorder + bottomBorder))

            device.emit(uinput.REL_Y, -10000)
            device.emit(uinput.REL_Y, int(pointInTouchPad * screenHeight))

    if e.code == 272:
        clicking = e.value == 1
        clickingText.set("Clicking: " + str(clicking))
        device.emit(uinput.BTN_LEFT, e.value)

if __name__ == "__main__":
    touchPadThread = threading.Thread(target=touchpad)
    touchPadThread.daemon = True
    touchPadThread.start()
    mainWindow()
