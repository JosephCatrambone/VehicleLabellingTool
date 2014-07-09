from __future__ import division
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
IMAGE_CACHE = dict();
BASE_PATH = sys.argv[1];
PATCH_SIZE = (128,128);
DB_NAME = 'vehicles.db';
CONSENSUS_THRESHOLD = 1; # Only one person needs to work on a patch before it's accepted.
# Connection and image set are migrated to the lobal store 'g'.  Should do the same with `image_set = list();`

# Routes
@app.route("/")
@app.route("/index.html")
def index():
	return render_template('index.html')

# Ajax Calls
@app.route("/get_work") #, methods=['GET'])
def get_work():
	# Select an image from our images at random.
	global IMAGE_CACHE
	db = get_db();
	c = db.cursor();
	c.execute("SELECT id, filename, x, y FROM work_pool WHERE submissions < {}".format(CONSENSUS_THRESHOLD));
	patch_id, img_filename, x, y = c.fetchone();
	if img_filename not in IMAGE_CACHE: # Have we loaded this picture already?
		print("Loading image {} into cache.".format(img_filename));
		IMAGE_CACHE[img_filename] = Image.open(os.path.join(BASE_PATH, img_filename));
	img_data = IMAGE_CACHE[img_filename];
	crop_data = img_data.crop(box=(x, y, x+PATCH_SIZE[0], y+PATCH_SIZE[1]));
	points = list();
	for entry in c.execute("SELECT x, y, x_forward, y_forward FROM vehicles WHERE x > ? AND y > ? AND x < ? AND y < ? AND image=?", (x, y, x+PATCH_SIZE[0], y+PATCH_SIZE[1], img_filename)):
		transform = {'x': (entry[0]-x)/PATCH_SIZE[0], 'y': (entry[1]-y)/PATCH_SIZE[1]};
		forward = {'x': (entry[2]-x)/PATCH_SIZE[0], 'y': (entry[3]-y)/PATCH_SIZE[1]};
		points.append({'transform':transform, 'forward':forward});
	content = {'filename':img_filename, 'offset_x':x, 'offset_y':y, 'patch_id':patch_id, 'data':encode_img_as_base64_png(crop_data), 'points':points};
	c.close();
	return Response(json.dumps(content), mimetype="application/json");

@app.route("/submit_result", methods=['POST'])
def submit_result():
	data = json.loads(request.form['json']);
	db = get_db();
	cursor = db.cursor();
	cursor.execute("UPDATE work_pool SET submissions = submissions+1 WHERE id=?", (data['patch_id'], ));
	# c.executemany('INSERT INTO vehicles (image, x, y) VALUES (?,?,?)', data)
	for point in data['points']:
		cursor.execute('INSERT INTO vehicles (image, x, y, x_forward, y_forward) VALUES (?, ?, ?, ?, ?)', 
			(data['filename'], 
			data['x_offset']+(PATCH_SIZE[0]*point['transform']['x']), 
			data['y_offset']+(PATCH_SIZE[1]*point['transform']['y']), 
			data['x_offset']+(PATCH_SIZE[0]*point['forward']['x']), 
			data['y_offset']+(PATCH_SIZE[1]*point['forward']['y']),)
		);
	db.commit();
	cursor.close();
	return Response(json.dumps({'status':'okay'}), mimetype="application/json");
	
# DB Access and Init Functions	
def init_db():
	connection = sqlite3.connect(DB_NAME);
	connection.row_factory = sqlite3.Row;
	c = connection.cursor();
	c.execute("CREATE TABLE work_pool (id INTEGER PRIMARY KEY, filename TEXT, x NUMERIC, y NUMERIC, submissions NUMERIC)");
	c.execute("CREATE TABLE vehicles (id INTEGER PRIMARY KEY, image TEXT, x NUMERIC, y NUMERIC, x_forward NUMERIC, y_forward NUMERIC, submitter TEXT)");
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
	try:
		init_db();
		print("Created database file {}".format(DB_NAME));
	except sqlite3.OperationalError as oe:
		pass
	app.run(debug=True, host='0.0.0.0', port=5000);
