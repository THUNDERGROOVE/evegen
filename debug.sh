#!/bin/bash

mkdir debug
cd debug && ../configure CPPFLAGS=-DDEBUG CXXFLAGS="-g -O0" && make
