import json
import imp
class Plugin(object):
    """
    Base Class for Plugins. 
    =======================
    All plugins must consist of a single class that inherits from this one. 
    The class name must be equivalent to the module name. 
    ie myplugin.py contains  the myplugin class (lower case).
    Plugins must be installed in the plugins directory
    To enable a pugin add it to plugin.json as a key value pair, where
    the key is the plugin name and the value is the target. 
    The target is page, where * is all pages. path/* is also permissible.
    Each class must 
        1. be capable of taking any set of arbitary key/value pairs via **kwargs
            (you are free to ignore/discard any of them)
        2. produce as their sole ouput a dictionary through the output method, 
            that must have a key called 'class_name' 
            with the value self.__class__.__name__ 

        This dictionary will be passed back into the Page/Post etc object
        in a dictionary called plugins in as the value to a key that is 
        the same as the module name (i.e. lower class) which will be 
        added to its vars(self) where it can be used in jinja2 templates.
        It will be passed vars(self) as **kwargs
    """
    pass

class Sampleplugin(Plugin):
    """Sample Plugin"""
    def __init__(self, **kwargs):
        """takes **kwargs"""
        self.page = "My name is " + kwargs['page']
    def output(self):
        """returns dict"""
        return {'class_name' : self.__class__.__name__, 'page_name' : self.page}

def load_plugin_conf(plugin_file):
    """Get plugin conf from json file, return dict.
    JSON file should be name, applies to k/v array"""
    try:
        with open(plugin_file, 'r') as pfile:
            plugin_conf = json.load(pfile)
    except IOError:
        plugin_conf = {}
    return plugin_conf

def load_plugins(plugin_path, plugin_conf):
    """Parse plugin conf and checks to see if plugin can be found, and if so
    load it.Returns a dict identical in format to 
    plugin_conf (name, applies_to) with loaded modules"""
    plugins={}
    for name, applies_to in plugin_conf:
        filename, pathname, description = imp.find_module(name, plugin_path)
        try:
            imp.load_module(filename, pathname, description)
            plugins[name] = applies_to
        finally:
            if filepath:
                filepath.close()
    return plugins

'''
# importing with indirection using __import__
# import class
X = __import__('datetime')
# assign class 
z = vars(X)['datetime']
# or x = X.getattr(module, 'datetime')
z.now()

# with imp
file, fpath, desc = imp.find_module(name[, path]) -- search for module
imp.load_module(name, file, fpath, desc)
'''
        
