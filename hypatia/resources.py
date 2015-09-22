# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""Manage assets and resources.

These are utilities which are commonly utilized
by all modules in Hypatia. It serves for the ugly,
underlying components of miscellaneous actions which
assist other modules, and does not do much on its own.

need to put file handlers in its own module

"""

import os
import zipfile

from hypatia import filehandlers


class Resource(object):
    """A zip archive in the resources directory, located by
    supplying a resource category and name. Files are stored
    as a str, BytesIO, PygAnimation, or ConfigParser, in a
    dictionary. Files are referenced by filepath/filename.

    Attributes:
        files (dict): Key is file name, value can be one of str,
            BytesIO, PygAnim, or ConfigParser objects.

    Example:
        >>> from hypatia import sprites
        >>> resource = Resource('walkabouts', 'debug')
        >>> 'walk_north.gif' in resource
        True
        >>> isinstance(resource['walk_north.gif'],
        ...            sprites.AnimatedSprite)
        True
        >>> resource = Resource('scenes', 'debug')
        >>> resource['tilemap.txt'].startswith('debug')
        True

    """

    FROM_EXTENSION = {
                     '.ini': filehandlers.load_ini,
                     '.gif': filehandlers.load_gif,
                     '.png': filehandlers.load_png,
                     '.txt': filehandlers.load_txt,
                    }

    def __init__(self, resource_category, resource_name):
        """Load a resource ZIP using a category and zip name.

        Args:
            resource_category (str): E.g., tilesheets, walkabouts.
            resource_name (str): E.g., debug.

        """

        # The default path for a resource is:
        #   ./resource_category/resource_name
        # We'll be looking for an archive or directory that
        # looks something like these examples:
        #   * ./resources/walkabouts/hat
        #   * ./resources/scenes/debug.zip
        # Keep in mind that directories are chosen over
        # zip archives (if the names are the same).
        path = os.path.join(
                            'resources',
                            resource_category,
                            resource_name
                           )
        # ... Once files have been collected from the aforementioned
        # path, the files will be passed through their respective
        # file_handler, if available for the given file extension.

        # 1. Create a dictionary, where the key is the file name
        # (including extension) and the value is the result
        # of using x.open(path).read().
        files = {}

        # choose between loading as an unpacked directory, or a zip file.
        # unpacked takes priority.
        if os.path.isdir(path):

            # go through each file in the supplied path, making an
            # entry in the files dictionary, whose value is the
            # file data (bytesio) and key is file name.
            for file_name in os.listdir(path):
                file_data = open(os.path.join(path, file_name)).read()
                files[file_name] = file_data

        # we're dealing with a zip file for our resources
        else:

            with zipfile.ZipFile(path + ".zip") as zip_file:

                for file_name in zip_file.namelist():

                    # because namelist will also generate
                    # the directories
                    if not file_name:

                        continue

                    file_data = zip_file.open(file_name).read()
                    files[file_name] = file_data

        # 2. "Prepare" the "raw file data" from the files
        # dictionary we just created. If a given file's
        # file extension is in file_handlers, the data
        # will be updated by an associated function.
        for file_name in files.keys():
            file_data = files[file_name]
            file_extension = os.path.splitext(file_name)[1]

            # if there is a known "handler" for this extension,
            # we want the file data for this file to be the output
            # of said handler
            if file_extension in Resource.FROM_EXTENSION:
                file_handler = Resource.FROM_EXTENSION[file_extension]
                file_data = file_handler(files, file_name)

            files[file_name] = file_data

        self.files = files

    def __getitem__(self, file_name):

        return self.files[file_name]

    def __contains__(self, item):

        return item in self.files

    def get_type(self, file_extension):
        """Return a dictionary of files which have the file extension
        specified. Remember to include the dot, e.g., ".gif"!

        Arg:
            file_extension (str): the file extension (including dot) of
                the files to return.

        Warning:
            Remember to include the dot in the file extension, e.g., ".gif".

        Returns:
            dict|None: {file name: file content} of files which have the
                file extension specified. If no files match,
                None is returned.

        """

        matching_files = {}

        for file_name, file_content in self.files.items():

            if os.path.splitext(file_name)[1] == file_extension:
                matching_files[file_name] = file_content

        return matching_files or None
