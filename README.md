VehicleLabellingTool
====================

A tool to serve lots of users with an interface to label positive examples in large images.

Getting Started
===

```bash
$ virtualenv env
$ . ./env/bin/activate
$ pip install -r requirements.txt
$ python main.py my/images/folder/*.png
```

Note: on Windows . ./env/bin/activate might have to be swapped for env\Scripts\activate.bat

TODO
===
- Undo + Delete Function
- Bulk-add (Switch between create/normal every click.)
- Add user credentials to server to see who is contributing.
- Fix bug with scaled canvas.  Canvas is displaying at 4x and is reporting back positions at that scale.  Perhaps the full bounding box should be sent to client and client should send back a pair of numbers in [0,1].
