#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import shutil
import time
import datetime
import math
import json
import random
import string
# import redis
import urllib
import urllib2
import traceback
from exceptions import Exception

reload(sys)
sys.setdefaultencoding('utf-8')

cur_path = os.path.dirname(__file__)
# sys.path.append(os.path.abspath(os.path.join(cur_path , "../conf/")))

#conf
import rec_conf as conf1

#logging
# import logging
# import logging.config
# log_conf_file = os.path.join(cur_path, '../conf/log.conf')
# logging.config.fileConfig(log_conf_file)
# ilog = logging.getLogger('root')
# ilog_info = logging.getLogger('recinfo')
# ilog_warn = logging.getLogger('recwarn')

import MySQLdb
import MySQLdb.cursors
