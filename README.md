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
- Get only sections which are unvisited.
- Fix bug where a new point/forward is created instead of an old one being created.
- Make the user interface more intuitive.  'Add point' should add one to the center, then clicking and dragging should behave as expected.
