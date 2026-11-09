FROM ghcr.io/mbrubeck/agate:3.3

COPY public-gemini/ /gmi/

ENTRYPOINT ["agate", "--addr", "0.0.0.0:1965", "--content", "/gmi/", "--certs", "/certs/store/", "--hostname", "gemini.aklsh.me"]
