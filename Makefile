graphana:
	docker run -d -p 3000:3000 -e "GF_SECURITY_ADMIN_PASSWORD=secret" grafana/grafana

influx:
	influxd -config /usr/local/etc/influxdb.conf

build: clean venv

clean:
	rm -rf venv

venv:
	virtualenv venv
	venv/bin/pip install -r requirements.txt

run:
	./src/manage.py trade