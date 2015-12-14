# -*- coding: utf-8 -*-
"""
    drupan.engine

    The engine is part of drupan that holds all plugins and subsystems
    together and runs the actual site creation process.
"""

from .site import Site
from .config import Config
from .template import Render
from .serve import http


class Engine(object):
    """Drupan engine doing all the work"""
    def __init__(self):
        self.site = Site()
        self.config = Config()
        self.reader = None
        self.writer = None
        self.plugins = list()
        self.renderer = None
        self.deployment = None

    def prepare_engine(self):
        """get all subsystems and plugins setup"""
        if self.config.reader:
            imported = self._load_module(self.config.reader, "inout", "Reader")
            self.reader = imported.Reader(self.site, self.config)

        if self.config.writer:
            imported = self._load_module(self.config.writer, "inout", "Writer")
            self.writer= imported.Writer(self.site, self.config)

        for name in self.config.plugins:
            imported = self._load_module(name, "plugins", "Plugin")
            plugin = imported.Plugin(self.site, self.config)
            self.plugins.append(plugin)

        self.renderer = Render(self.site, self.config)

        if self.config.deployment:
            imported = self._load_module(
                self.config.deployment,
                "deployment",
                "Deploy",
            )
            self.deployment = imported.Deploy(self.site, self.config)

    @staticmethod
    def _load_module(name, base_name, kind):
        """Load a drupan module and return it.

        :param name: name of the module to load
        :param base_name: base path for drupan standard module
        :param kind: class to import
        :returns: imported class from `name`
        """
        try:
            plugin_name = "drupan{0}".format(name)
            return __import__(plugin_name, fromlist=[kind])
        except ImportError:
            plugin_name = "drupan.{0}.{1}".format(base_name, name)
            return __import__(plugin_name, fromlist=[kind])

    def run(self):
        """run the site generation process"""
        self.reader.run()
        for plugin in self.plugins:
            plugin.run()
        self.renderer.run()
        self.writer.run()

    def serve(self):
        """serve the generated site"""
        http(self.config.get_option("writer", "directory"))

    def deploy(self):
        """deploy the generated site"""
        if not self.deployment:
            return

        self.deployment.run()
