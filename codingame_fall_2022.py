import sys
import math

OWNER = 1
OPPONENT = 0
NEUTRAL = -1


class GameState:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_dict = {}
        self.own_matter = 0
        self.opponent_matter = 0
        self.actions = []
    
    def set_tile(self, position, tile):
        self.tile_dict[position] = tile

    def init_turn_board(self):
        self.actions = []
        for y in range(self.height):
            for x in range(self.width):
                scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in input().split()]

                tile = Tile(
                    x = x,
                    y = y,
                    scrap_amount = scrap_amount, 
                    owner = owner, 
                    units = units, 
                    recycler = recycler, 
                    can_build = can_build,
                    can_spawn = can_spawn, 
                    in_range_of_recycler= in_range_of_recycler
                )
                self.set_tile((x, y), tile)

    def find_tile_to_spawn(self):
        for tile in self.tile_dict.values():
            if tile.can_spawn:
                return tile

    def get_units(self):
        units = []
        for tile in self.tile_dict.values():
            if tile.owner == OWNER and tile.units > 1:
                units.append(tile)
        return units

    def init_build_phase(self):
        available_spawns = self.own_matter // 10
        if available_spawns:
            tile_to_spawn = self.find_tile_to_spawn()
            self.actions.append(f"SPAWN {available_spawns} {tile_to_spawn.x} {tile_to_spawn.y}")

    def init_move_phase(self):
        units = self.get_units()

    def execute_actions(self):
        if self.actions:
            print(";".join(self.actions))
        else:
            print("WAIT")


class Tile:
    def __init__(self, x, y, scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler):
        self.x = x
        self.y = y
        self.scrap_amount = scrap_amount
        self.owner = owner
        self.units = units
        self.recycler = recycler
        self.can_build = can_build
        self.can_spawn = can_spawn
        self.in_range_of_recycler = in_range_of_recycler

    def __repr__(self):
        return f"(Tile: {self.x}, {self.y})"



width, height = [int(i) for i in input().split()]
game_state = GameState(width, height)

while True:
    game_state.own_matter, game_state.opponent_matter = [int(i) for i in input().split()]
    game_state.init_turn_board()
    game_state.init_build_phase()
    game_state.execute_actions()

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    print(game_state.tile_dict, file=sys.stderr, flush=True)
