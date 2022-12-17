import sys

ME = 1
OPP = 0
NEUTRAL = -1

MINIMUM_RECYCLER_SCRAP_AMOUNT = 20
ALWAYS_BUILD_SCRAP_AMOUNT = 35

def get_tile_distance(tile_one, tile_two):
    return abs(tile_one.x - tile_two.x) + abs(tile_one.y - tile_two.y)

class GameState:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_dict = {}
        self.own_matter = 0
        self.opponent_matter = 0
        self.actions = []
        self.total_recyclers_build = 0
    
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
        #Find spawnable tile closest to enemy units to make sure units are spawned in useful locations

        spawn_tile = None
        closest_enemy_distance = None
        for tile in self.tile_dict.values():
            if (
                tile.can_spawn and 
                tile.units == 0
            ):
                enemies = self.get_occupied_tiles(owner=OPP)
                
                #Find closest enemy
                tile_enemy_distance = None
                for enemy in enemies:
                    distance = get_tile_distance(tile, enemy)
                    if not tile_enemy_distance or tile_enemy_distance < distance:
                        tile_enemy_distance = distance
                if not closest_enemy_distance or tile_enemy_distance < closest_enemy_distance:
                    closest_enemy_distance = tile_enemy_distance
                    spawn_tile = tile
        return spawn_tile

    def find_total_scrap_amount(self, tile):
        total = tile.scrap_amount
        d = (-1, 1)
        adjacent_tiles = []
        #print(f"{self.tile_dict.keys()}", file=sys.stderr, flush=True)
        for dx in d:
            x = tile.x + dx
            y = tile.y
            adjacent_tiles.append((x,y))
        for dy in d:
            x = tile.x
            y = tile.y + dy
            adjacent_tiles.append((x,y))
        
        for x,y in adjacent_tiles:
            adjacent_tile = (x,y) in self.tile_dict.keys() and self.tile_dict[(x,y)]
            if adjacent_tile:
                if adjacent_tile.in_range_of_recycler:
                    return 0
                tile_amount = min(self.tile_dict[(x,y)].scrap_amount, tile.scrap_amount)
                total += tile_amount
        return total

    def find_tile_for_recycler(self):
        build_tile = None
        best_scrap_amount = 0
        minimum_scrap = MINIMUM_RECYCLER_SCRAP_AMOUNT if len(self.recyclers) < 3 else ALWAYS_BUILD_SCRAP_AMOUNT
        for tile in self.tile_dict.values():
            if tile.can_build and not tile.in_range_of_recycler:
                total = self.find_total_scrap_amount(tile)
                if total > minimum_scrap and total > best_scrap_amount:
                    build_tile = tile
                    best_scrap_amount = total
        return build_tile

    def get_occupied_tiles(self, owner=ME):
        units = []
        for tile in self.tile_dict.values():
            if tile.owner == owner and tile.units >= 1:
                units.append(tile)
        units.sort(key = lambda x: x.units)
        return units

    @property
    def recyclers(self):
        recyclers = []
        for tile in self.tile_dict.values():
            if tile.owner == ME and tile.recycler:
                recyclers.append(tile)
        return recyclers

    @property
    def attack_mode(self):
        return len(self.recyclers) > 2

    def execute_build_phase(self):
        available_spawns = self.own_matter // 10
        for i in range(available_spawns):
            build_tile = self.find_tile_for_recycler()
            if build_tile:
                self.actions.append(f"BUILD {build_tile.x} {build_tile.y}")    
                continue
            tile_to_spawn = self.find_tile_to_spawn()
            if tile_to_spawn:
                self.actions.append(f"SPAWN 1 {tile_to_spawn.x} {tile_to_spawn.y}")

    def find_tile_to_move_to(self, unit):
        target_tile = None
        target_distance = None

        for tile in self.tile_dict.values():
            distance = get_tile_distance(tile, unit)

            if (
                (self.attack_mode and tile.owner == OPP and not tile.recycler) or (not self.attack_mode and tile.owner != ME) and
                not tile.friendly_unit_destination and 
                not tile.will_disappear and
                not tile.is_grass and
                (not target_distance or distance < target_distance)
            ):                
                target_tile = tile
                target_distance = distance
            
        if target_tile:
            target_tile.friendly_unit_destination = True
        return target_tile


    def execute_move_phase(self):
        occupied_tiles = self.get_occupied_tiles()
        for tile in occupied_tiles:
            for unit in range(tile.units):
                destination_tile = self.find_tile_to_move_to(tile)
                if destination_tile:
                    self.actions.append(f"MOVE {1} {tile.x} {tile.y} {destination_tile.x} {destination_tile.y}")

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
        self.friendly_unit_destination = False

    def __repr__(self):
        return f"(Tile: {self.x}, {self.y})"

    @property
    def will_disappear(self):
        return self.scrap_amount == 1 and self.in_range_of_recycler

    @property
    def is_grass(self):
        return self.scrap_amount == 0



width, height = [int(i) for i in input().split()]
game_state = GameState(width, height)

while True:
    game_state.own_matter, game_state.opponent_matter = [int(i) for i in input().split()]
    game_state.init_turn_board()
    game_state.execute_move_phase()
    game_state.execute_build_phase()
    game_state.execute_actions()

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    print(game_state.tile_dict, file=sys.stderr, flush=True)
