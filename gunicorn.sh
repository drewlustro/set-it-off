#!/bin/bash
cd /sites/setitoff
source /sites/envs/setitoff/bin/activate
gunicorn production:application -b unix:/tmp/setitoff.sock
