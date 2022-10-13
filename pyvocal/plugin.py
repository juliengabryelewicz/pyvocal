import abc
import configparser
import imp
import inspect
import os

MUST_HAVE_OPTIONS = (
    ('Plugin', 'Name'),
    ('Plugin', 'Version')
)

PLUGIN_INFO_FILENAME = "plugin.info"

def parse_info_file(infofile_path):
    cp = configparser.RawConfigParser()
    cp.read(infofile_path)

    options_missing = False
    for option in MUST_HAVE_OPTIONS:
        if not cp.has_option(*option):
            options_missing = True

    if options_missing:
        print("Info file is missing values!")

    return cp

def get_plugin_class(module_name, plugin_directory):
    mod = imp.load_module(module_name, None, plugin_directory,("py", "r", imp.PKG_DIRECTORY))
    plugin_classes = inspect.getmembers(mod, lambda cls: inspect.isclass(cls) and issubclass(cls, PluginObject))
    if len(plugin_classes) < 1:
        print("Plugin class not found!")

    if len(plugin_classes) > 1:
        print("Multiple plugin classes found!")

    return plugin_classes[0][1]

class PluginList:

    def __init__(self, plugin_dirs):
        self._plugin_dirs = [os.path.abspath(os.path.expanduser(d))
                             for d in plugin_dirs]
        self._plugins = {}
        self._info_fname = PLUGIN_INFO_FILENAME

    def find_plugins(self):
        for plugin_dir in self._plugin_dirs:
            for root, dirs, files in os.walk(plugin_dir, topdown=True):
                for name in files:
                    if name != self._info_fname:
                        continue
                    try:
                        plugin_info = self.parse_plugin(root)
                    except Exception as e:
                        error_message = ''
                        if hasattr(e, 'strerror') and e.strerror:
                            error_message = e.strerror
                            if hasattr(e, 'errno') and e.errno:
                                error_message += ' [Errno %d]' % e.errno
                        elif hasattr(e, 'message'):
                            error_message = e.message
                        elif hasattr(e, 'msg'):
                            error_message = e.msg
                        if not error_message:
                            error_message = 'Unknown'
                        print(error_message)
                    else:
                        if plugin_info.name not in self._plugins:
                            self._plugins[plugin_info.name] = plugin_info

    def parse_plugin(self, plugin_directory):
        infofile_path = os.path.join(plugin_directory, self._info_fname)
        cp = parse_info_file(infofile_path)
        plugin_class = get_plugin_class(cp.get('Plugin', 'Name'),plugin_directory)
        return PluginInfo(cp, plugin_class, plugin_directory)

class PluginInfo(object):
    def __init__(self, cp, plugin_class, directory):
        self._cp = cp
        self._plugin_class = plugin_class
        self._path = directory

    def _get_optional_info(self, *args):
        try:
            value = self._cp.get(*args)
        except configparser.Error:
            value = ''
        return value

    @property
    def plugin_class(self):
        return self._plugin_class

    @plugin_class.setter
    def plugin_class(self, value):
        if self._plugin_class is not None:
            raise RuntimeError('Changing a plugin class it not allowed!')
        self._plugins_class = value

    @property
    def name(self):
        return self._cp.get('Plugin', 'Name')

    @property
    def version(self):
        return self._cp.get('Plugin', 'Version')

    @property
    def description(self):
        return self._get_optional_info('Plugin', 'Description')

class PluginObject:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def get_response(self,intent, slots):
        pass

    @abc.abstractmethod
    def has_intent(self,intent):
        pass
