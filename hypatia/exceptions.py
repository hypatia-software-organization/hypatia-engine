class TMXMissingPlayerStartPosition(Exception):
    """TMX file parsed does not have a player start
    position, which is required to create scenes.

    See Also:
        :class:`TMX`

    """

    def __init__(self):
        message = "TMX file missing player_start_position"
        super(TMXMissingPlayerStartPosition, self).__init__(message)


class TMXTooManyTilesheets(Exception):
    """A TMX file was attempted to be imported through
    `TileMap.from_tmx()`, but the TMX defined more than
    one tilesheet. This is a feature Hypatia does not
    support.

    See Also:
        :meth:`TileMap.from_tmx()` and :class:`TMX`.

    """

    def __init__(self):
        """The exception message is this class' docstring.

        Note:
            Mostly scaffolding, plus won't be here for long.

        """

        message = TMXTooManyTilesheets.__docstring__
        super(TMXTooManyTilesheets, self).__init__(message)


class TMXVersionUnsupported(Exception):
    """Attempted to create a TileMap from a TMX map, but
    the TMX map version is unsupported.

    Attribs:
        map_version (str): the version which was attempted

    """

    def __init__(self, map_version):
        """

        Args:
            map_version (str): the map version which is
                unsupported. This becomes the map_version
                attribute.

        """

        message = 'version %s unsupported' % map_version
        super(TMXVersionUnsupported, self).__init__(message)
        self.map_version = map_version


class TMXLayersNotCSV(Exception):
    """The data encoding used for layers during Tilemap.from_tmx()
    is not supported. Only CSV is supported.

    Attribs:
        data_encoding (str): the failed data encoding.

    """

    def __init__(self, data_encoding):
        """

        Args:
            data_encoding (str): the failed data encoding

        """

        message = 'tmx layer data encoding %s unsupported' % data_encoding
        super(TMXLayersNotCSV, self).__init__(message)
        self.data_encodign = data_encoding

