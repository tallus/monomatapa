#!/usr/bin/env python

from flask import render_template, flash, redirect, abort
from flask import Markup, escape

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import RstLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

import os.path
from os import getcwd

from collections import OrderedDict

import markdown

from resumemaker import app

# N.B. static pages do not need to have attributes  defined here:
# it is sufficient to have a page.md in src for each /page
# to be served. However if a page is to show up in the top navigation
# there must be an entry present with the name attribute set.
static_pages = OrderedDict({
    'index' : {
        'name' : 'home',
        'src' : 'resume.md',
        'title' : 'home', 
        'heading' : 'Paul Munday'
        }
    })

def get_static_attributes(page):
    '''return attributes for static pages (if present)'''
    srcfile = page.rstrip('/') + '.md'
    attributes = {'src': srcfile, 'title' : None, 'heading' : None}
    if page in static_pages:
        sp = static_pages[page]
        for attribute in ['src', 'title' , 'heading']:
            if attribute in sp:
                attributes[attribute] = sp[attribute]
    return attributes['src'], attributes['title'], attributes['heading']


def src_file(name, directory=None):
    '''return path to file in this app'''
    if not directory:
        return os.path.join( 'resumemaker', name)
    else:
        return os.path.join('resumemaker', directory, name)
    
def render_markdown(file, trusted=False):
    '''Return markdown file rendered as html. Defaults to untrusted:
        html characters are escaped so will not be rendered.
        This departs from markdown spec which allows embedded html.'''
    try:
        with open(file, 'r') as f:
            if trusted == True:
                return markdown.markdown(f.read())
            else:
                return markdown.markdown(escape(f.read()))
    except IOError:
           return None

def static_page(srcfile, heading=None, title=None):
    '''return a page generator  function for static pages 
    written in Markdown under src/. Takes the name of the markdown file
    its title and main heading'''
    def page_generator(heading=heading, title=title):
        src = render_markdown(src_file(srcfile, 'src'))
        if not src:
            abort(404)
        else:
            if not heading:
                heading = os.path.splitext(srcfile)[0].capitalize()
            if not title:
                title = heading.lower()
            return render_template("static.html",
                title = title, heading = heading, 
                contents = Markup(src))
    return page_generator()

@app.errorhandler(404)
def page_not_found(e):
    ''' provides basic 404 page'''
    return render_template('static.html', 
            title = "404::page not found", heading = "Page Not Found", 
            contents = Markup(
                "This page in not there, try somewhere else.")), 404

@app.route("/")
def index():
    '''provides index page'''
    srcfile, title, heading = get_static_attributes('index')
    return static_page(srcfile, title = title, heading = heading)

@app.route("/<path:page>")
def staticpage(page):
    '''displays /page or /page/ as long as src/page.md exists.
    srcfile, title and heading may be set in the pages global 
    (ordered) dictionary but are not required'''
    srcfile, title, heading = get_static_attributes(page)
    return static_page(srcfile, title = title, heading = heading)

@app.route("/source")
def source():
    '''view source files used to render a page'''
    with open(src_file('views.py'), 'r') as f:
        src = f.read()
    code = highlight(src, PythonLexer(), HtmlFormatter())
    css = HtmlFormatter(style="friendly").get_style_defs('.highlight')
    return render_template("static.html", internal_css =  css,
        title = "view the source code", heading = "View the Source Code",
        contents = Markup(code))

