#.ONESHELL:
#SHELL:= /bin/bash

# why does this not work with ONESHELL?
SHELL:= /usr/bin/env bash

.PHONY: all clean install

all: .venv/bin/wheel require.pip
	source .venv/bin/activate && \
	pip install --requirement require.pip && \
	pip list

.venv/bin/wheel: .venv/
	source .venv/bin/activate && \
	pip install --upgrade pip setuptools wheel

.venv/:
	python3 -m venv .venv

clean:
	rm -fr .venv/
