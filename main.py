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
    uinput.ABS_X + (0, 0xFFFF, 0, 0),
    uinput.ABS_Y + (0, 0xFFFF, 0, 0)
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
        configuration.save(config)


    def updateEnabled():
        global enabled
        enabled = enabledVariable.get()
        device.emit(uinput.BTN_LEFT, 0)


    optionFrame = tk.LabelFrame(text="Options")
    optionFrame.grid_columnconfigure((0,1), weight=1)
   
    tk.Button(optionFrame,text="Update Options",command=updateOptions).grid(row=2,column=0)
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

            cursorX = int(stretch(e.value / touchWidth, config['leftBorder'], config['rightBorder']) * 0xFFFF)
        if e.code == 54:
            global touchHeight, y
            y = e.value
            if(e.value > touchHeight):
                touchHeight = e.value
            yText.set("Touch Y: " + str(y) + " / " + str(touchHeight))

            cursorY = int(stretch(e.value / touchHeight, config['topBorder'], config['bottomBorder']) * 0xFFFF)

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

lastCursorX = lastCursorY = 0
def moveTo(x, y):
    global cursorX, cursorY, lastCursorX, lastCursorY

    cursorX = x
    cursorY = y

    device.emit(uinput.ABS_X, x, syn=False)
    device.emit(uinput.ABS_Y, y)

    lastCursorX = x
    lastCursorY = y
    # device.syn()


if __name__ == "__main__":
    touchPadThread = None
    touchPadThread = threading.Thread(target=touchpad)
    touchPadThread.daemon = True
    touchPadThread.start()
    mainWindow()
