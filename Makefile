rpi-setup:
	python3 -m venv .venv
	source .venv/bin/activate &&\
	pip install -r requirements_rpi.txt

py-setup:
	python3 -m venv .venv
	source .venv/bin/activate &&\
	pip install -r requirements.txt

py-test:
	python3 -m unittest discover -s tibberios/tests

