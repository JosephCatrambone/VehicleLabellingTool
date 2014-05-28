import sys, os
import sqlite3
import atexit
import base64
import json
from StringIO import StringIO
from glob import glob
from random import randint, choice
from PIL import Image
from flask import Flask, request, g, render_template, Response

# Globals
app = Flask(__name__);
PATCH_SIZE = (128,128);
DB_NAME = 'vehicles.db';
# Connection and image set are migrated to the lobal store 'g'.
#connection = sqlite3.connect('vehicles.db');
#image_set = list();

# Routes
@app.route("/")
@app.route("/index.html")
def index():
	return render_template('index.html')

# Ajax Calls
@app.route("/get_work") #, methods=['GET'])
def get_work():
	# Select an image from our images at random.
	# TODO: FIX THIS CACHING CODE
	#img_filename = choice(g.image_filenames);
	#img_data = None
	#if img_filename not in g.images: # Have we loaded this picture already?
	#	g.images[img_filename] = Image.open(img_filename);
	#	img_data = g.images[img_filename];
	img_filename = choice(glob(sys.argv[1]));
	img_data = Image.open(img_filename);
	x = randint(PATCH_SIZE[0], img_data.size[0]-PATCH_SIZE[0]);
	y = randint(PATCH_SIZE[1], img_data.size[1]-PATCH_SIZE[1]);
	crop_data = img_data.crop(box=(x, y, x+PATCH_SIZE[0], y+PATCH_SIZE[1]));
	content = {'filename':img_filename, 'offset_x':x, 'offset_y':y, 'data':encode_img_as_base64_png(crop_data)};
	return Response(json.dumps(content), mimetype="application/json");

@app.route("/submit_result", methods=['POST'])
def submit_result():
	data = json.loads(request.form['json']);
	db = get_db();
	cursor = db.cursor();
	cursor.execute('INSERT INTO vehicles (image, x, y) VALUES (?, ?, ?)', (data['filename'], data['x_offset']+data['x'], data['y_offset']+data['y']));
	db.commit();
	cursor.close();
	return Response(json.dumps({'status':'okay'}), mimetype="application/json");
	
# DB Access and Init Functions	
def init_db():
	c = connection.cursor();
	c.execute("CREATE TABLE vehicles (id INTEGER PRIMARY KEY, image TEXT, x NUMERIC, y NUMERIC, direction NUMERIC, submitter TEXT)");
	# db = get_db();
	# with app.open_resource('schema.sql', more='r') as f:
	# db.cursor().executescript(f.read());
	# db.commit();
	connection.commit();
	c.close();

def get_db():
	if not hasattr(g, 'db_connection'):
		g.db_connection = sqlite3.connect(DB_NAME);
		g.db_connection.row_factory = sqlite3.Row; # Not necessary, but makes it easier later on.
	return g.db_connection;

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'db_connection'):
		g.db_connection.close();

# Helper functions
def encode_img_as_base64_png(img):
	sout = StringIO();
	img.save(sout, format='PNG');
	contents = sout.getvalue();
	sout.close();
	return base64.b64encode(contents);

if __name__ == "__main__":
	app.run(debug=True);
