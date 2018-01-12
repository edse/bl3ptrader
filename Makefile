all: requirements run

pyclean:
	find . -name *.pyc -delete

clean: pyclean
	rm -rf venv

venv: clean
	virtualenv venv

run:
	./src/manage.py migrate
	./src/manage.py trade

django:
	./src/manage.py runserver

requirements:
	pip install -r requirements.txt

grafana:
	docker run -d -p 3000:3000 -e "GF_SECURITY_ADMIN_PASSWORD=secret" grafana/grafana:4.6.2

influx:
	influxd -config /usr/local/etc/influxdb.conf

dev: clean venv requirements grafana influx
