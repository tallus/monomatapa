"""
Monomotapa:
    a city whose inhabitants are bounded by deep feelings of friendship, so that
    they intuit one another's most secret needs and desire. For instance, if one
    dreams that his friend is sad, the friend will perceive the distress and 
    rush to the sleepers rescue.

    (Jean de La Fontaine, *Fables choisies, mises en vers*, VIII:11 Paris, 
    2nd ed., 1678-9)

cited in : 
Alberto Manguel and Gianni Guadalupi, *The Dictionary of Imaginary Places*, 
Bloomsbury, London, 1999.

A micro cms written using the Flask microframework, orignally to manage my 
personal site. It is designed so that publishing a page requires no more than
dropping a markdown page in the appropriate directory (though you need to edit
a json file if you want it to appear in the top navigation). 

It can also display its own source code and run its own unit tests.

The name 'monomotapa' was chosen more or less at random (it shares an initial
with me) as I didn't want to name it after the site and be typing import 
paulmunday, or something similar,  as that would be strange.

Monomotapa - A Micro CMS
Copyright (C) 2014, Paul Munday.

PO Box 28228, Portland, OR, USA 97228
paul at paulmunday.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero  Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

There should also be a copy of the GPL in src/license.md that should be accessible by going to <a href ="/license">/license<a> on this site.
"""


from flask import render_template, abort, Markup, escape, request, make_response

from pygments import highlight
from pygments.lexers import PythonLexer, HtmlDjangoLexer, TextLexer
from pygments.formatters import HtmlFormatter

import markdown

import os.path
import os
import subprocess
import json
from collections import OrderedDict

from monomotapa import app
from config import ConfigError

class MonomotapaError(Exception):
    """create classs for own errors"""
    pass

def get_page_attributes(jsonfile):
    """Returns dictionary of page_attributes.
    Defines additional static page attributes loaded from json file.
    N.B. static pages do not need to have attributes defined there,
    it is sufficient to have a page.md in src for each /page 
    possible values are src (name of markdown file to be rendered)
    heading, title, and trusted (i.e. allow embeded html in markdown)"""
    try:
        with open(src_file(jsonfile), 'r') as pagesfile:
            page_attributes = json.load(pagesfile)
    except IOError:
            page_attributes = []
    return page_attributes

