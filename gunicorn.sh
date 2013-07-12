#!/bin/bash
cd /sites/set-it-off
source /sites/envs/setitoff/bin/activate
gunicorn production:application -b unix:/tmp/setitoff.sock
