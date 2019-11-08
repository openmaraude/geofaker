#!/usr/bin/env python

__version__ = '0.1.0'
__doc__ = 'Animate taxis along prerecorded GPS tracks'
__homepage__ = 'https://github.com/openmaraude/geofaker'
__author__ = 'Vincent Lara'
__contact__ = 'vincent.lara@data.gouv.fr'

import argparse
import asyncio
import csv
import hashlib
import json
import logging
import random
import socket
import time

import gpxpy


MOVE_DELAY = 5

logger = logging.getLogger(__name__)


class Geotaxi:
    """Wrapper around geotaxi UDP socket."""

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (host, port)

    def send(self, data):
        r = self.sock.sendto(data, self.addr)


async def move_taxi(taxi, gpx, geotaxi):
    while True:
        # Follow random track
        trace = gpx.tracks[random.randrange(0, len(gpx.tracks))]
        for segment in trace.segments:
            for point in segment.points:
                unix_timestamp = int(time.time())
                payload = {
                    'timestamp': str(unix_timestamp),
                    'operator': taxi['operator'],
                    'version': taxi['version'],
                    'lat': str(point.latitude),
                    'lon': str(point.longitude),
                    'device': taxi['device'],
                    'taxi': taxi['taxi'],
                    'status': taxi['status'],
                }

                h = ''.join([payload[key] for key in (
                    'timestamp', 'operator', 'taxi', 'lat', 'lon', 'device', 'status', 'version'
                )])
                h += taxi['apikey']

                payload['hash'] = hashlib.sha1(h.encode('utf8')).hexdigest()

                data = json.dumps(payload)
                logger.debug(
                    'taxi %s: new position lon=%s lat=%s',
                    taxi['taxi'],
                    point.longitude,
                    point.latitude
                )
                geotaxi.send(data.encode('utf8'))

                await asyncio.sleep(MOVE_DELAY)

        logger.debug('taxi %s: track finished, start new track', taxi['taxi'])
        await asyncio.sleep(10 * MOVE_DELAY)


async def animate(taxis, gpx, geotaxi):
    """Update `geotaxi` with `taxis` positions following tracks defined in `gpx`.
    """
    await asyncio.gather(
        *(move_taxi(taxi, gpx, geotaxi) for taxi in taxis)
    )


def parse_taxis_file(taxis_file):
    taxis = []
    with open(taxis_file) as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True, delimiter=',', quoting=csv.QUOTE_NONE)

        for row in reader:
            taxis.append({
                'operator': row[0],
                'version': row[1],
                'taxi': row[2],
                'status': row[5],
                'device': row[6],
                'apikey':row[8]
            })
    return taxis


def parse_gpx_file(tracks_file):
    with open(tracks_file) as handle:
        return gpxpy.parse(handle)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('taxis_file', help='taxis.csv file')
    parser.add_argument('tracks_file', help='tracks.gpx file')
    parser.add_argument('--geotaxi-addr', required=True)
    parser.add_argument('--geotaxi-port', default=8080, type=int)
    args = parser.parse_args()

    geotaxi = Geotaxi(args.geotaxi_addr, args.geotaxi_port)

    taxis = parse_taxis_file(args.taxis_file)
    gpx = parse_gpx_file(args.tracks_file)

    asyncio.run(animate(taxis, gpx, geotaxi))


if __name__ == '__main__':
    main()
