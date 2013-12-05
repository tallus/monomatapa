#!/usr/bin/env python

from flask import render_template, flash, redirect
from flask import Markup 

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import RstLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

import os.path
from os import getcwd

import markdown

from resumemaker import app

path = os.path.join(getcwd(), 'resumemaker')
srcpath = os.path.join(path, 'src')

def render_markdown(file):
    '''Return (trusted) markdown file rendered as html.'''
    with open(file, 'r') as f:
        return markdown.markdown(f.read())

@app.route("/", methods = ['GET', 'POST'])
def index():
    src= render_markdown(os.path.join(srcpath, 'resume.md'))
    return render_template("static.html",
        title = "resume", heading = "Paul Munday", 
        contents = Markup(src))

@app.route("/src")
def source():
    with open(os.path.join(path, 'views.py'), 'r') as f:
        src = f.read()
    code = highlight(src, PythonLexer(), HtmlFormatter())
    css = HtmlFormatter(style="friendly").get_style_defs('.highlight')
    return render_template("static.html", internal_css =  css,
            title = "view the source code", heading = "View the Source Code",
            contents = Markup(code))

@app.route("/about/")
def about():
    src = render_markdown(os.path.join(srcpath, 'about.md'))
    return render_template("static.html", 
        title = "about", heading = "About This Website", 
        contents = Markup(src))

@app.route("/colophon/")
def colophon():
    src = render_markdown(os.path.join(srcpath, 'colophon.md'))
    return render_template("static.html", 
        title = "colophon", heading = "Colophon", 
        contents = Markup(src))


