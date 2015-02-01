#
# This file is part of Neubot <https://www.neubot.org/>.
#
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.
#

""" WWW handler """

import logging
import mimetypes
import os

from . import serializer

class WWWHandler(object):
    """ WWW handler class """

    def __init__(self):
        self.default_file = "index.html"
        self.rootdir = None

    def set_default_file(self, default_file):
        """ Set default file name """
        self.default_file = default_file

    def set_rootdir(self, rootdir):
        """ Allow to override the rootdir """
        if not rootdir:
            logging.debug("www: empty rootdir => no rootdir")
            return
        logging.debug("www: user specified rootdir: %s", rootdir)
        self.rootdir = os.path.abspath(
            os.path.realpath(os.path.abspath(rootdir)))
        logging.debug("www: real rootdir is: %s", self.rootdir)

    def resolve_path(self, path):
        """ Safely maps HTTP path to filesystem path """

        logging.debug("www: rootdir %s", self.rootdir)
        logging.debug("www: original path %s", path)

        path = os.sep.join([self.rootdir, path])
        path = os.path.abspath(path)             # Process "../"s
        path = os.path.realpath(path)            # Resolve symlinks
        path = os.path.abspath(path)             # Just in case

        logging.debug("www: normalized path %s", path)

        if not path.startswith(self.rootdir):
            return

        return path

    @staticmethod
    def guess_mimetype(path):
        """ Guess mimetype of the file at path """
        mimetype, encoding = mimetypes.guess_type(path)
        if not mimetype:
            mimetype = "text/plain"
        return mimetype, encoding

    def _serve_file(self, path):
        """ Serve the file at path """

        if not os.path.isfile(path):
            return serializer.compose_error(404, "Not Found")

        logging.debug("www: url mapped to existing file: %s", path)

        try:
            filep = open(path, "rb")
        except (OSError, IOError):
            return serializer.compose_error(404, "Not Found")

        return self.serve_filep(self, filep)

    def serve_filep(self, filep):
        """ Serve the content of a file """

        mimetype, encoding = self.guess_mimetype(path)

        logging.debug("www: sending file to client")

        return serializer.compose_filep(200, "Ok", {
            "Content-Type": mimetype,
            "Content-Encoding": encoding,  # None is filtered out
        }, filep)

    def serve_directory(self, path):
        """ Serve the directory at path """
        path = os.sep.join([path, self.default_file])
        logging.debug("www: url isdir; trying with: %s", path)
        return self._serve_file(path)

    def __call__(self, request):
        """ Process HTTP request for WWW resource """

        if not self.rootdir:
            logging.warning("www: rootdir is not set")
            return serializer.compose_error(403, "Forbidden")

        logging.debug("www: requested to serve: %s", request.url)

        path = self.resolve_path(request.url)
        if not path:
            return serializer.compose_error(403, "Forbidden")

        logging.debug("www: url mapped to: %s", path)

        if os.path.isdir(path):
            return self.serve_directory(path)
        else:
            return self._serve_file(path)
