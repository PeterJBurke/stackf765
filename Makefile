# StackF765 - regenerate everything from the Python design files.
#   make            build all three boards (schematic, layout, fab files, renders) and the site
#   make verify     run every automated check on the committed files
#   make firmware   build the ArduPilot bootloader and ArduCopter (set ARDUPILOT=/path/to/ardupilot)
PY ?= python3
ARDUPILOT ?= ../ardupilot

all: libs lower service upper site verify

libs:
	$(PY) gen/make_footprints.py
	@echo "3D models: run '$(PY) gen/make_models.py' in an environment with CadQuery if you change them"

lower service upper:
	$(PY) gen/build.py $@ --docs

site:
	$(PY) gen/make_site.py

verify:
	$(PY) tools/verify.py

firmware:
	firmware/build.sh $(ARDUPILOT) copter

.PHONY: all libs lower service upper site verify firmware
