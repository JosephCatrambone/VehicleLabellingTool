#!/usr/bin/env python
import sys, os
import sqlite3
import csv
from datetime import datetime
from PIL import Image

# WPAFB09 data is in the form x with 'TIME' in the form 21-OCT-09 08.25.17.087000000 PM
# The actual frame times are in the form 20091021202517-01000101-VIS.ntf.r1.img0_jpg8m.raw.jpg

# CSV Data
# id,LATITUDE,LONGITUDE,X,Y,TIME,FRAME_NUMBER,TYPE
# 1,39.771141447642805,-84.09588282166273,9476,7187,21-OCT-09 08.25.17.087000000 PM,100,M

if __name__=="__main__":
	# Create the database
	csv_file = sys.argv[1];
	img_base_path = sys.argv[2];
	db = sqlite3.connect(sys.argv[3]);
	db.row_factory = sqlite3.Row;

	# Insert all vehicles
	image_filenames = set();
	cursor = db.cursor();
	cursor.execute("CREATE TABLE vehicles (id INTEGER PRIMARY KEY, image TEXT, x NUMERIC, y NUMERIC, x_forward NUMERIC, y_forward NUMERIC, submitter TEXT)");
	fin = open(csv_file, 'r');
	cin = csv.DictReader(fin);
	for row in cin:
		timestamp = datetime.strptime(row['TIME'], "%d-%b-%y %I.%M.%S.%f000 %p");
		frame_number = row['FRAME_NUMBER'];
		image_file = "{0}-01000{1:03d}-VIS.ntf.r1.img0_jpg8m.raw.jpg".format(timestamp.strftime('%Y%m%d%H%M%S'), int(frame_number));
		image_filenames.add(image_file);
		cursor.execute('INSERT INTO vehicles (image, x, y, x_forward, y_forward) VALUES (?, ?, ?, ?, ?)', (image_file, row['X'], row['Y'], row['X'], row['Y']));
		print("Inserted ({}, {}, {}) into vehicles.".format(image_file, row['X'], row['Y']));
        db.commit();

	# Create the regions of interest
	REGION_SIZE = 128;
	cursor.execute("CREATE TABLE work_pool (id INTEGER PRIMARY KEY, filename TEXT, x NUMERIC, y NUMERIC, submissions NUMERIC)");
	for image_name in image_filenames:
		try:
			img = Image.open(os.path.join(img_base_path, image_name));
			number_of_channels = len(img.getbands());
			for y in range(0, img.size[1], 32):
				for x in range(0, img.size[0], 32):
					# Make sure there's interesting information in this patch.
					extrema = img.crop((x, y, x+REGION_SIZE, y+REGION_SIZE)).getextrema();
					if number_of_channels == 1:
						if extrema[0] == extrema[1]:
							continue;
					elif number_of_channels == 3:
						if extrema[0][0] == extrema[0][1] and extrema[1][0] == extrema[1][1] and extrema[2][0] == extrema[2][1]:
							continue;
					# This patch is interesting.  Add it.	
					cursor.execute('INSERT INTO work_pool (filename, x, y, submissions) VALUES (?, ?, ?, ?)', (image_name, x, y, 0));
					print('INSERT INTO work_pool (filename, x, y, submissions) VALUES ({}, {}, {}, {})'.format(image_name, x, y, 0));
		except Exception as e:
			print("Exception.  Skipping: {}".format(image_name));
	db.commit();

	# Wrap up
        cursor.close();
