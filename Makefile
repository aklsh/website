HUGO ?= hugo
RSYNC ?= rsync
PYTHON ?= python3
HUGO_CACHEDIR ?= $(CURDIR)/.hugo_cache
CONTENT_SOURCE ?= content
CONTENT_BUILD ?= .build
HTML_CONTENT ?= $(CONTENT_BUILD)/mdhtml
GEMTEXT_CONTENT ?= $(CONTENT_BUILD)/mdgemtext

WEB_BUILD ?= public
GEMINI_SOURCE ?= gemini
GEMINI_BUILD ?= public-gemini

WEB_REMOTE ?= aklsh@100.93.74.76
WEB_PATH ?= /home/aklsh/sites/website

# Set these when invoking deploy-gemini/deploy, for example:
# make deploy-gemini GEMINI_REMOTE=aklsh@gemini-host GEMINI_PATH=/home/aklsh/capsule
GEMINI_REMOTE ?= aklsh@100.93.74.76
GEMINI_PATH ?= /home/aklsh/sites/capsule

.PHONY: all build prepare-html prepare-gemtext http gemini deploy deploy-http deploy-gemini clean

all: build

build: http gemini

prepare-html:
	$(PYTHON) scripts/prepare-content.py --target html --source $(CONTENT_SOURCE) --output $(HTML_CONTENT)

prepare-gemtext:
	$(PYTHON) scripts/prepare-content.py --target gemtext --source $(CONTENT_SOURCE) --output $(GEMTEXT_CONTENT)

http:
	$(MAKE) prepare-html
	HUGO_CACHEDIR=$(HUGO_CACHEDIR) $(HUGO) --gc --minify --contentDir $(HTML_CONTENT) --destination $(WEB_BUILD)

gemini:
	$(MAKE) prepare-gemtext
	$(PYTHON) scripts/build-gemini.py --content $(GEMTEXT_CONTENT) --assets $(GEMINI_SOURCE) --output $(GEMINI_BUILD)

deploy: deploy-http deploy-gemini

deploy-http: http
	$(RSYNC) -avz --delete $(WEB_BUILD)/ $(WEB_REMOTE):$(WEB_PATH)/

deploy-gemini: gemini
	@test -n "$(GEMINI_REMOTE)" || (echo "GEMINI_REMOTE is required; refusing to deploy" >&2; exit 1)
	@test -n "$(GEMINI_PATH)" || (echo "GEMINI_PATH is required; refusing to deploy" >&2; exit 1)
	$(RSYNC) -avz --delete $(GEMINI_BUILD)/ $(GEMINI_REMOTE):$(GEMINI_PATH)/

clean:
	rm -rf $(WEB_BUILD) $(GEMINI_BUILD) $(CONTENT_BUILD)
