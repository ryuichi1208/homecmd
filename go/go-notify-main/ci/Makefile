.PHONY: build doc fmt lint run test vendor-get

GO ?= go
PREFIX?=/usr/local
INSTALL_BIN=$(PREFIX)/bin/
TEST_TARGETS=./irc ./service ./config ./control ./mockirc ./cmd/tenyksctl ./version ./

default: all

all: test build

force-build: clean build

build:
	$(GO) build -v -o main
