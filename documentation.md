#Giiker_engine
is a python module allowing interaction with the ***Xiaomi Mijia Giiker Super Cube***

#Requirements
- Python3.5 (3+ should work, but 3.5 is the only tested)
- binascii 
- pygatt 3.2.0
- numpy 1.11.0  
---
- Windows:  
    -BGAPI compatible Bluetooth adapter, BLED112
- Linux:  
    -any Bluetooth 4.0+ adapter  
        (BGAPI compatible adapters can work, with a prime(override))
- Android:
    - untested as of yet.

#Features
- Bluetooth Low Energy communication layer
    - scan for smartcubes
    - connect to and access data on the cube
    - subscribe to events on the cube (with callbacks)
- Translation of Packet data down to variables
    - 3x3x3 array prepared to access any part of the cube
    - classes for pieces of a rubik's cube.
        - information neccesarry for rendering the cube.  
        with each piece comes it's:
            - permutation
            - orientaion
            - faces
- Shortcut functions for faster debugging.
- Special functions for simplified retrieving and experimenting with ***additional data*.  
     **(data that wasn't reverse engineered and/or implemented into this module)

#Examples
- scan for BLE devices
  ```python
  from giiker_engine import *
  prime() # choose "BGAPI" or "GATTTOOL" or leave empty for auto-selection.
  list = scan() # optional timeout for scanning default is 10sec.
  print(list)

  '''do whatever you need'''

  unprime()
  ```
---
- connect to a giiker
  ```python
  from giiker_engine import *
  prime() # choose "BGAPI" or "GATTTOOL" or leave empty for auto-selection.
  link_start("FF:FF:FF:FF:FF:FF") # your MAC adress goes here. Optional timeout, default is 40sec.

  '''do whatever you need'''

  link_stop()
  unprime()
  ```
---
- get the state of the giiker as data.
  ```python
  from giiker_engine import *
  prime() # choose "BGAPI" or "GATTTOOL" or leave empty for auto-selection.
  link_start("FF:FF:FF:FF:FF:FF") # your MAC adress goes here. Optional timeout, default is 40sec.
  
  state_data = read(18) # 18 is the handle for state data.
  
  '''do whatever you need'''
  
  link_stop()
  unprime()
  ``` 
  
  
#Reference

- Iinitialize the Bluetooth capabilities 
    ```python 
    prime() 
    ```
    it will load a system prefered backend, and init the BT module  
    you can force which backend is loaded with `prime(override)`  
    override can be one of these: `"BGAPI"`, `"GATTTOOL"`.
---
- Release the Bluetooth properly before the end of the program  
    ```python
    unprime()
    ```
    (otherwise it may end up in a bad state, depends on the specific hardware)
---
- Scan any BLE devices and return a list of their names, mac adresses and signal strengths.  
Meant for drawing a selection menu.
    ```python
    scan() / scan(timeout=10)
    ```
---
- connect to the given mac adress  
    ```python
    link_start(mac) / link_start(mac, tineout=40)
    ```
    preferably a giiker cube, although other devices could also be used through this module
---
- disconnect from the cube properly
    ```python
    link_stop()
    ```
---
- assign ***callback function names*** to be called when a *subscribed event* is triggered
    ```python
    set_empty_callback(callback)
    set_data_callback(callback)
    set_move_callback(callback)
    set_adv_callback(callback)
    set_inst_callback(callback)
    ```
    to disable a callback assign it to None ```set_empty_callback(None)```  

    User written functions for receiving these callbacks need to take arguments respectively:  
    - empty_callback
            
        ```python
        def function_name():
        ```
    - data_callback
        ```python
        def function_name(data):
        ```
        #######example data="1234567833333333123456789abc000031334143"
    - move_callback
        ```python
        def function_name(lastmoves):
        ```
        #######example lastmoves="31334143"
    - adv_callback
        ```python
        def function_name(data):
        ```
        #######adv_callback is a special callback for experimenting with *additional data*
    - inst_callback
        ```python
        def function_name(cube_3Darray):
        ```
        #######this callback returns a 3x3x3 array of Piece objects
---
- Subscribe to cube events
    ```python
    subscribe() / subscribe(handle=18)
    ```
---
- Unsubscribe
    ```python
    unsubscribe() / unsubscribe(handle=18)
    ```
---
- Read data from the cube
    ```python
    read(handle)
    ```
    retrieve data just like in *data_callback* from the cube (handle=18).  
    this can also be used for experimenting with *additional data*.  
    handles between 1-33 (with exceptions)
---
- Write data to the cube
    ```python
    write(handle, data)
    ```
    this one is also for experimenting.  
    in file *list of found services* are all the handles and information about them I have found  
    Some of those services have assigned descriptions and permissions like Read Write Notify, to define what can be done with a given handle
---
- Get an up to date service spreadsheet straight from the cube
    ```python
    discovery()
    ```
    I found this very incomplete, but it may become necessary if they change handles.
---
- Set everything up with one command
    ```python
    auto_deploy(mac) / auto_deploy(mac, callback) / auto_deploy(mac, callbcak, kind)
    ```
    use for testing in console, to limit the amout of typing on each iteration.
    
    It will:  
    - ```(mac)```
        ```python
        prime()
        link_start()   
        subscribe(18)
        ```
    - ```(mac, callback)``` will on top of that
        ```python
        set_empty_callback(callback)
        ```
    - ```(mac, callback, kind)``` will redirect which callback to set
        ```python
        kind =
              0 - empty_callback
              1 - data_callback
              2 - move_callback
              3 - inst_callback
        ```
---
- Wrap everything up with one command
    ```python
    auto_reploy()
    ```
    quickest way to exit gracefully
---
- Get the current state of the 3Darray
    ```python
    cube.state3D
    ```
    No getter(), just grab that global var if you need it.
---
- Manually update the 3Darray
    ```python
    cube.intake(data)
    ```
    in case they do change handles, calling this with the data string that used to be on handle 18, will update the state3D accordingly
---
- Easily translate between color names, and side numbers
    ```python
    cube.const.SIDE[side_number] #  return color name
    cube.const.COLOR[color_name] #  return side number
    
    1 - "BLUE"
    2 - "YELLOW"
    3 - "RED"
    4 - "WHITE"
    5 - "PINK"
    6 - "GREEN"
    ```
---