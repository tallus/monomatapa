#!/usr/bin/env python

from flask import render_template, abort, Markup, escape, request 
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import TextLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

import os.path
from os import getcwd

from collections import OrderedDict

import json

import markdown

from resumemaker import app


# 
def get_page_attributes():
    """Returns dictionary of page_attributes.
    Defines additional static page attributes loaded from json file.
    N.B. static pages do not need to have attributes defined there,
    it is sufficient to have a page.md in src for each /page 
    possible values are src (name of markdown file to be rendered)
    heading, title, and trusted (i.e. allow embeded html in markdown)"""
    with open(src_file('pages.json'), 'r') as pagesfile:
        page_attributes = json.load(pagesfile)
    return page_attributes

# Navigation
def top_navigation(page):
    """Generates navigation as an OrderedDict from navigation.json.
    Navigation.json consists of a json array(list) "nav_order"
    containing the names of the top navigation elements and 
    a json object(dict) called "nav_elements"
    if a page is to show up in the top navigation
    there must be an entry present in nav_order but there need not
    be one in nav_elements. However if there is the key must be the same. 
    Possible values for nav_elements are link_text, url and urlfor
    The name  from nav_order will be used to set the link text, 
    unless link_text is present in nav_elements.
    url and urlfor are optional, however if ommited the url wil be
    generated in the navigation by  url_for('staticpage', page=[key])
    equivalent to  @app.route"/page"; def page())
    which may not be correct. If a url is supplied  it will be used 
    otherwise if urlfor is supplied it the url will be
    generated with url_for(urlfor). url takes precendence so it makes
    no sense to supply both."""
    with open(src_file('navigation.json'), 'r') as  navfile:
        navigation = json.load(navfile)
    base_nav = OrderedDict({})
    for key in navigation["nav_order"]:
        nav = {}
        nav['base'] = key
        nav['link_text'] = key
        if key in navigation["nav_elements"]:
            elements = navigation["nav_elements"][key]
            nav.update(elements)
        base_nav[key] = nav
    return {'navigation' :  base_nav, 'page' : page}

# For static pages
class StaticPage:
    """Generates static pages as objects"""
    def __init__(self, page):
        """Define attributes for static pages (if present)"""
        # set default attributes
        self.page = page
        attributes = {'src': page.rstrip('/') + '.md', 'name' : page,
                'title' : None, 'heading' : None, 'trusted': False}
        # update values if set
        pages = get_page_attributes()
        if page in pages:
            attributes.update(pages[page])
        # set attributes using indirection, sets self.src etc
        for attribute, value in attributes.iteritems():
            vars(self)[attribute] = value
    
    def generate_page(self):
        """return a page generator function for static pages 
        written in Markdown unde
        r src/."""
        def page_generator(heading=self.heading, title=self.title):
            src = render_markdown(src_file(self.src, 'src'), self.trusted)
            if not src:
                abort(404)
            else:
                if not heading:
                    # src - extension capitalized
                    heading = os.path.splitext(self.src)[0].capitalize()
                if not title:
                    title = heading.lower()
                return render_template("static.html",
                    title = title, heading = heading, 
                    navigation =  top_navigation(self.page), 
                    contents = Markup(src)),
        return page_generator()

# helper functions for static pages
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

# Define routes

@app.errorhandler(404)
def page_not_found(e):
    """ provides basic 404 page"""
    return render_template('static.html', 
            title = "404::page not found", heading = "Page Not Found", 
            navigation = top_navigation('404'),
            contents = Markup(
                "This page in not there, try somewhere else.")), 404

@app.route("/")
def index():
    """provides index page"""
    index = StaticPage('index')
    return index.generate_page()

@app.route("/<path:page>")
def staticpage(page):
    """displays /page or /page/ as long as src/page.md exists.
    srcfile, title and heading may be set in the pages global 
    (ordered) dictionary but are not required"""
    static_page = StaticPage(page)
    return static_page.generate_page()

@app.route("/source")
def source():
    """Display source files used to render a page"""
       # render views.py
    with open(src_file('views.py'), 'r') as f:
        src = f.read()
    code = highlight(src, PythonLexer(), HtmlFormatter())
    contents = "<h2>views.py</h2>\n%s" % code
    # render markdown
    page = request.args.get('page')
    pagename = page + '.md'
    pages = get_page_attributes()
    if page in pages and 'src' in pages[page]:
        pagename = pages[page]['src']
    page = request.args.get('page')
    if os.path.exists(src_file(pagename, 'src')):
        page = src_file(pagename, 'src')
    elif os.path.exists(src_file(pagename)):
        page = src_file(pagename)
    else:
        print "no page:" + page
        page = None
    if page:
        with open(page, 'r') as f:
            markdown = f.read()
            contents  += "<h2>%s</h2>" % pagename
            contents += highlight(markdown, TextLexer(), HtmlFormatter())
    # format contents
    css = HtmlFormatter(style="friendly").get_style_defs('.highlight')
    return render_template("static.html", internal_css =  css,
        title = "view the source code", heading = "View the Source Code",
        navigation = top_navigation('source'),
        contents = Markup(contents))
    
