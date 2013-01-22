#!/usr/bin/env python

import sys
sys.path.append(".")

import os
import datetime
import time
import readline
import calendar

# get environment
if len(sys.argv) == 2:
    os.environ['FLASK_ENV'] = sys.argv[1]

from pprint import pprint

from flask import *

from app.lib import *
from app.models import *
from app.lib.database import db
from app.lib import database, util


os.environ['PYTHONINSPECT'] = 'True'
