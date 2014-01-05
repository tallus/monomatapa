#!/usr/bin/env python

from flask import render_template, flash, redirect, abort, Markup, escape
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
# to be served.
pages = {
    'index' : {
        'src' : 'resume.md',
        'title' : 'home', 
        'heading' : 'Paul Munday',
        'trusted' : True,
        },
     'about' : {
         'title' : 'about me',
         'heading' : 'About Me',
         'trusted' : True,
         },
    }

# Navigation

# if a page is to show up in the top navigation
# there must be an entry present with the name attribute set.
# name will be used to set the link text, unless link_text is also present
# url and urlfor are optional, however if ommited the url wil be generated
# in the navigation by  url_for('staticpage', page=[key])
# (equivalent to  @app.route"/page"; def page())
# which may not be correct. If a url is supplied  it will be used 
# otherwise if urlfor is supplied it the url will be
# generated with url_for(urlfor). url takes precendence so it makes
# no sense to supply both.

top_navigation = OrderedDict({
    'index' : {
        'name' : 'home',
        'urlfor' : 'index',
        },
    'about' : {
        # name : 'about'
        'link text' : 'about me' 
        },
    'github' : {
        'name' : 'github',
        'url' : 'https://github.com/tallus',
        },
    'colophon' : {
        'name' : 'colophon',
        },
    'source'  : {
        'name' : 'source',
        'link_text' : 'view the source',
        'urlfor' : 'source'
        }
    })


def base_navigation():
    """Generates base  info navigation from navigation OrderedDict"""
    base_nav = OrderedDict({})
    for key, value in top_navigation.iteritems():
        nav = {}
        if 'name' in value:
            nav['base'] = key
            if 'link_text' in value:
                nav['text'] = value['link_text']
            else:
                nav['text'] = value['name']
            if 'url' in value:
                nav['url'] = value['url']
            if 'urlfor' in value:
                nav['urlfor'] = value['urlfor']
            base_nav[key] = nav
    return base_nav

# this is static so generate once
base_nav = base_navigation()

def  navigation(page):
    """Generates top navigation info."""
    return {'navigation' :  base_nav, 'page' : page}


def get_static_attributes(page):
    """return attributes for static pages (if present)"""
    srcfile = page.rstrip('/') + '.md'
    attributes = {'src': srcfile,  'name' : page,
            'title' : None, 'heading' : None, 'trusted': False}
    if page in pages:
        sp = pages[page]
        for attribute in ['src', 'title' , 'heading', 'trusted']:
            if attribute in sp:
                attributes[attribute] = sp[attribute]
    return attributes['src'], attributes['title'], attributes['heading'], attributes['trusted']


def src_file(name, directory=None):
    """return path to file in this app"""
    if not directory:
        return os.path.join( 'resumemaker', name)
    else:
        return os.path.join('resumemaker', directory, name)
    
def render_markdown(file, trusted=False):
    """Return markdown file rendered as html. Defaults to untrusted:
        html characters (and character entities) are escaped 
        so will not be rendered. This departs from markdown spec 
        which allows embedded html."""
    try:
        with open(file, 'r') as f:
            if trusted == True:
                return markdown.markdown(f.read())
            else:
                return markdown.markdown(escape(f.read()))
    except IOError:
           return None

def static_page(srcfile, page, heading=None, title=None, trusted=False):
    """return a page generator  function for static pages 
    written in Markdown under src/. Takes the name of the markdown file,
    the page name (equivalent = @app.route"/page"; def page())
    its title and main heading"""
    def page_generator(heading=heading, title=title):
        src = render_markdown(src_file(srcfile, 'src'), trusted)
        if not src:
            abort(404)
        else:
            if not heading:
                heading = os.path.splitext(srcfile)[0].capitalize()
            if not title:
                title = heading.lower()
            return render_template("static.html",
                title = title, heading = heading, 
                navigation = navigation(page), 
                contents = Markup(src)),
    return page_generator()

@app.errorhandler(404)
def page_not_found(e):
    """ provides basic 404 page"""
    return render_template('static.html', 
            title = "404::page not found", heading = "Page Not Found", 
            navigation = navigation('404'),
            contents = Markup(
                "This page in not there, try somewhere else.")), 404

@app.route("/")
def index():
    """provides index page"""
    srcfile, title, heading, trusted = get_static_attributes('index')
    return static_page(srcfile, 'index',  
            title = title, heading = heading, trusted=trusted)

@app.route("/<path:page>")
def staticpage(page):
    """displays /page or /page/ as long as src/page.md exists.
    srcfile, title and heading may be set in the pages global 
    (ordered) dictionary but are not required"""
    srcfile, name, title, heading, trusted = get_static_attributes(page)
    return static_page(srcfile, page,
            title = title, heading = heading, trusted=trusted)

@app.route("/source")
def source():
    """view source files used to render a page"""
    with open(src_file('views.py'), 'r') as f:
        src = f.read()
    code = highlight(src, PythonLexer(), HtmlFormatter())
    css = HtmlFormatter(style="friendly").get_style_defs('.highlight')
    return render_template("static.html", internal_css =  css,
        title = "view the source code", heading = "View the Source Code",
        navigation = navigation('source'),
        contents = Markup(code))