def get_page_attribute(attr_src, page, attribute):
    """returns attribute of page if it exists, else None.
    attr_src = dictionary(from get_page_attributes)"""
    if page in attr_src and attribute in attr_src[page]:
        return attr_src[page][attribute]
    else:
        return None
    

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
    no sense to supply both.
    Web Sign-in is supported by adding a "rel": "me" attribute.
    """
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


# For pages
class Page:
    """Generates  pages as objects"""
    def __init__(self, page, **kwargs):
        """Define attributes for  pages (if present).
        Sets self.name, self.title, self.heading, self.trusted etc
        This is done through indirection so we can update the defaults 
        (defined  in the 'attributes' dictionary) with values from config.json
        or pages.json easily without lots of if else statements.
        If css is supplied it will overide any default css. To add additional
        style sheets on a per page basis specifiy them in pages.json.
        The same also applies with hlinks.
        css is used to set locally hosted stylesheets only. To specify 
        external stylesheets use hlinks: in config.json for 
        default values that will apply on all pages unless overidden, set here
        to override the default. Set in pages.json to add after default.
        """
        # set default attributes
        self.page = page.rstrip('/')
        self.defaults = get_page_attributes('defaults.json')
        self.pages = get_page_attributes('pages.json')
        title = page.lower()
        heading = page.capitalize()
        try:
            self.default_template = self.defaults['template']
        except KeyError:
            raise ConfigError('template not found in default.json')
        # will become self.name, self.title, self.heading, 
        # self.footer, self.internal_css, self.trusted
        attributes = {'name' : self.page, 'title' : title,
                'navigation' : top_navigation(self.page),
                'heading' : heading, 'footer' : None,
                'css' : None , 'hlinks' :None, 'internal_css' : None,
                'trusted': False}
        # set from defaults
        attributes.update(self.defaults)
        # override with kwargs
        attributes.update(kwargs)
        # override attributes if set in pages.json
        if page in self.pages:
            attributes.update(self.pages[page])
        # set attributes (as self.name etc)  using indirection
        for attribute, value in attributes.iteritems():
            vars(self)[attribute] = value
        # reset these as we want to append rather than overwrite if supplied
        if 'css' in kwargs:
            self.css = kwargs['css']
        elif 'css' in self.defaults:
                self.css = self.defaults['css']
        if 'hlinks' in kwargs:
            self.hlinks = kwargs['hlinks']
        elif 'hlinks' in self.defaults:
            self.hlinks = self.defaults['hlinks']
        # append hlinks and css from pages.json rather than overwriting
        # if css or hlinks are not supplied they are set to default
        if page in self.pages:
            if 'css' in self.pages[page]:
                self.css = self.css + self.pages[page]['css']
            if 'hlinks' in self.pages[page]:
                self.hlinks = self.hlinks + self.pages[page]['hlinks']
        # append heading to default if set in config
        if app.config['default_title']:
            self.title = app.config['default_title'] + self.title


    def _get_markdown(self):
        """returns rendered markdown or 404 if source does not exist"""
        src = self.get_page_src(self.page, 'src', 'md') 
        if src is None:
            abort(404)
        else:
            return render_markdown(src, self.trusted)

    def get_page_src(self, page, directory=None, ext=None):
        """"return path of file (used to generate page) if it exists,
        or return none.
        Also returns the template used to render that page, defaults
        to static.html.
        It will optionally add an extension, to allow 
        specifiying pages by route."""
        # is it stored in a config
        pagename = get_page_attribute(self.pages, page, 'src')
        if not pagename:
            pagename = page + get_extension(ext)
        if os.path.exists(src_file(pagename , directory)):
            return src_file(pagename, directory)
        else:
            return None

    def get_template(self, page):
        """returns the template for the page"""
        pagetemplate = get_page_attribute(self.pages, page, 'template')
        if not pagetemplate:
            pagetemplate = self.default_template
        if os.path.exists(src_file(pagetemplate , 'templates')):
            return pagetemplate
        else:
            raise MonomotapaError("Template: %s not found" % pagetemplate)

    def generate_page(self, contents=None):
        """return a page generator function.
        For static pages written in Markdown under src/.
        contents are automatically rendered.
        N.B. See note above in about headers"""
        if not contents:
            contents = self._get_markdown()
        template = self.get_template(self.page)
        return render_template(template, 
                contents = Markup(contents),
                **vars(self)
                )

# helper functions
def src_file(name, directory=None):
    """return potential path to file in this app"""
    if not directory:
        return os.path.join( 'monomotapa', name)
    else:
        return os.path.join('monomotapa', directory, name)


def get_extension(ext):
    '''constructs extension, adding or stripping leading . as needed.
    Return null string for None'''
    if ext is None:
        return ''
    elif ext[0] == '.':
        return ext
    else:
        return '.%s' % ext

def render_markdown(srcfile, trusted=False):
    """Return markdown file rendered as html. Defaults to untrusted:
        html characters (and character entities) are escaped 
        so will not be rendered. This departs from markdown spec 
        which allows embedded html."""
    try:
        with open(srcfile, 'r') as f:
            if trusted == True:
                return markdown.markdown(f.read())
            else:
                return markdown.markdown(escape(f.read()))
    except IOError:
        return None

def render_pygments(srcfile, lexer_type):
    """returns src(file) marked up with pygments"""
    if lexer_type == 'python':
        with open(srcfile, 'r') as f:
            src = f.read()
            contents = highlight(src, PythonLexer(), HtmlFormatter())
    elif lexer_type == 'html':
        with open(srcfile, 'r') as f:
            src = f.read()
            contents = highlight(src, HtmlDjangoLexer(), HtmlFormatter())
    # default to TextLexer for everything else
    else:
        with open(srcfile, 'r') as f:
            src = f.read()
            contents = highlight(src, TextLexer(), HtmlFormatter())
    return contents

def get_pygments_css(style=None):
    """returns css for pygments, use as internal_css"""
    if style is None:
        style = 'friendly'
    return HtmlFormatter(style=style).get_style_defs('.highlight')


def heading(text, level):
    """return as html heading at h[level]"""
    hl = 'h%s' % str(level)
    return '\n<%s>%s</%s>\n' % (hl, text, hl)


# Define routes

@app.errorhandler(404)
def page_not_found(e):
    """ provides basic 404 page"""
    defaults = get_page_attributes('defaults.json')
    try:
        css = defaults['css']
    except KeyError:
        css = None
    pages = get_page_attributes('pages.json')
    if '404' in pages:
        if'css' in pages['404']:
            css = pages['404']['css']
    return render_template('static.html', 
            title = "404::page not found", heading = "Page Not Found", 
            navigation = top_navigation('404'),
            css = css,
            contents = Markup(
                "This page is not there, try somewhere else.")), 404

@app.route("/")
def index():
    """provides index page"""
    index = Page('index')
    return index.generate_page()

# default route is it doe not exist elsewhere
@app.route("/<path:page>")
def staticpage(page):
    """ display a static page rendered from markdown in src
    i.e. displays /page or /page/ as long as src/page.md exists.
    srcfile, title and heading may be set in the pages global 
    (ordered) dictionary but are not required"""
    static_page = Page(page)
    return static_page.generate_page()

# specialized pages
@app.route("/source")
def source():
    """Display source files used to render a page"""
    source_page = Page('source', title = "view the source code", 
            heading = "View the Source Code",
            internal_css = get_pygments_css())
    page = request.args.get('page')
    # get source for markdown if any. 404's for non-existant markdown
    # unless special page eg source
    pagesrc = source_page.get_page_src(page, 'src', 'md')
    special_pages = ['source', 'unit-tests', '404']
    if not page in special_pages and pagesrc is None:
        abort(404)
    # set enable_unit_tests  to true  in config.json to allow 
    #  unit tests to be run  through the source page
    if app.config['enable_unit_tests']:
        contents = '''<p><a href="/unit-tests" class="button">Run unit tests
    </a></p>'''
        # render tests.py if needed
        if page == 'unit-tests':
            contents += heading('tests.py', 2)
            contents += render_pygments('tests.py', 'python')
    else:
        contents = ''
    # render views.py
    contents += heading('views.py', 2)
    contents += render_pygments(source_page.get_page_src('views.py'), 
            'python')
    # render markdown if present
    if pagesrc:
        contents += heading(os.path.basename(pagesrc), 2)
        contents += render_pygments(pagesrc, 'markdown')
    # render jinja templates
    contents += heading('base.html', 2)
    contents += render_pygments(
            source_page.get_page_src('base.html', 'templates'), 'html')
    template = source_page.get_template(page)
    contents += heading(template, 2)
    contents += render_pygments(
            source_page.get_page_src(template, 'templates'), 'html')
    return source_page.generate_page(contents)

@app.route("/unit-tests")
def unit_tests():
    """display results of unit tests"""
    unit_tests = Page('unit-tests', heading = "Test Results", 
            internal_css = get_pygments_css())
    # exec unit tests in subprocess, capturing stderr
    capture = subprocess.Popen(["python", "tests.py"], 
            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output = capture.communicate()
    results = output[1]
    contents = '''<p>
    <a href="/unit-tests" class="button">Run unit tests</a>
    </p><br>\n
    <div class="output" style="background-color:'''
    if 'OK' in results:
        color = "#ddffdd"
        result = "TESTS PASSED"
    else:
        color = "#ffaaaa"
        result = "TESTS FAILING"
    contents += ('''%s">\n<strong>%s</strong>\n<pre>%s</pre>\n</div>\n'''
            % (color, result, results))
    # render test.py 
    contents += heading('tests.py', 2)
    contents += render_pygments('tests.py', 'python')
    return unit_tests.generate_page(contents)

