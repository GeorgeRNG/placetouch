import evdev
import time
import uinput
import threading
import tkinter as tk
import configuration

touchPad = 0

options = list(map(lambda n: evdev.InputDevice(n), evdev.list_devices()))
optionNames = list(map(lambda n: n.path + ": " + n.name, options))
for (i, device) in enumerate(options):
    if("touchpad" in device.name.lower()):
        touchPad = i

events = (
    uinput.BTN_LEFT,
    uinput.REL_X,
    uinput.REL_Y
)
device = uinput.Device(events)

config = configuration.load()
configuration.save(config)

enabled = True

capabilities = options[touchPad].capabilities()[3]
touchHeight = capabilities[1][1].max
touchWidth = capabilities[0][1].max
# touchHeight = touchWidth = 0

window = tk.Tk()
# window.grid_columnconfigure((0,1))
xText = tk.StringVar()
xText.set("X: -")
yText = tk.StringVar()
yText.set("Y: -")
clickingText = tk.StringVar()
clickingText.set("Clicking: False")
selectedEvent = tk.StringVar()
selectedEvent.set(optionNames[touchPad])
enabledVariable = tk.BooleanVar()
enabledVariable.set(True)
def mainWindow():
    touchpadSelection = tk.OptionMenu(window,selectedEvent,*optionNames)
    touchpadSelection.grid(column=0,row=0,columnspan=2)

    dataFrame = tk.LabelFrame(text="Infomation")
    xLabel = tk.Label(dataFrame,textvariable=xText)
    xLabel.pack()
    yLabel = tk.Label(dataFrame,textvariable=yText)
    yLabel.pack()
    clickingLable = tk.Label(dataFrame,textvariable=clickingText)
    clickingLable.pack()
    dataFrame.grid(column=0,row=1)

    def updateOptions():
        try:
            width = int(screenWidthText.get())
            height = int(screenHeightText.get())

            config['screenWidth'] = width
            config['screenHeight'] = height

            configuration.save(config)
        except:
            screenWidthText.set(str(config['screenWidth']))
            screenHeightText.set(str(config['screenHeight']))

    def tryScreenSize():
        try:
            global canTrustCursor
            enabledVariable.set(False)
            updateEnabled()

            width = int(screenWidthText.get())
            height = int(screenHeightText.get())

            canTrustCursor = False
            moveTo(width,height)
        except ValueError:
            print("couldn't parse integers")

    def updateEnabled():
        global enabled
        enabled = enabledVariable.get()
        device.emit(uinput.BTN_LEFT, 0)


    optionFrame = tk.LabelFrame(text="Options")
    optionFrame.grid_columnconfigure((0,1), weight=1)
    tk.Label(optionFrame,text="Screen Width").grid(row=0,column=0)
    screenWidthText = tk.StringVar()
    screenWidthText.set(str(config['screenWidth']))
    tk.Entry(optionFrame,textvariable=screenWidthText).grid(row=0,column=1)

    tk.Label(optionFrame,text="Screen Height").grid(row=1,column=0)
    screenHeightText = tk.StringVar()
    screenHeightText.set(str(config['screenHeight']))
    tk.Entry(optionFrame,textvariable=screenHeightText).grid(row=1,column=1)

    tk.Button(optionFrame,text="Update Options",command=updateOptions).grid(row=2,column=0)
    tk.Button(optionFrame,text="Check Screen Size",command=tryScreenSize).grid(row=2,column=1)
    optionFrame.grid(column=1,row=1)

    enabledSwitch = tk.Checkbutton(text="Enabled",variable=enabledVariable,command=updateEnabled)
    enabledSwitch.grid(column=0,row=3)

    exitButton = tk.Button(text="Exit",command=exit)
    exitButton.grid(column=1,row=3)
    window.mainloop()

def touchpad():
    global enabled, device

    time.sleep(0.1)

    for event in options[touchPad].read_loop():
        if enabled:
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

            cursorX = int(stretch(e.value / touchWidth, config['leftBorder'], config['rightBorder']) * config['screenWidth'])
        if e.code == 54:
            global touchHeight, y
            y = e.value
            if(e.value > touchHeight):
                touchHeight = e.value
            yText.set("Touch Y: " + str(y) + " / " + str(touchHeight))

            cursorY = int(stretch(e.value / touchHeight, config['topBorder'], config['bottomBorder']) * config['screenHeight'])

    moveTo(cursorX, cursorY)

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
def moveTo(x, y):
    global cursorX, cursorY, lastCursorX, lastCursorY, canTrustCursor

    cursorX = x
    cursorY = y

    if(x >= config['screenWidth'] or y >= config['screenHeight']):
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
