#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GeoFaker: animate taxis along prerecorded GPS tracks."""
import sys
import random
import time
import thread
import socket
import csv
import gpxpy
import json
import hashlib

ADDR = ('geoloc.dev.api.taxi', 80)

def animate(taxi_, gpx, udpsock, addr, delay):
    """Animate a single taxi along random tracks."""
    while True:
        trace = gpx.tracks[random.randrange(0, len(gpx.tracks))]
        for segment in trace.segments:
            for point in segment.points:
                unix_timestamp = int(time.time())
                payload={"timestamp":unix_timestamp, "operator": taxi_['operator'],
                         "version": taxi_['version'], "lat": point.latitude,
                         "lon": point.longitude, "device": taxi_['device']}
                concat = "".join(map(lambda k: payload[k], ['timestamp', 'operator',
				'taxi', 'lat', 'lon', 'device', 'status', 'version']))
                concat += taxi_['apikey']
                data['hash'] = str(hashlib.sha1(concat).hexdigest())
                udpsock.sendto(json.dumps(data), addr)
                time.sleep(delay)
        time.sleep(10*delay)

def main(argv):
    """Animate taxis along random tracks."""
    taxisfile = argv[1]
    taxis = []
    gpxfile = argv[2]
    udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(taxisfile, 'rb') as csvfile:
        taxisreader = csv.reader(csvfile, skipinitialspace=True, delimiter=',', \
                quoting=csv.QUOTE_NONE)
        for row in taxisreader:
            if row:
                taxis.append({'operator': row[0], 'version': row[1], \
                        'taxi': row[2], 'status': row[5], 'device': row[6], 'apikey':row[8]})

    with open(gpxfile, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    for taxi in taxis:
        thread.start_new_thread(animate, (taxi, gpx, udpsock, ADDR, 5))

    while 1:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: geofaker.py taxis.csv tracks.gpx"
    else:
        main(sys.argv)
