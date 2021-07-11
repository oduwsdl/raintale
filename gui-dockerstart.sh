#!/bin/bash

redis-server --daemonize yes --save
cd MementoEmbed && waitress-serve --port=5550 --call mementoembed:create_app & 
/app/raintale-gui/start-gui.sh
