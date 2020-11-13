# geofaker

Geofaker is a simple script which takes two parameters:

* a .csv file listing taxis, with the columns `operator, api_version, taxi_id, lat, lon, status, device, hash, operator_api_key`.
* a [.gpx file](https://en.wikipedia.org/wiki/GPS_Exchange_Format) to describe routes.

Then it moves taxis following routes.


## Note

This script is only used with [APITaxi_devel](https://github.com/openmaraude/APITaxi_devel) and on the development platform [dev.api.taxi](https://dev.api.taxi).

It is probably useless, and we should consider removing this component completely.


## Contributions

* paris-small.gpx:

   © OpenStreetMap contributors (the data is available under the Open Database License)
