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
   
    # test StaticPage class
    # generate_page is not tested here as it is reliant on 
    # flask's context, testing is implicit in test_static_page etc

    def test_StaticPage(self):
        staticpage = resumemaker.views.StaticPage(self.route)
        self.assertEquals(staticpage.name, self.route)
        self.assertEquals(staticpage.src, self.filename)
        self.assertEquals(staticpage.title, self.route.lower())
        self.assertEquals(staticpage.heading, self.route.capitalize())
        self.assertFalse(staticpage.trusted)
   
   # test helper functions

    def test_src_exists(self):
        result = resumemaker.views.src_exists(self.route)
        self.assertEquals(result, 'resumemaker/src/' + self.filename)

    def test_src_exists_with_lookup(self):
        result = resumemaker.views.src_exists('index')
        self.assertEquals(result, 'resumemaker/src/resume.md')
    
    def test_src_exists_nonexistant_source(self):
        result = resumemaker.views.src_exists('non_existant')
        self.assertIsNone(result)

    def test_src_file(self):
        result = resumemaker.views.src_file('test')
        self.assertEquals(result, 'resumemaker/test')

    def test_src_file_with_dir(self):
        result = resumemaker.views.src_file('test', 'src')
        self.assertEquals(result, 'resumemaker/src/test')

    def test_get_page_src(self):
        pagesrc = resumemaker.views.get_page_src(self.route)
        self.assertEquals(pagesrc, 'resumemaker/src/' + self.filename)

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
       
    # test page display/routes

    def test_index(self):
         index_page = self.app.get('/')
         assert 'Paul Munday' in index_page.data

    def test_static_page(self):
        static_page = self.app.get('/' +  self.route)
        assert 'test' in static_page.data

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
        assert '<h2>views.py' in source_page.data
        assert '<h2>tests.py' not in source_page.data
    
    def test_source_page_for_rendered_source(self):
        source_page = self.app.get('/source?page=source')
        assert 'StaticPage' in source_page.data

    def test_source_page_for_unittests(self):
        source_page = self.app.get('/source?page=unit-tests')
        assert '<h2>tests.py' in source_page.data
        assert '<h2>views.py' not in source_page.data
    
    def test_source_page_for_rendered_unittests(self):
        source_page = self.app.get('/source?page=unit-tests')
        assert 'def test_source_page_for_unittests' in source_page.data

if __name__ == '__main__':
    unittest.main()
