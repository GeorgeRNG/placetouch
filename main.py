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

config = configuration.load()
configuration.save(config)

enabled = True

capabilities = options[touchPad].capabilities()[3]
touchHeight = capabilities[1][1].max
touchWidth = capabilities[0][1].max
# touchHeight = touchWidth = 0

absWidth = touchWidth
absHeight = touchHeight

events = (
    uinput.BTN_LEFT,
    uinput.ABS_X + (0, absWidth, 0, 0),
    uinput.ABS_Y + (0, absHeight, 0, 0)
)
device = uinput.Device(events)

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
leftPaddingVariable = tk.DoubleVar()
leftPaddingVariable.set(config['leftBorder'])
rightPaddingVariable = tk.DoubleVar()
rightPaddingVariable.set(config['rightBorder'])
topPaddingVariable = tk.DoubleVar()
topPaddingVariable.set(config['topBorder'])
bottomPaddingVariable = tk.DoubleVar()
bottomPaddingVariable.set(config['bottomBorder'])
imageDownScale = 5
calibrationImage = tk.PhotoImage(width=int(touchWidth / imageDownScale), height=int(touchHeight / imageDownScale))
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
            left = float(leftPaddingVariable.get())
            right = float(rightPaddingVariable.get())
            top = float(topPaddingVariable.get())
            bottom = float(bottomPaddingVariable.get())

            config['leftBorder'] = left
            config['rightBorder'] = right
            config['topBorder'] = top
            config['bottomBorder'] = bottom
        except:
            leftPaddingVariable.set(config['leftBorder'])
            rightPaddingVariable.set(config['rightBorder'])
            topPaddingVariable.set(config['topBorder'])
            bottomPaddingVariable.set(config['bottomBorder'])

        configuration.save(config)


    def updateEnabled():
        global enabled
        enabled = enabledVariable.get()
        device.emit(uinput.BTN_LEFT, 0)

    optionFrame = tk.LabelFrame(text="Options")
    tk.Label(optionFrame,text="Padding should be from 0 to 1. 0 means the left/top of the touchpad").grid(column=0,row=0,columnspan=2)
    tk.Label(optionFrame,text="Left Padding").grid(sticky="E",column=0,row=1)
    leftPaddingEntry = tk.Entry(optionFrame,textvariable=leftPaddingVariable)
    leftPaddingEntry.grid(stick="W",column=1,row=1)
    tk.Label(optionFrame,text="Right Padding").grid(sticky="E",column=0,row=2)
    rightPaddingEntry = tk.Entry(optionFrame,textvariable=rightPaddingVariable)
    rightPaddingEntry.grid(sticky="W",column=1,row=2)
    tk.Label(optionFrame,text="Top Padding").grid(sticky="E",column=0,row=3)
    topPaddingEntry = tk.Entry(optionFrame,textvariable=topPaddingVariable)
    topPaddingEntry.grid(sticky="W",column=1,row=3)
    tk.Label(optionFrame,text="Bottom Padding").grid(sticky="E",column=0,row=4)
    bottomPaddingEntry = tk.Entry(optionFrame,textvariable=bottomPaddingVariable)
    bottomPaddingEntry.grid(sticky="W",column=1,row=4)
    tk.Button(optionFrame,text="Update Options",command=updateOptions).grid(column=0,row=5,columnspan=2)
    optionFrame.grid(column=1,row=1)

    calibrationCanvas = tk.Canvas(height=(touchHeight / imageDownScale), width=(touchWidth / imageDownScale), bg="#000000")
    calibrationCanvas.grid(column=2,row=1)
    calibrationCanvas.create_image(((touchWidth / imageDownScale) / 2, (touchHeight / imageDownScale) / 2), image=calibrationImage, state="normal")

    enabledSwitch = tk.Checkbutton(text="Enabled",variable=enabledVariable,command=updateEnabled)
    enabledSwitch.grid(column=0,row=3)

    exitButton = tk.Button(text="Exit",command=exit)
    exitButton.grid(column=1,row=3)
    window.mainloop()

def touchpad():
    global enabled, device

    time.sleep(0.1)

    for event in options[touchPad].read_loop():
        get_xy_coords(event,device)

cursorX = cursorY = 0
fingerI = x = y = 0
clicking = False
def get_xy_coords(e,device):
    global fingerI, x, y

    if e.code == 47: # finger index
        fingerI = e.value

    if e.code == 57: # some touch index thing
        if(e.value == -1):
            fingerI = 0
            canTrustCursor = False

    if fingerI == 0:
        global cursorX, cursorY
        if e.code == 53:
            global touchWidth
            x = e.value
            if(e.value > touchWidth):
                touchWidth = e.value
            xText.set("Touch X: " + str(x) + " / " + str(touchWidth))

            cursorX = int(stretch(e.value / touchWidth, config['leftBorder'], config['rightBorder']) * absWidth)
        if e.code == 54:
            global touchHeight
            y = e.value
            if(e.value > touchHeight):
                touchHeight = e.value
            yText.set("Touch Y: " + str(y) + " / " + str(touchHeight))

            cursorY = int(stretch(e.value / touchHeight, config['topBorder'], config['bottomBorder']) * absHeight)

    if e.code == 0:
        global lastCursorX, lastCursorY
        calibrationImage.put("#ffffff", (int(x / imageDownScale),int(y / imageDownScale)))
        if lastCursorX != cursorX or lastCursorY != cursorY:
            if enabled:
                moveTo(cursorX, cursorY)
            lastCursorX = cursorX
            lastCursorY = cursorY


    if e.code == 272:
        clicking = e.value == 1
        clickingText.set("Clicking: " + str(clicking))
        if enabled:
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
