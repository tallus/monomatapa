#!/usr/bin/env python

from flask import render_template, flash, redirect
from flask import Markup 

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

import os.path
from os import getcwd

from resumemaker import app

path = os.path.join(getcwd(), 'resumemaker')
srcpath = os.path.join(path, 'src')

@app.route("/", methods = ['GET', 'POST'])
def index():
    return render_template("static.html", 
        title = "resume", heading = "Paul Munday", 
    contents = Markup("""My Resume will be here..."""))

@app.route("/src")
def source():
    with open(os.path.join(path, 'views.py'), 'r') as f:
        src = f.read()
    code = highlight(src, PythonLexer(), HtmlFormatter())
    css = HtmlFormatter(style="friendly").get_style_defs('.highlight')
    return render_template("static.html", internal_css =  css,
            title = "view the source", heading = "View the Source",
            contents = Markup(code))

@app.route("/about/")
def about():
    with open(os.path.join(srcpath, 'about'), 'r') as f:
        src = f.read()
    return render_template("static.html", 
        title = "about", heading = "About This Website", 
    contents = Markup(src))

@app.route("/colophon/")
def colophon():
    with open(os.path.join(srcpath, 'colophon'), 'r') as f:
        src = f.read()
    return render_template("static.html", 
        title = "colophon", heading = "Colophon", 
    contents = Markup(src))

