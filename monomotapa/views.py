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

Copyright (C) 2014, Paul Munday.

PO Box 28228, Portland, OR, USA 97228
paul at paulmunday.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

There should also be a copy of the GPL in src/license.md that should be accessible  by going to <a href ="/license">/license<a> on this site.

As originally distributed this program will be able to display its own source code, which may count as conveying under the terms of the GPL v3. You should therefore make sure the copy of the GPL (i.e. src/license.md) is left in place.

You are also free to remove this section from the code as long as any modified copy you distribute (including a copy that is unchanged except for removal of this feature) is also licensed under the GPL version 3 (or later versions).

None of this means you have to license your own content this way, only the original source code and any modifications, or any subsequent additions that have been explicitly licensed under the GPL version 3 or later. 

You are therefore free to add templates and style sheets under your own terms though I would be happy if you chose to license them in the same way. 
"""
# set ENABLE_UNIT_TESTS to false to prevent unit tests being run
# through the source page
ENABLE_UNIT_TESTS = True

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

def get_page_attributes(jsonfile):
    """Returns dictionary of page_attributes.
    Defines additional static page attributes loaded from json file.
    N.B. static pages do not need to have attributes defined there,
    it is sufficient to have a page.md in src for each /page 
    possible values are src (name of markdown file to be rendered)
    heading, title, and trusted (i.e. allow embeded html in markdown)"""
    with open(src_file(jsonfile), 'r') as pagesfile:
        page_attributes = json.load(pagesfile)
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
    def __init__(self, page, title=None, heading=None, template = None):
        """Define attributes for  pages (if present).
        Sets self.name, self.title, self.heading, self.trusted
        This is done through indirection so we can update the defaults 
        (defined  in the 'attributes' dictionary) with values from pages.json
        easily without lots of if else statements.
        """
        # set default attributes
        self.page = page.rstrip('/')
        if not title:
            title = page.lower()
        if not heading:
            heading = page.capitalize()
        # will become self.name, self.title, self.heading, 
        # self.footer, self.template, self.trusted, self.headers
        attributes = {'name' : self.page, 'title' : title, 'hlinks' : None,
                'heading' : heading, 'footer' : None, 
                template: 'static.html', 'trusted': False}
        # overide attributes if set in pages.json
        self.pages = get_page_attributes('pages.json')
        if page in self.pages:
            attributes.update(self.pages[page])
        # set attributes (as self.name etc)  using indirection
        for attribute, value in attributes.iteritems():
            vars(self)[attribute] = value

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
            pagetemplate = 'static.html'
        if os.path.exists(src_file(pagetemplate , 'templates')):
            return pagetemplate
        else:
            # return static.html if we can't find the template
            return 'static.html'


    def generate_page(self, contents=None, internal_css=None, footer=None):
        """return a page generator function.
        For static pages written in Markdown under src/.
        contents are automatically rendered.
        N.B. See note above in about headers"""
        if not contents:
            contents = self._get_markdown()
        template = self.get_template(self.page)
        if not footer:
            footer = self.footer
        def page_generator(contents=contents, heading=self.heading, 
                title=self.title, internal_css = internal_css, 
                hlinks = self.hlinks, template=template, footer=footer):
            return render_template(template,
                title = title, heading = heading, internal_css = internal_css,
                hlinks = hlinks, footer = footer,
                navigation =  top_navigation(self.page), 
                contents = Markup(contents)),
        return page_generator()

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
    return render_template('static.html', 
            title = "404::page not found", heading = "Page Not Found", 
            navigation = top_navigation('404'),
            contents = Markup(
                "This page in not there, try somewhere else.")), 404

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
            heading = "View the Source Code")
    page = request.args.get('page')
    # get source for markdown if any. 404's for non-existant markdown
    # unless special page eg source
    pagesrc = source_page.get_page_src(page, 'src', 'md')
    special_pages = ['source', 'unit-tests', '404']
    if not page in special_pages and pagesrc is None:
        abort(404)
    # set ENABLE_UNIT_TESTS to false to prevent unit tests being run
    # through the source page
    if ENABLE_UNIT_TESTS:
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
    # format contents
    css = get_pygments_css()
    return source_page.generate_page(contents, internal_css = css)

@app.route("/unit-tests")
def unit_tests():
    """display results of unit tests"""
    unit_tests = Page('unit-tests', heading = "Test Results")
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
    css = get_pygments_css()
    return unit_tests.generate_page(contents, internal_css = css)

