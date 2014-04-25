"""
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

There should also be a copy of the GPL in src/license.md that should be accessib
le  by going to <a href ="/license">/license<a> on this site.

As originally distributed this program will be able to display its own source co
de, which may count as conveying under the terms of the GPL v3. You should there
fore make sure the copy of the GPL (i.e. src/license.md) is left in place.

You are also free to remove this section from the code as long as any modified c
opy you distribute (including a copy that is unchanged except for removal of thi
s feature) is also licensed under the GPL version 3 (or later versions).

None of this means you have to license your own content this way, only the origi
nal source code and any modifications, or any subsequent additions that have bee
n explicitly licensed under the GPL version 3 or later. 

You are therefore free to add templates and style sheets under your own terms th
ough I would be happy if you chose to license them in the same way. 
"""

import monomotapa
import unittest
import tempfile
import os
import os.path


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = monomotapa.app.test_client()
        path = 'monomotapa/src/'
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".md",
                dir=path, delete=False)
        self.filename = os.path.basename(self.tmpfile.name)
        self.route = os.path.splitext(self.filename)[0]
        with open(self.tmpfile.name ,'w') as f:
            f.write("&aleph; test")

    def tearDown(self):
        os.unlink(self.tmpfile.name)
   
    # Test Page class
    # generate_page is not tested directlu here as it is reliant on 
    # flask's context, testing is implicit in test_static_page etc)

    def test_Page(self):
        staticpage = monomotapa.views.Page(self.route)
        self.assertEquals(staticpage.name, self.route)
        self.assertEquals(staticpage.title, self.route.lower())
        self.assertEquals(staticpage.heading, self.route.capitalize())
        self.assertFalse(staticpage.trusted)
   
    # test generate page via call to home page
    
    def test_generate_page_with_template(self):
        index_page = self.app.get('/')
        # makes assumptions about templating/content
        self.assertIn('<div id="home">', index_page.data)
 
    def test_get_page_src(self):
        page = monomotapa.views.Page(self.route)
        result = page.get_page_src(self.filename, 'src')
        self.assertEquals(result, 'monomotapa/src/' + self.filename)

    def test_get_page_src_with_extension(self):
        page = monomotapa.views.Page(self.route)
        result = page.get_page_src(self.route, 'src', 'md')
        self.assertEquals(result, 'monomotapa/src/' + self.filename)
    
    def test_get_page_src_with_lookup(self):
        page = monomotapa.views.Page(self.route)
        result = page.get_page_src('index', 'src')
        self.assertEquals(result, 'monomotapa/src/home.md')
    
    def test_get_page_src_nonexistant_source(self):
        page = monomotapa.views.Page(self.route)
        result = page.get_page_src('non_existant')
        self.assertIsNone(result)

    def test_get_template(self):
        page = monomotapa.views.Page(self.route)
        result = page.get_template(self.route)
        self.assertEquals(result, 'static.html')
   
    def test_get_template_with_template(self):
        page = monomotapa.views.Page(self.route)
        result = page.get_template('index')
        self.assertEquals(result, 'home.html')

   # Test helper functions

    def test_get_page_attribute(self):
        pages = { 'test' : {'src' : 'test.md'}}
        result = monomotapa.views.get_page_attribute(pages, 'test', 'src')
        self.assertEquals(result, 'test.md')

    def test_get_page_attribute_no_page(self):
        pages = { 'test' : {'src' : 'test.md'}}
        result = monomotapa.views.get_page_attribute(pages, 'notest', 'src')
        self.assertIsNone(result)
    
    def test_get_page_attribute_no_attribute(self):
        pages = { 'test' : {'src' : 'test.md'}}
        result = monomotapa.views.get_page_attribute(pages, 'test', 'nosrc')
        self.assertIsNone(result)

    def test_src_file(self):
        result = monomotapa.views.src_file('test')
        self.assertEquals(result, 'monomotapa/test')

    def test_src_file_with_dir(self):
        result = monomotapa.views.src_file('test', 'src')
        self.assertEquals(result, 'monomotapa/src/test')

    def test_get_extension_no_period(self):
        result = monomotapa.views.get_extension('md')
        self.assertEquals(result, '.md')
    
    def test_get_extension_with_period(self):
        result = monomotapa.views.get_extension('.md')
        self.assertEquals(result, '.md')
    
    def test_get_extension_with_None(self):
        result = monomotapa.views.get_extension(None)
        self.assertEquals(result, '')

    def test_render_markdown(self):
        markdown = monomotapa.views.render_markdown(self.tmpfile.name)
        self.assertIn( 'test', markdown)

    def test_render_markdown_untrusted(self):
        markdown = monomotapa.views.render_markdown(self.tmpfile.name)
        self.assertNotIn( '&aleph;', markdown)
    
    def test_render_markdown_trusted(self):
        markdown = monomotapa.views.render_markdown(self.tmpfile.name,
                trusted=True)
        self.assertIn('&aleph;', markdown)
   
    def test_pygments_renderer(self):
        results = monomotapa.views.render_pygments(self.tmpfile.name,
                'markdown')
        self.assertIn('<pre>', results)
        self.assertIn('test', results)

    def test_get_pygments_css(self):
        css = monomotapa.views.get_pygments_css()
        self.assertIn('.highlight', css)

    def test_heading(self):
        expected = '\n<h1>test</h1>\n'
        result = monomotapa.views.heading('test', 1)
        self.assertEquals(result, expected)
    

    # Test page display/routes
    # Some of these  are dependent on templates and contents supplied,
    # but we want to test our end points


    def test_index(self):
        index_page = self.app.get('/')
        # makes assumptions about templating/content
        self.assertIn('Monomotapa', index_page.data)
        # will fail if md not rendered 
        self.assertNotIn('Not in this page', index_page.data)
        title = '%s</title>' % 'home'
        self.assertIn( title, index_page.data)

    def test_static_page(self):
        static_page = self.app.get('/' +  self.route)
        # tests for content
        self.assertIn('test', static_page.data)
        # will fail if md not rendered 
        self.assertNotIn('Not in page', static_page.data)

    def test_static_page_heading(self):
        static_page = self.app.get('/' +  self.route)
        # note dependent of static page template
        heading = '<h1>%s</h1>' % self.route.capitalize()
        self.assertIn( heading, static_page.data)

    def test_static_page_title(self):
        # note dependent of static page template
        static_page = self.app.get('/' +  self.route)
        title = '%s</title>' % self.route.lower()
        self.assertIn( title, static_page.data)


    def test_static_page_404(self):
        static_page = self.app.get('/non_existant')
        self.assertEquals(static_page.status_code, 404)

    def test_static_page_200(self):
        static_page = self.app.get('/' + self.route)
        self.assertEquals(static_page.status_code, 200)
  
    def test_source_page(self):
        source_page = self.app.get('/source?page=%s' % self.route)
        self.assertIn(self.filename, source_page.data)
    
    def test_source_page_200(self):
        static_page = self.app.get('/source?page=%s' % self.route)
        self.assertEquals(static_page.status_code, 200)

    def test_source_page_404(self):
        static_page = self.app.get('/source?page=non_existant')
        self.assertEquals(static_page.status_code, 404)

    def test_source_page_for_source(self):
        source_page = self.app.get('/source?page=source')
        # N.B. this makes assumptions about page layout
        # i.e. page names rendered as h2 heading
        self.assertIn('<h2>views.py', source_page.data)
        self.assertNotIn('<h2>tests.py', source_page.data)
    
    def test_source_page_for_rendered_source(self):
        source_page = self.app.get('/source?page=source')
        self.assertIn('Page', source_page.data)

    def test_source_page_for_unittests(self):
        source_page = self.app.get('/source?page=unit-tests')
        # N.B. this makes assumptions about page layout
        # i.e. page names rendered as h2 heading
        self.assertIn('<h2>tests.py', source_page.data)
    
    def test_source_page_for_rendered_unittests(self):
        source_page = self.app.get('/source?page=unit-tests')
        # always true if this test is rendered
        self.assertIn('def test_source_page_for_unittests', source_page.data)

    def test_source_page_for_rendered_template(self):
        source_page = self.app.get('/source?page=%s' % self.route)
        # always true if this test is rendered
        self.assertIn('static.html', source_page.data)

    def test_source_page_for_rendered_template_set(self):
        source_page = self.app.get('/source?page=%s' % 'index')
        # always true if this test is rendered
        self.assertIn('home.html', source_page.data)
if __name__ == '__main__':
    unittest.main()
