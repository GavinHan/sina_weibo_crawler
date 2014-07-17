#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''

import os
import yaml

base = os.path.dirname(os.path.abspath(__file__))
user_conf = os.path.join(base, 'conf.yaml')

conf_file = open(user_conf)
config = yaml.load(conf_file)

login_list = config['login']

threadNum = config['threadnum']
startUid = config['startUid']

mongo_host = config['mongo']['host']
mongo_port = config['mongo']['port']
db_name = config['db']

instances = config['instances']
mypath = config['mypath']

instance_index = config['instance_index']