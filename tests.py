import resumemaker
import unittest
import tempfile
import os
import os.path

class ResumeTestCase(unittest.TestCase):

    def setUp(self):
        self.app = resumemaker.app.test_client()
        path = 'resumemaker/src/'
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".md",
                dir=path, delete=False)
        self.filename = os.path.basename(self.tmpfile.name)
        self.route = os.path.splitext(self.filename)[0]
        with open(self.tmpfile.name ,'w') as f:
            f.write("&aleph; test")

    def tearDown(self):
        os.unlink(self.tmpfile.name)
   
    # Test StaticPage class
    # generate_page is not tested here as it is reliant on 
    # flask's context, testing is implicit in test_static_page etc

    def test_StaticPage(self):
        staticpage = resumemaker.views.StaticPage(self.route)
        self.assertEquals(staticpage.name, self.route)
        self.assertEquals(staticpage.title, self.route.lower())
        self.assertEquals(staticpage.heading, self.route.capitalize())
        self.assertFalse(staticpage.trusted)
   
   # Test helper functions
    def test_src_file(self):
        result = resumemaker.views.src_file('test')
        self.assertEquals(result, 'resumemaker/test')

    def test_src_file_with_dir(self):
        result = resumemaker.views.src_file('test', 'src')
        self.assertEquals(result, 'resumemaker/src/test')

    def test_get_extension_no_period(self):
        result = resumemaker.views.get_extension('md')
        self.assertEquals(result, '.md')
    
    def test_get_extension_with_period(self):
        result = resumemaker.views.get_extension('.md')
        self.assertEquals(result, '.md')
    
    def test_get_extension_with_None(self):
        result = resumemaker.views.get_extension(None)
        self.assertEquals(result, '')

    def test_get_page_src(self):
        result = resumemaker.views.get_page_src(self.filename, 'src')
        self.assertEquals(result, 'resumemaker/src/' + self.filename)

    def test_get_page_src_with_extension(self):
        result = resumemaker.views.get_page_src(self.route, 'src', 'md')
        self.assertEquals(result, 'resumemaker/src/' + self.filename)
    
    def test_get_page_src_with_lookup(self):
        result = resumemaker.views.get_page_src('index', 'src')
        self.assertEquals(result, 'resumemaker/src/resume.md')
    
    def test_get_page_src_nonexistant_source(self):
        result = resumemaker.views.get_page_src('non_existant')
        self.assertIsNone(result)

    def test_render_markdown(self):
        markdown = resumemaker.views.render_markdown(self.tmpfile.name)
        assert 'test' in markdown

    def test_render_markdown_untrusted(self):
        markdown = resumemaker.views.render_markdown(self.tmpfile.name)
        assert '&aleph;' not in markdown
    
    def test_render_markdown_trusted(self):
        markdown = resumemaker.views.render_markdown(self.tmpfile.name,
                trusted=True)
        assert '&aleph;' in markdown
       
    # Test page display/routes
    # Some of these  are dependent on templates and contents supplied,
    # but we want to test our end points


    def test_index(self):
        index_page = self.app.get('/')
        # makes assumptions about templating/content
        assert 'Paul Munday' in index_page.data
        # will fail if md not rendered 
        assert 'None' not in index_page.data
        title = '<title>paulmunday.net::%s</title>' % 'home'
        assert  title in index_page.data


    def test_static_page(self):
        static_page = self.app.get('/' +  self.route)
        # tests for content
        assert 'test' in static_page.data
        # will fail if md not rendered 
        assert 'None' not in static_page.data

    def test_static_page_heading(self):
        static_page = self.app.get('/' +  self.route)
        # note dependent of static page template
        heading = '<h1>%s</h1>' % self.route.capitalize()
        assert  heading in static_page.data

    def test_static_page_title(self):
        # note dependent of static page template
        static_page = self.app.get('/' +  self.route)
        title = '<title>paulmunday.net::%s</title>' % self.route.lower()
        assert  title in static_page.data


    def test_static_page_404(self):
        static_page = self.app.get('/non_existant')
        self.assertEquals(static_page.status_code, 404)

    def test_static_page_200(self):
        static_page = self.app.get('/' + self.route)
        self.assertEquals(static_page.status_code, 200)
    
    def test_source_page(self):
        source_page = self.app.get('/source?page=%s' % self.route)
        assert self.filename in source_page.data
    
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
        assert '<h2>views.py' in source_page.data
        assert '<h2>tests.py' not in source_page.data
    
    def test_source_page_for_rendered_source(self):
        source_page = self.app.get('/source?page=source')
        assert 'StaticPage' in source_page.data

    def test_source_page_for_unittests(self):
        source_page = self.app.get('/source?page=unit-tests')
        # N.B. this makes assumptions about page layout
        # i.e. page names rendered as h2 heading
        assert '<h2>tests.py' in source_page.data
        assert '<h2>views.py' not in source_page.data
    
    def test_source_page_for_rendered_unittests(self):
        source_page = self.app.get('/source?page=unit-tests')
        # always true if this test is rendered
        assert 'def test_source_page_for_unittests' in source_page.data

if __name__ == '__main__':
    unittest.main()
