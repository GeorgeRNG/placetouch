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


capabilities = options[touchPad].capabilities()[3]
touchHeight = capabilities[1][1].max
touchWidth = capabilities[0][1].max
# touchHeight = touchWidth = 0

################# OPTIONS #################
screenHeight = 540
screenWidth = 960

leftBorder = 0.1
rightBorder = 0.9
topBorder = 0.1
bottomBorder = 0.9
################# OPTIONS #################

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
        uinput.BTN_LEFT,
        uinput.REL_X,
        uinput.REL_Y
    )

    with uinput.Device(events) as device:

        time.sleep(0.1)

        for event in options[touchPad].read_loop():
            get_xy_coords(event,device)

cursorX = cursorY = 0
fingerI = x = y = 0
clicking = False
def get_xy_coords(e,device):
    global fingerI
    if e.code == 47: # finger index
        fingerI = e.value

    if e.code == 57: # some touch index thing
        if(e.value == -1):
            fingerI = 0
            canTrustCursor = False

    if fingerI == 0:
        global cursorX, cursorY
        if e.code == 53:
            global touchWidth, x
            x = e.value
            if(e.value > touchWidth):
                touchWidth = e.value
            xText.set("Touch X: " + str(x) + " / " + str(touchWidth))

            cursorX = int(stretch(e.value / touchWidth, leftBorder, rightBorder) * screenWidth)
        if e.code == 54:
            global touchHeight, y
            y = e.value
            if(e.value > touchHeight):
                touchHeight = e.value
            yText.set("Touch Y: " + str(y) + " / " + str(touchHeight))

            cursorY = int(stretch(e.value / touchHeight, topBorder, bottomBorder) * screenHeight)

    moveTo(device, cursorX, cursorY)

    if e.code == 272:
        clicking = e.value == 1
        clickingText.set("Clicking: " + str(clicking))
        device.emit(uinput.BTN_LEFT, e.value)

def stretch(value, start, end):
    if start == end:
        return 0.5

    if start > end:
        start, end = end, start

    if value <= start:
        return 0.0
    elif value >= end:
        return 1.0
    else:
        return (value - start) / (end - start)

canTrustCursor = False
lastCursorX = lastCursorY = 0
def moveTo(device, x, y):
    global screenWidth, screenWidth
    global cursorX, cursorY, lastCursorX, lastCursorY, canTrustCursor

    cursorX = x
    cursorY = y

    if(x >= screenWidth or y >= screenHeight):
        canTrustCursor = False

    if x == 0 or not canTrustCursor:
        print("move to left")
        device.emit(uinput.REL_X, -10000)
    if y == 0 or not canTrustCursor:
        print("move to top")
        device.emit(uinput.REL_Y, -10000)

    if not canTrustCursor:
        print("reset cursor")

        device.emit(uinput.REL_X, x)
        device.emit(uinput.REL_Y, y)

        canTrustCursor = True

    else:
        device.emit(uinput.REL_X, x - lastCursorX)
        device.emit(uinput.REL_Y, y - lastCursorY)

    lastCursorX = x
    lastCursorY = y
    # device.syn()


touchPadThread = None
if __name__ == "__main__":
    touchPadThread = threading.Thread(target=touchpad)
    touchPadThread.daemon = True
    touchPadThread.start()
    mainWindow()
