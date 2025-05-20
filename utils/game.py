import json
import random
import typing
from typing import List
from utils.jsontools import CompactJSONEncoder

STANDING_TO_POSITIONS = {
    4: {0: [3, 0], 1: [2, 0], 2: [1, 0], 3: [0, 0]},
    6: {0: [3, 0], 1: [2, 1], 2: [2, 0], 3: [1, 1], 4: [1, 0], 5: [0, 0]}
}


class CubieDerby:
    def __init__(self):
        # Game specific variables
        self.cubes = None
        self.num_of_cubes = None
        self.num_of_pads = None
        self.starting_positions = None
        self.is_game_finished = None
        self.standings: List[str] | None = None
        self.game_summary: dict | None = None

    def play_game(self,
                  cubes: List[str],
                  num_of_pads: int,
                  starting_positions: dict = None,
                  randomize_order: bool = True,
                  ):

        from utils.cubes import CUBE_CLASSES
        self.cubes = [CUBE_CLASSES[cube](self) for cube in cubes]
        self.num_of_cubes = len(cubes)
        self.num_of_pads = num_of_pads
        self.is_game_finished = False
        self.game_summary = {
            'number_of_cubes': self.num_of_cubes,
            'number_of_pads': self.num_of_pads,
            'starting_positions': {},
            'rounds': [],
        }

        if randomize_order:
            random.shuffle(self.cubes)

        if starting_positions is not None:
            for cube in self.cubes:
                cube.position, cube.stack_order = starting_positions[cube.name]
        else:
            # Stack everyone on the starting pad
            for cube_idx in range(len(self.cubes)):
                self.cubes[cube_idx].stack_order = len(self.cubes) - 1 - cube_idx
            starting_positions = {cube.name: [cube.position, cube.stack_order]
                                  for cube in self.cubes}

        self.game_summary['starting_positions'] = starting_positions

        while not self.is_game_finished:
            self.play_round()
            random.shuffle(self.cubes)

        self.game_summary['standings'] = [cube.name for cube in self.standings]

    def play_round(self):
        turn_order = self.cubes

        actions_in_round = []
        for cube in turn_order:
            if self.is_game_finished:
                break

            action = cube.take_turn()
            action['positions'] = {c.name: (c.position, c.stack_order) for c in self.cubes}
            actions_in_round.append(action)

            # Check for the winner
            if cube.position + 1 >= self.num_of_pads:
                self.is_game_finished = True
                self.determine_standings()
                break

        self.game_summary['rounds'].append({
            'actions': actions_in_round,
            'turn_order': [c.name for c in turn_order]
        })

    def get_stack_at_position(self, position: int) -> List:
        return [c for c in self.cubes if c.position == position]

    def determine_standings(self):
        # Sort cubes by position (descending) and stack order (descending)
        self.standings = sorted(self.cubes, key=lambda x: (-x.position, -x.stack_order))

    def write_results_to_json(self, fp):
        with open(fp, 'w') as out_file:
            json.dump(self.game_summary, out_file, cls=CompactJSONEncoder, indent=2)
