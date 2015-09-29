import os
import io
import pkgutil
import threading

class VFSException(Exception):
    pass

class MountPointInUse(VFSException):
    def __init__(self, path):
        self.path = path

class IsADirectory(VFSException):
    def __init__(self, path):
        self.path = path

class NotADirectory(VFSException):
    def __init__(self, path):
        self.path = path

class FileNotFound(VFSException):
    def __init__(self, path):
        self.path = path

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
            raise MountPointInUse(mountpoint)

        self._mountpoints[mountpoint] = provider
        self._mountpoints[mountpoint]._cache_files()

    def unmount(self, mountpoint):
        """Unmount a provider from the given mountpoint.

        Args:
          mountpoint (str): Mountpoint to unmount
        """

        if not mountpoint in self._mountpoints:
            return

        del self._mountpoints[mountpoint]

    def split(self, path):
        return self.normalize(path).split(self.PATH_SEPARATOR)

    def normalize(self, path):
        # Remove root.
        if path.startswith(self.PATH_SEPARATOR):
            path = path[len(self.PATH_SEPARATOR):]

        # Split path into directory pieces and remove empty or redundant directories.
        pieces = [ piece for piece in path.split(self.PATH_SEPARATOR)
                   if piece and piece != '.' ]

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
                return not self._mountpoints[lookpath].isdir(spath[len(looked):])

        return False

    def list(self, path):
        """Returns a list of the files and subdirectories in the given path,
        including whether the given path is a file or directory.
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

        raise FileNotFound(path)

class VFSProvider(object):
    def __init__(self):
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
        dir = self._contents

        for fragment in spath:
            if fragment not in dir["children"]:
                raise FileNotFound(VFS.PATH_SEPARATOR.join(spath))

            dir = dir["children"][fragment]

        return dir["isdir"]

    def list(self, spath):
        dir = self._contents
        for fragment in spath:
            if fragment not in dir["children"]:
                raise FileNotFound(VFS.PATH_SEPARATOR.join(spath))

            dir = dir["children"][fragment]

        if not dir["isdir"]:
            raise NotADirectory(VFS.PATH_SEPARATOR.join(spath))

        out = []
        for i in dir["children"].keys():
            out.append({
                "name": i,
                "isdir": dir["children"][i]["isdir"],
            })

        return out

    def exists(self, spath):
        dir = self._contents

        for fragment in spath:
            if fragment not in dir["children"]:
                return False

            dir = dir["children"][fragment]

        return True

    def open(self, spath):
        dir = self._contents
        for fragment in spath:
            if fragment not in dir["children"]:
                raise FileNotFound(VFS.PATH_SEPARATOR.join(spath))

            dir = dir["children"][fragment]

        if dir["isdir"]:
            raise IsADirectory(path)

        return dir["contents"]

    def _cache_files(self):
        pass

class FilesystemProvider(VFSProvider):
    def __init__(self, path):
        super(FilesystemProvider, self).__init__()
        self._path = os.path.abspath(path)

    def _cache_files(self):
        for root, dirs, files in os.walk(self._path):
            sroot = root[len(self._path):].split(os.sep)[1:]

            nest = self._contents
            for fragment in sroot:
                if not fragment in nest["children"]:
                    nest["children"][fragment] = {
                        "isdir": True,
                        "children": {},
                    }

                nest = nest["children"][fragment]

            for file in files:
                path = os.path.join(self._path, *sroot)
                path = os.path.join(path, file)
                with open(path, 'r') as fh:
                    contents = fh.read()

                nest["children"][file] = {
                    "isdir": False,
                    "contents": io.BytesIO(contents),
                }

