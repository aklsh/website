HUGO ?= hugo
RSYNC ?= rsync
PYTHON ?= python3
FLY ?= fly
HUGO_CACHEDIR ?= $(CURDIR)/.hugo_cache
CONTENT ?= content

WEB_BUILD ?= public
GEMINI_BUILD ?= public-gemini

WEB_REMOTE ?= aklsh@100.93.74.76
WEB_PATH ?= /home/aklsh/sites/website

.PHONY: all build http gemini deploy deploy-http deploy-gemini deploy-fly clean

all: build

build: http gemini

http:
	HUGO_CACHEDIR=$(HUGO_CACHEDIR) $(HUGO) --gc --minify --destination $(WEB_BUILD)

gemini:
	$(PYTHON) scripts/build-gemini.py --content $(CONTENT) --output $(GEMINI_BUILD)

deploy: deploy-http deploy-gemini

deploy-http: http
	$(RSYNC) -avz --delete $(WEB_BUILD)/ $(WEB_REMOTE):$(WEB_PATH)/

deploy-gemini: gemini
	$(FLY) deploy --ha=false --depot=false

deploy-fly: deploy-gemini

clean:
	rm -rf $(WEB_BUILD) $(GEMINI_BUILD)
