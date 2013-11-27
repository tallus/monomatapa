#!/usr/bin/env python

from flask import Flask

app = Flask(__name__)

from resumemaker import views

