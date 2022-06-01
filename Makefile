.PHONY: gui gui_dry help

gui:
	python tests/gui_test.py
gui_dry:
	python tests/gui_test.py -d
help:
	python tests/help.py
