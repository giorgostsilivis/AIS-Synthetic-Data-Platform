# -*- coding: utf-8 -*-
__version__ = '0.1'
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
app = Flask('project')
app.config['SECRET_KEY'] = 'random'
app.config['UPLOAD_FOLDER'] = 'project/static'
app.config['MAX_CONTENT_PATH'] = 2000000

# added
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
#
app.debug = True
toolbar = DebugToolbarExtension(app)
from project.controllers import *
