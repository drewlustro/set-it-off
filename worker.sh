#!/bin/bash
cd /sites/setitoff
source /sites/envs/setitoff/bin/activate
python ./scripts/run_worker.py playsong > /sites/logs/setitoff-worker-playsong.log
