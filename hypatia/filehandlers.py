"""File handlers for Resources.

"""

import os
from io import BytesIO

try:
    import ConfigParser as configparser
    from cStringIO import StringIO

except ImportError:
    import configparser
    from io import StringIO


def load_png(files, file_name):
    """Return an BytesIO object based on supplied file. This is
    a file handler for Resource.

    Args:
        files (dict): Resources files, whereas key is the file name,
            and the value is the untouched file contents itself.
        file_name (str): File from "files" to use for making an
            AnimatedSprite object.

    Returns:
        AnimatedSprite: --

    See Also:
        * Resources.__init__()
        * animations.AnimatedSprite

    """

    return BytesIO(files[file_name])


def load_txt(files, file_name):
    """Return a decoded string based on supplied file. This is
    a file handler for Resource.

    Args:
        files (dict): Resource files, whereas key is the file
            name and the value is the untouched file contents
            itself.
        file_name (StR): File from "files" to use for making
            an animatedSprite object.

    Returns:
        AnimatedSprite: --

    See Also:
        * Resources.__init__()
        * animations.AnimatedSprite

    """

    return files[file_name].decode('utf-8')


def load_gif(files, file_name):
    """Return an AnimatedSprite object based on a bytesio
    object. This is a file handler.

    Args:
        files (dict): Resources files, whereas key is the file name,
            and the value is the untouched file contents itself.
        file_name (str): File from "files" to use for making an
            AnimatedSprite object.

    Returns:
        AnimatedSprite: --

    See Also:
        * Resources.__init__()
        * animations.AnimatedSprite

    """

    # forgive me for this most hackey of ways to avoid
    # a circular dependency
    from hypatia.sprites import AnimatedSprite

    file_data = files[file_name]

    # NOTE: i used to handle this just in
    # Resources.__init__()
    gif_bytesio = BytesIO(file_data)

    # get the corersponding INI which configures our anchor points
    # for this gif, from the files
    gif_name_no_ext = os.path.splitext(file_name)[0]

    try:
        anchor_ini_name = gif_name_no_ext + '.ini'
        anchor_config_ini = files[anchor_ini_name]

        # if the INI file has not already been parsed into
        # ConfigParser object, we'll do that now, so we
        # can accurately construct our AnimatedSprite.
        try:
            anchor_config_ini.sections()
        except AttributeError:
            anchor_config_ini = load_ini(files, anchor_ini_name)

    except KeyError:
        anchor_config_ini = None

    return AnimatedSprite.from_file(gif_bytesio, anchor_config_ini)


def load_ini(files, file_name):
    """Return a ConfigParser object based on a bytesio
    object. This is a file handler.

    Args:
        files (dict): Resources files, whereas key is the file name,
            and the value is a BytesIO object of said file.
        file_name (str): File from "files" to use for making a
            ConfigParser object.

    Returns:
        ConfigParser: --

    See Also:
        Resources.__init__()

    """

    file_data = files[file_name]

    # i used to do this in Resources.__init__()
    file_data = file_data.decode('utf-8')

    file_data = StringIO(file_data)
    config = configparser.ConfigParser()

    # NOTE: this still works in python 3, though it was
    # replaced by config.read_file()
    config.readfp(file_data)

    return config
