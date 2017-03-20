from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys, time
import win32gui, win32con, win32api, win32file
import win32gui_struct, winnt

import systray_rc

GUID_DEVINTERFACE_MONITOR = "{E6F07B5F-EE97-4a90-B076-33F57BF4EAA7}"

# WM_DEVICECHANGE message handler.
class Foo(QObject):

    changed = pyqtSignal(str)

    def OnDeviceChange(self, hwnd, msg, wp, lp):
        # Unpack the 'lp' into the appropriate DEV_BROADCAST_* structure,
        # using the self-identifying data inside the DEV_BROADCAST_HDR.
        info = win32gui_struct.UnpackDEV_BROADCAST(lp)
        #self.changed.emit('foo')
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

    def __init__(self):
        super().__init__()
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = 'test_devicenotify'
        wc.style =  win32con.CS_GLOBALCLASS|win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hbrBackground = win32con.COLOR_WINDOW+1
        wc.lpfnWndProc={win32con.WM_DEVICECHANGE:self.OnDeviceChange}
        class_atom=win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(wc.lpszClassName,
            'Waiting for Monitor Change',
            # no need for it to be visible.
            win32con.WS_CAPTION,
            100,100,900,900, 0, 0, 0, None)

        filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
                                            GUID_DEVINTERFACE_MONITOR)
        hdev = win32gui.RegisterDeviceNotification(hwnd, filter,
                                                   win32con.DEVICE_NOTIFY_WINDOW_HANDLE)
    def run(self):
        while True:
            time.sleep(0.1)
            win32gui.PumpWaitingMessages()

    # def __init__(self):
    #     message_map = {
    #       win32con.WM_DEVICECHANGE : self.onDeviceChange
    #     }
    #
    #     wc = win32gui.WNDCLASS ()
    #     hinst = wc.hInstance = win32api.GetModuleHandle (None)
    #     wc.lpszClassName = "DeviceChangeDemo"
    #     wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
    #     wc.hCursor = win32gui.LoadCursor (0, win32con.IDC_ARROW)
    #     wc.hbrBackground = win32con.COLOR_WINDOW
    #     wc.lpfnWndProc = message_map
    #     classAtom = win32gui.RegisterClass (wc)
    #     style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
    #     self.hwnd = win32gui.CreateWindow (
    #       classAtom,
    #       "Device Change Demo",
    #       style,
    #       0, 0,
    #       win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
    #       0, 0,
    #       hinst, None
    #     )
    #     filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
    #                                         GUID_DEVINTERFACE_MONITOR)
    #     hdev = win32gui.RegisterDeviceNotification(self.hwnd, filter,
    #                                                win32con.DEVICE_NOTIFY_WINDOW_HANDLE)

f=Foo()
f.run()
