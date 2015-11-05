import os
import io
import pkgutil
import threading


class VFSException(Exception):
    pass


class MountPointInUseException(VFSException):
    pass


class IsADirectoryException(VFSException):
    pass


class NotADirectoryException(VFSException):
    pass


class FileNotFoundException(VFSException):
    pass


class VFS(object):
    PATH_SEPARATOR = "/"

    def __init__(self):
        self._lock = threading.RLock()
        self._mountpoints = {}

    def mount(self, mountpoint, provider):
        """Mount the given provider at the specified mountpoint.

        Args:
            mountpoint (str): Mountpoint to use
            provider (hypatia.vfs.VFSProvider): Provider to mount
        """

        if mountpoint in self._mountpoints:
            raise MountPointInUseException(mountpoint)

        self._mountpoints[mountpoint] = provider
        self._mountpoints[mountpoint].cache_files()

    def unmount(self, mountpoint):
        """Unmount a provider from the given mountpoint.

        Args:
            mountpoint (str): Mountpoint to unmount
        """

        if mountpoint not in self._mountpoints:
            return

        del self._mountpoints[mountpoint]

    def split(self, path):
        """Split a path into it's parts.

        Returns:
            list: The parts of the path
        """

        return self.normalize(path).split(self.PATH_SEPARATOR)

    def normalize(self, path):
        """Normalize a path.

        Examples:
            >>> normalize("/path/../otherpath")
            ['otherpath']
        """

        # Remove root.
        if path.startswith(self.PATH_SEPARATOR):
            path = path[len(self.PATH_SEPARATOR):]

        # Split path into directory pieces and remove empty or redundant
        # directories.

        pieces = [piece for piece in path.split(self.PATH_SEPARATOR)
                  if piece and piece != '.']

        # Remove parent directory entries.
        while '..' in pieces:
            i = pieces.index('..')
            del pieces[i]
            # The preceding directory too, of course.
            if i > 0:
                del pieces[i - 1]

        return self.PATH_SEPARATOR + self.PATH_SEPARATOR.join(pieces)

    def isdir(self, path):
        """Returns whether or not the given path is a directory.

        Args:
            path (str): Path to check
        """

        spath = self.split(path)

        # work forwards and try and find a mountpoint matching the file's path
        looked = []
        for i in spath:
            looked.append(i)
            lookpath = VFS.PATH_SEPARATOR.join(looked)

            if lookpath in self._mountpoints:
                return self._mountpoints[lookpath].isdir(spath[len(looked):])

        return False

    def isfile(self, path):
        """Returns whether or not the given path is a file.

        Arguments:
            path (str): Path to check
        """

        spath = self.split(path)

        # work forwards and try and find a mountpoint matching the file's path
        looked = []
        for i in spath:
            looked.append(i)
            lookpath = VFS.PATH_SEPARATOR.join(looked)

            if lookpath in self._mountpoints:
                return not self._mountpoints[lookpath].isdir(spath[len(looked):])

        return False

    def list(self, path):
        """Return a list of the files in the given directory path.

        Returns:
            a list of dictionaries, one for each file/directory in the
            target directory, of the following format::

                {
                    "name": "filename",
                    "isdir": False,
                }
        """

        spath = self.split(path)
        looked = []
        for i in spath:
            looked.append(i)
            lookpath = VFS.PATH_SEPARATOR.join(looked)

            if lookpath in self._mountpoints:
                return self._mountpoints[lookpath].list(spath[len(looked):])

        return []

    def exists(self, path):
        """Returns whether or not a file exists at the given path.

        Args:
          path (str): Path to check
        """

        spath = self.split(path)

        # work forwards and try and find a mountpoint matching the file's path
        looked = []
        for i in spath:
            looked.append(i)
            lookpath = VFS.PATH_SEPARATOR.join(looked)

            if lookpath in self._mountpoints:
                return self._mountpoints[lookpath].exists(spath[len(looked):])

        return False

    def open(self, path):
        """Open a file with the given path. This returns a (read-only) BytesIO
        object.

        Args:
          path (str): Path to open
        """

        # TODO: Support read/write access, file modes. Implement this with a
        # File object that controls read/writing to the provider. See the
        # rave project's File class for details on how this should be
        # implemented.

        spath = self.split(path)

        # work forwards and try and find a mountpoint matching the file's path
        looked = []
        for i in spath:
            looked.append(i)
            lookpath = VFS.PATH_SEPARATOR.join(looked)

            if lookpath in self._mountpoints:
                return self._mountpoints[lookpath].open(spath[len(looked):])

        raise FileNotFoundException(path)


