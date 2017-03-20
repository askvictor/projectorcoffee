import sys
import ctypes.wintypes
from win32con import WM_SETTINGCHANGE, WM_DISPLAYCHANGE
from PyQt5.QtWidgets import QMainWindow, QApplication

import sys, time
import win32gui, win32con, win32api, win32file
import win32gui_struct, winnt

GUID_DEVINTERFACE_MONITOR = "{E6F07B5F-EE97-4a90-B076-33F57BF4EAA7}"

# WM_DEVICECHANGE message handler.
def OnDeviceChange(hwnd, msg, wp, lp):
    # Unpack the 'lp' into the appropriate DEV_BROADCAST_* structure,
    # using the self-identifying data inside the DEV_BROADCAST_HDR.
    info = win32gui_struct.UnpackDEV_BROADCAST(lp)

    # wp will be win32con.DBT_DEVICEQUERYREMOVE when removed and win32con.DBT_DEVICEARRIVAL when connected
    # monitor ID/type is info.name[4:19]

    print("Device change notification:", wp, str(info))  #
    if wp==win32con.DBT_DEVICEQUERYREMOVE and info.devicetype==win32con.DBT_DEVTYP_DEVICEINTERFACE:
        # Our handle is stored away in the structure - just close it
        print("Device being removed - closing handle")
        win32file.CloseHandle(info.handle)
        # and cancel our notifications - if it gets plugged back in we get
        # the same notification and try and close the same handle...
        win32gui.UnregisterDeviceNotification(info.hdevnotify)
    return True

class Example(QMainWindow):
     def __init__(self):
        super().__init__()

        self.initUI()

     def nativeEvent(self, eventType, message):
         msg = ctypes.wintypes.MSG.from_address(message.__int__())
         if eventType == "windows_generic_MSG":
             if msg.message == WM_DISPLAYCHANGE:
                 print("display change")
         return False, 0

     def initUI(self):
        self.statusBar().showMessage('Ready')

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Statusbar')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())