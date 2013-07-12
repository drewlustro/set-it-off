#!/bin/bash
cd /sites/set-it-off
source /sites/envs/setitoff/bin/activate
gunicorn production:app -b unix:/tmp/setitoff:wq.sock