class VFSProvider(object):
    def __init__(self):
        """A base virtual filesystem provider. This class on it's own does not
        store any files, it must be subclassed and the `cache_files()`
        function implemented in the subclass.
        """

        # _contents = {
        #     "dirname": {
        #         "isdir": True,
        #         "children": {
        #             "test": {
        #                 "isdir": False,
        #                 "contents": BytesIO(b"test"),
        #             }
        #         },
        #     },
        # }
        self._contents = {"isdir": True, "children": {}}

    def isdir(self, spath):
        """Returns whether or not the path given is a directory.

        Returns:
            bool: Whether or not the path is a directory
        """
        dir = self._contents

        for fragment in spath:
            if fragment not in dir["children"]:
                raise FileNotFoundException(VFS.PATH_SEPARATOR.join(spath))

            dir = dir["children"][fragment]

        return dir["isdir"]

    def list(self, spath):
        """Return a list of the files in the given directory path.

        Returns:
            a list of dictionaries, one for each file/directory in the
            target directory, of the following format::

                {
                    "name": "filename",
                    "isdir": False,
                }

        """

        dir = self._contents
        for fragment in spath:
            if fragment not in dir["children"]:
                raise FileNotFoundException(VFS.PATH_SEPARATOR.join(spath))

            dir = dir["children"][fragment]

        if not dir["isdir"]:
            raise NotADirectoryException(VFS.PATH_SEPARATOR.join(spath))

        out = []
        for i in dir["children"].keys():
            out.append({
                "name": i,
                "isdir": dir["children"][i]["isdir"],
            })

        return out

    def exists(self, spath):
        """Determines whether or not the path given exists in the filesystem.

        Returns:
            bool: Whether or not the path exists
        """

        dir = self._contents

        for fragment in spath:
            if fragment not in dir["children"]:
                return False

            dir = dir["children"][fragment]

        return True

    def open(self, spath):
        """Open a file from the virtual file system.

        Returns:
            io.BytesIO: a file-like object
        """

        dir = self._contents
        for fragment in spath:
            if fragment not in dir["children"]:
                raise FileNotFoundException(VFS.PATH_SEPARATOR.join(spath))

            dir = dir["children"][fragment]

        if dir["isdir"]:
            raise IsADirectoryException(path)

        return dir["contents"]

    def cache_files(self):
        """Cache files in the filesystem.
        """

        pass


class FilesystemProvider(VFSProvider):
    def __init__(self, path):
        """A VFS provider that takes files from the local file system.

        Arguments:
            path (str): The path to load files from
        """

        super(FilesystemProvider, self).__init__()
        self._path = os.path.abspath(path)

    def cache_files(self):
        """Caches files from the local file system.
        """

        for root, dirs, files in os.walk(self._path):
            sroot = root[len(self._path):].split(os.sep)[1:]

            nest = self._contents
            for fragment in sroot:
                if fragment not in nest["children"]:
                    nest["children"][fragment] = {
                        "isdir": True,
                        "children": {},
                    }

                nest = nest["children"][fragment]

            for file in files:
                path = os.path.join(self._path, *sroot)
                path = os.path.join(path, file)
                with open(path, 'rb') as fh:
                    contents = fh.read()

                nest["children"][file] = {
                    "isdir": False,
                    "contents": io.BytesIO(contents),
                }
