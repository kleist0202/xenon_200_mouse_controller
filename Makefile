.PHONY: gui gui_dry help

gui:
	python tests/gui_test.py
gui_dry:
	python tests/gui_test.py -d
help:
	python tests/help.py

install:
	chmod +x ./bin/xenon_driver
	cp ./bin/xenon_driver /usr/local/bin/
