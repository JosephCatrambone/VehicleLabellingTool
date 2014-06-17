VehicleLabellingTool
====================

A tool to serve lots of users with an interface to label positive examples in large images.

Getting Started
===

OSX/Linux
```bash
$ python -m virtualenv env
$ . ./env/bin/activate
$ pip install -r requirements.txt
$ python main.py my/images/folder/*.png
```

Windows
```
> python -m virtualenv env
> env\Scripts\activate
> pip install -r requirements.txt
> python main.py path\to\my\images\*.png
```

TODO
===
- Undo + Delete Function
- Add user credentials to server to see who is contributing.
- Fix bug with scaled canvas.  Canvas is displaying at 4x and is reporting back positions at that scale.  Perhaps the full bounding box should be sent to client and client should send back a pair of numbers in [0,1].
