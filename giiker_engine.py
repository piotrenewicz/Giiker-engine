from binascii import hexlify
import pygatt
import cube
from os import environ
from sys import platform as _sys_platform

primed = False
linked = False
# I have no easy way of testing the state3D, I'm just gonna hope it works.


#  borrowed from kivy/utils
def _get_platform():
    # On Android sys.platform returns 'linux2', so prefer to check the
    # presence of python-for-android environment variables (ANDROID_ARGUMENT
    # or ANDROID_PRIVATE).
    if 'ANDROID_ARGUMENT' in environ:
        return 'android'
    elif _sys_platform in ('win32', 'cygwin'):
        return 'win'
    elif _sys_platform == 'darwin':
        return 'macosx'
    elif _sys_platform.startswith('linux'):
        return 'linux'
    elif _sys_platform.startswith('freebsd'):
        return 'linux'
    return 'unknown'


platform = _get_platform()


def prime(backend_override=None):
    # for windows use BGAPI
    # for linux use GATTTools as default, allow switching to BGAPI
    global primed
    if not primed:
        global adapter
        if backend_override is not None:
            if backend_override == "BGAPI":
                adapter = pygatt.BGAPIBackend()
            elif backend_override == "GATTTOOL":
                adapter = pygatt.GATTToolBackend()
            else:
                print("Wrong override string!!")
                print("falling back to default setting")
                return prime()
        else:
            if platform == "win":
                adapter = pygatt.BGAPIBackend()
            elif platform == "linux":
                adapter = pygatt.GATTToolBackend()
            elif platform == "android":
                print("BLEBackend support untested!!")
                adapter = pygatt.GATTToolBackend()
            elif platform == "macosx":
                print("BLEBackend support untested!!")
                print("Apple devices are not supported by giiker_engine")
                print(" ")
                print("it will now attempt to function normally")
                adapter = pygatt.GATTToolBackend()
            elif platform == "unknown":
                print("can't recognise the host OS,")
                print("I have no clue if this will work")
                print("giving it a shot anyway")
                adapter = pygatt.GATTToolBackend()
        try:
            adapter.start()
        except:
            raise ConnectionRefusedError
        finally:
            primed = True
    else:
        return "primed already"


def unprime():
    global primed
    if primed:
        global adapter
        adapter.stop()
        primed = False
    else:
        return "not primed"


def scan(timeout=10):
    if primed:
        data = adapter.scan(timeout)
        results = []
        for i, response in enumerate(data):
            results.append({})
            results[i]['name'] = response['name']
            results[i]['MAC'] = response['address']
            results[i]['signal'] = response['rssi']
        return results
    else:
        return "core not primed!!"


def link_start(mac="C5:2D:77:0C:AD:E8", timeout=40):
    if primed:
        global linked
        if not linked:
            global device
            try:
                device = adapter.connect(mac, timeout, pygatt.BLEAddressType.random)
            except:
                raise ConnectionError
            finally:
                linked = True
        else:
            return "core was linked already"
    else:
        return "core not primed!!"


def link_stop():
    global linked
    if linked:
        global device
        device.disconnect()
        linked = False
    else:
        return "no linkage to stop"


def discovery():
    if linked:
        global device
        uuidval = {}
        for key, entry in device.discover_characteristics().items():
            uuidval[entry.handle] = str(entry.uuid)
        return uuidval
    else:
        return "Link missing"


ReadAccess = [3, 5, 7, 11, 14, 18, 33]
WriteAccess = [3, 25, 28, 30]
NotifyAccess = [14, 18, 22, 30]


def refine(data):
    try:
        product = data.decode()
        if not product.isprintable():
            raise UnicodeDecodeError  # this doesn't actually raise anything, just forces to the except block

    except:
        product = hexlify(data).decode()
    return product


def read(handle):
    try:
        data = device.char_read_handle(handle)
        return refine(data)
    except:
        return "Wrong handle {} Use one of {} for ReadAccess".format(handle, ReadAccess)


def write(handle, data):
    if handle in WriteAccess:
        device.char_write_handle(handle, data.encode())
    else:
        return "Wrong handle {} Use one of {} for WriteAccess".format(handle, WriteAccess)


empty_callback = None
data_callback = None
move_callback = None
adv_callback = None


def set_empty_callback(callback):
    global empty_callback
    empty_callback = callback


def set_data_callback(callback):
    global data_callback
    data_callback = callback


def set_move_callback(callback):
    global move_callback
    move_callback = callback


def set_adv_callback(callback):
    global adv_callback
    adv_callback = callback


def set_inst_callback(callback):
    cube.inst_callback = callback


def notify(handle, value):
    if handle == 18:
        statusupdate(value)
    else:
        if adv_callback is not None:
            adv_callback(refine(value))


def statusupdate(value):
    data = refine(value)
    cube.intake(data)
    if empty_callback is not None:
        empty_callback()
    if data_callback is not None:
        data_callback(data)
    if move_callback is not None:
        move_callback(data[32:])


def subscribe(handle=18):
    try:
        device.subscribe(discovery()[handle], callback=notify)
    except:
        return "Wrong handle {} Use one of {} for NotifyAccess".format(handle, NotifyAccess)


def unsubscribe(handle=18):
    try:
        device.unsubscribe(discovery()[handle])
    except:
        return "Wrong handle {} Use one of {} for NotifyAccess".format(handle, NotifyAccess)


def auto_deploy(mac, callback=None, kind=0):
    if callback is not None:
        if kind == 0:
            set_empty_callback(callback)
        if kind == 1:
            set_data_callback(callback)
        if kind == 2:
            set_move_callback(callback)
        if kind == 3:
            set_inst_callback(callback)
    prime()
    link_start(mac)
    subscribe(18)


def auto_reploy():
    unsubscribe(18)
    link_stop()
    unprime()
    set_empty_callback(None)
    set_data_callback(None)
    set_move_callback(None)
    set_adv_callback(None)
    set_inst_callback(None)