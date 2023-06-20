
from evdev import InputDevice
import time
import uinput
#SET THIS TO YOUR DEVICE
touchPad = InputDevice('/dev/input/event6')

touchHeight = 0
touchWidth = 0

screenHeight = 530
screenWidth = 970

doTouchWidthStart = 500
doTouchHeightStart = 500

doTouchWidthEnd = 500
doTouchHeightEnd = 500

def main():
    events = (
        uinput.REL_X,
        uinput.REL_Y,
        uinput.BTN_LEFT,
        uinput.BTN_RIGHT,
    )

    with uinput.Device(events) as device:

        time.sleep(1)

        for event in touchPad.read_loop():
            get_xy_coords(event,device)

def get_xy_coords(e,device):
    if e.code == 53:
        global touchWidth
        if(e.value > touchWidth):
            touchWidth = e.value

        pointInTouchPad = e.value / touchWidth

        device.emit(uinput.REL_X, -10000)
        device.emit(uinput.REL_X, int(pointInTouchPad * screenWidth))
    if e.code == 54:
        global touchHeight
        if(e.value > touchHeight):
            touchHeight = e.value

        device.emit(uinput.REL_Y, -10000)
        device.emit(uinput.REL_Y, int((e.value / touchHeight) * screenHeight))


if __name__ == "__main__":
    main()