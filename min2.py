import sys, time
import win32gui, win32con, win32api, win32file
import win32gui_struct, winnt

# These device GUIDs are from Ioevent.h in the Windows SDK.  Ideally they
# could be collected somewhere for pywin32...
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


def TestDeviceNotifications():
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = 'test_devicenotify'
    wc.style =  win32con.CS_GLOBALCLASS|win32con.CS_VREDRAW | win32con.CS_HREDRAW
    wc.hbrBackground = win32con.COLOR_WINDOW+1
    wc.lpfnWndProc={win32con.WM_DEVICECHANGE:OnDeviceChange}
    class_atom=win32gui.RegisterClass(wc)
    hwnd = win32gui.CreateWindow(wc.lpszClassName,
        'Testing some devices',
        # no need for it to be visible.
        win32con.WS_CAPTION,
        100,100,900,900, 0, 0, 0, None)

    hdevs = []
    # Watch for all USB device notifications
    filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
                                        GUID_DEVINTERFACE_MONITOR)
    hdev = win32gui.RegisterDeviceNotification(hwnd, filter,
                                               win32con.DEVICE_NOTIFY_WINDOW_HANDLE)
    hdevs.append(hdev)
    # and create handles for all specified directories
    # now start a message pump and wait for messages to be delivered.
    while 1:
        win32gui.PumpWaitingMessages()
        time.sleep(0.01)


if __name__=='__main__':
    # optionally pass device/directory names to watch for notifications.
    # Eg, plug in a USB device - assume it connects as E: - then execute:
    # % win32gui_devicenotify.py E:
    # Then remove and insert the device.
    TestDeviceNotifications()
