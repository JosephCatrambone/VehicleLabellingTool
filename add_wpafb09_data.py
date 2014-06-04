#!/usr/bin/env python
import sys, os
import sqlite3
import csv
from datetime import datetime

# WPAFB09 data is in the form x with 'TIME' in the form 21-OCT-09 08.25.17.087000000 PM
# The actual frame times are in the form 20091021202517-01000101-VIS.ntf.r1.img0_jpg8m.raw.jpg

# CSV Data
# id,LATITUDE,LONGITUDE,X,Y,TIME,FRAME_NUMBER,TYPE
# 1,39.771141447642805,-84.09588282166273,9476,7187,21-OCT-09 08.25.17.087000000 PM,100,M

if __name__=="__main__":
	csv_file = sys.argv[1];
	db = sqlite3.connect(sys.argv[2]);
	db.row_factory = sqlite3.Row;
	cursor = db.cursor();
	cursor.execute("CREATE TABLE vehicles (id INTEGER PRIMARY KEY, image TEXT, x NUMERIC, y NUMERIC, x_forward NUMERIC, y_forward NUMERIC, submitter TEXT)");
	fin = open(csv_file, 'r');
	cin = csv.DictReader(fin);
	for row in cin:
		timestamp = datetime.strptime(row['TIME'], "%d-%b-%y %I.%M.%S.%f000 %p");
		frame_number = row['FRAME_NUMBER'];
		image_file = "{0}-01000{1:03d}-VIS.ntf.r1.img0_jpg8m.raw.jpg".format(timestamp.strftime('%Y%m%d%H%M%S'), int(frame_number));
		cursor.execute('INSERT INTO vehicles (image, x, y) VALUES (?, ?, ?)', (image_file, row['X'], row['Y']));
		print("Inserted ({}, {}, {}) into vehicles.".format(image_file, row['X'], row['Y']));
        db.commit();
        cursor.close();
