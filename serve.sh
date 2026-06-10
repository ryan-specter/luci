#!/bin/sh
cd "$(dirname "$0")"
python3 build.py
exec python3 -m http.server 8765 --directory site
