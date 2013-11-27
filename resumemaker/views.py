#!/usr/bin/env python

import unittest
from flask import render_template, flash, redirect
from flask import Markup 
from resumemaker import app

@app.route("/", methods = ['GET', 'POST'])
def index():
    return render_template("static.html", 
        title = "resume", heading = "Paul Munday", 
    contents = Markup("""My Resume will be here..."""))

@app.route("/about/")
def about():
    return render_template("static.html", 
        title = "about", heading = "About This Website", 
    contents = Markup("""Content goes here..."""))

@app.route("/colophon/")
def colophon():
    return render_template("static.html", 
        title = "colophon", heading = "Colophon", 
    contents = Markup("""<h3>A note about the technology</h3><em>This was made using the <a href="http://flask.pocoo.org">Flask</a> microframework for <a href="http://www.python.org">Python</a>.</em><br> 
    <h3>A note about the type</h3>
    <em>This is set in the <a href="http://www.google.com/fonts/specimen/EB+Garamond">EB Garamond</a> typeface.</em>"""))

@app.route("/src")
def source():
    with open('/home/paul/code/paulmunday.net/resumemaker/views.py', 'r') as f:
        contents = f.read()
    return render_template("static.html",
            title = "view the source", heading = "View the Source",
            contents = Markup("<code> %s </code>" % contents))

    #if __name__ == "__main__":
