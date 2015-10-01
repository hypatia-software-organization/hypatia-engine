class Scene(object):
    def __init__(self, tilemap, player_start_pos, human_player, npcs):
        self.tilemap = tilemap
        self.player_start_position = player_start_pos
        self.human_player = human_player
        self.npcs = npcs
