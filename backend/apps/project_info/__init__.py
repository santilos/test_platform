# -*- coding: utf-8 -*-
# @Time : 2022/2/10 18:15
# @Author : chenxu.tian
# @Email : chenxu.tian@horizon.ai
# @File : __init__.py.py
# @Project : test_platform
# @Description : project info model
from sanic.blueprints import Blueprint

# 不可使用驼峰写法
from settings import API_VERSION

PATH = '/project_info'
NAME = 'project_info'
project_info = Blueprint(NAME, PATH, version=API_VERSION[0])
