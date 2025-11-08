import json
import random
from typing import List
from utils.jsontools import CompactJSONEncoder

STANDING_TO_POSITIONS = {
    4: {0: [3, 0], 1: [2, 0], 2: [1, 0], 3: [0, 0]},
    6: {0: [3, 0], 1: [2, 1], 2: [2, 0], 3: [1, 1], 4: [1, 0], 5: [0, 0]}
}


class CubieDerby:
    def __init__(self,
                 cubes: List[str],
                 num_of_pads: int,
                 starting_positions: dict = None,
                 randomize_order: bool = True,
                 record_actions: bool = False):
        from utils.cubes import CUBE_CLASSES, Cube

        self.cubes = [CUBE_CLASSES[cube](self) for cube in cubes]
        self.num_of_pads = num_of_pads
        self.starting_positions = starting_positions
        self.randomize_order = randomize_order
        self.record_actions = record_actions
        self.num_of_cubes = len(cubes)

        # Game specific variables
        self.is_game_finished: bool | None = None
        self.standings: List['Cube'] | None = None
        self.rounds: List | None = None

    def play_game(self):
        self.is_game_finished = False
        self.rounds = []

        if self.randomize_order:
            random.shuffle(self.cubes)

        if self.starting_positions is not None:
            for cube in self.cubes:
                cube.position, cube.stack_order = self.starting_positions[cube.name]
        else:
            # Stack everyone on the starting pad
            for cube_idx in range(len(self.cubes)):
                self.cubes[cube_idx].stack_order = len(self.cubes) - 1 - cube_idx
            self.starting_positions = {cube.name: [cube.position, cube.stack_order]
                                       for cube in self.cubes}

        while not self.is_game_finished:
            changli_cube = self.play_round()
            random.shuffle(self.cubes)
            if changli_cube is not None:
                self.cubes.remove(changli_cube)
                self.cubes.append(changli_cube)

    def play_round(self):
        turn_order = self.cubes

        changli_cube = None
        actions_in_round = []
        for cube in turn_order:
            if self.is_game_finished:
                break

            action = cube.take_turn()
            if self.record_actions:
                action['positions'] = {c.name: (c.position, c.stack_order)
                                       for c in self.cubes}
                actions_in_round.append(action)

            # Trigger Changli's skill for next round
            if action['cube_name'] == 'Changli' and action.get('skill_activated', None):
                changli_cube = cube

            # Check for the winner
            if cube.position + 1 >= self.num_of_pads:
                self.is_game_finished = True
                self.determine_standings()
                break

        if self.record_actions:
            self.rounds.append({
                'actions': actions_in_round,
                'turn_order': [c.name for c in turn_order]
            })

        return changli_cube

    def get_stack_at_position(self, position: int) -> List:
        return [c for c in self.cubes if c.position == position]

    def determine_standings(self):
        # Sort cubes by position (descending) and stack order (descending)
        self.standings = sorted(self.cubes, key=lambda x: (-x.position, -x.stack_order))

    def get_game_data(self):
        return {
            'number_of_cubes': self.num_of_cubes,
            'number_of_pads': self.num_of_pads,
            'starting_positions': self.starting_positions,
            'rounds': self.rounds,
            'standings': [cube.name for cube in self.standings]
        }

    def write_results_to_json(self, fp):
        with open(fp, 'w') as out_file:
            json.dump(self.get_game_data(), out_file, cls=CompactJSONEncoder, indent=2)
