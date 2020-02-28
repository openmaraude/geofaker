FROM debian

RUN apt-get update && apt-get install -y \
  python3-pip

COPY paris-small.gpx /

COPY . /app
WORKDIR /app

RUN pip3 install .

RUN useradd geofaker
USER geofaker

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
