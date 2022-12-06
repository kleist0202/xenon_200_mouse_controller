.PHONY: gui gui_dry default

gui:
	python tests/gui_test.py
gui_dry:
	python tests/gui_test.py -d
default:
	python tests/help.py

install:
	chmod +x ./bin/xenon_driver
	cp ./bin/xenon_driver /usr/local/bin/
