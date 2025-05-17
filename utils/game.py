import random
from typing import List
from dataclasses import dataclass
import json
from utils.jsontools import CompactJSONEncoder


@dataclass
class Cube:
    name: str
    position: int = 0
    stack_order: int = 0  # 0 -> bottom of stack
    skill_activated: str | None = None
    extra_moves: int = 0

    def roll_die(self) -> int:
        if self.name == 'Zani':
            return random.choice([1, 3])
        return random.randint(1, 3)

    def apply_skill(self, info: 'CubieDerby', turn_order: List['Cube']) -> int:
        extra = 0

        if self.name == 'Roccia' and self == turn_order[-1]:
            extra = 2
            self.skill_activated = 'Last to move (+2)'

        elif self.name == 'Brant' and self == turn_order[0]:
            extra = 2
            self.skill_activated = 'First to move (+2)'

        elif self.name == 'Phoebe' and random.random() < 0.5:
            extra = 1
            self.skill_activated = '50% chance for extra (+1)'

        elif self.name == 'Zani' and info.zani_triggered:
            info.zani_triggered = False
            extra = 2

        return extra


class CubieDerby:
    def __init__(self, cubes, pad_num):
        self.cubes = [Cube(cube) for cube in cubes]
        self.num_of_pads = pad_num
        self.rounds: List[dict] = []
        self.round_number = 0
        self.finished = False
        self.standings: List[str] = []
        self.starting_positions = None

        # Global Skill Variables
        self.cantarella_triggered: bool = False
        self.cartethyia_triggered: bool = False
        self.zani_triggered: bool = False

    def play_game(self,
                  starting_positions: dict = None,
                  randomize_order: bool = True):

        if randomize_order:
            random.shuffle(self.cubes)

        if starting_positions is not None:
            for cube in self.cubes:
                cube.position, cube.stack_order = starting_positions[cube.name]
        else:
            # Stack everyone on starting pad
            for cube_idx in range(len(self.cubes)):
                self.cubes[cube_idx].stack_order = 5 - cube_idx
            starting_positions = {cube.name: [cube.position, cube.stack_order] for cube in self.cubes}

        self.starting_positions = starting_positions

        while not self.finished:
            self.play_round()
            random.shuffle(self.cubes)

    def play_round(self):
        self.round_number += 1
        turn_order = self.cubes

        actions_in_round = []
        for cube in turn_order:
            if self.finished:
                break

            cube.skill_activated = None

            die_roll = cube.roll_die()
            extra_movement = cube.apply_skill(self, turn_order) + cube.extra_moves
            total_movement = die_roll + extra_movement

            self.move_cube(cube, total_movement)

            # Cartethyia post-move skill condition
            if cube.name == 'Cartethyia' and not self.cartethyia_triggered:
                sorted_cubes = sorted(self.cubes, key=lambda x: x.position)
                if cube.stack_order == 0 and cube.position == sorted_cubes[0].position:
                    if random.random() < 0.6:
                        cube.cartethyia_triggered = True
                        cube.extra_moves = 2
                        cube.skill_activated = 'Ranked last, permanent (+2)'

            # Record action
            actions_in_round.append({
                'cube_name': cube.name,
                'die_rolled': str(die_roll) + (f' + {extra_movement}' if extra_movement != 0 else ''),
                'skill_activated': cube.skill_activated,
                'positions': {c.name: (c.position, c.stack_order) for c in self.cubes},
            })

            # Check for winner
            if cube.position + 1 >= self.num_of_pads:
                self.finished = True
                self.determine_standings()
                break

        self.rounds.append({
            'actions': actions_in_round,
            'turn_order': [c.name for c in turn_order]
        })

    def get_stack_at_position(self, position: int) -> List[Cube]:
        return sorted(
            [c for c in self.cubes if c.position == position],
            key=lambda x: x.stack_order
        )

    def move_cube(self, cube: Cube, movement: int):
        # Find all cubes in the same stack (including this one)
        stack = self.get_stack_at_position(cube.position)
        moving_cubes = [c for c in stack if c.stack_order >= cube.stack_order]

        # Zani during-move skill condition
        if cube.name == 'Zani' and len(moving_cubes) > 1 and random.random() < 0.4:
            self.zani_triggered = True
            cube.skill_activated = 'Stacked move, next turn (+2)'

        new_position = min(cube.position + movement, self.num_of_pads - 1)

        # Cantarella during-move skill condition
        if cube.name == 'Cantarella' and not self.cantarella_triggered:
            # Check if she passed any cubes
            passed_cubes = [c for c in self.cubes if cube.position < c.position < new_position]
            if len(passed_cubes) > 0:
                passed_cubes = sorted(passed_cubes, key=lambda c: (-c.position, c.stack_order))
                for i, c in enumerate(passed_cubes):
                    c.position = cube.position

                moving_cubes = passed_cubes + moving_cubes

                self.cantarella_triggered = True
                cube.skill_activated = 'Carrying passed cubes forward.'

        # Check if moving onto another stack
        target_stack = self.get_stack_at_position(new_position)
        max_stack_order = (max(c.stack_order for c in target_stack) + 1) if target_stack else 0
        for i, c in enumerate(moving_cubes):
            c.position = new_position
            c.stack_order = max_stack_order + i

    def determine_standings(self):
        # Sort cubes by position (descending) and stack order (descending)
        sorted_cubes = sorted(self.cubes, key=lambda x: (-x.position, -x.stack_order))
        self.standings = [cube.name for cube in sorted_cubes]

    def write_results_to_json(self, fp):
        result = {
            'rounds': self.rounds,
            'standings': self.standings,
            'starting_positions': self.starting_positions,
            'number_of_cubes': len(self.cubes),
            'number_of_pads': self.num_of_pads
        }
        with open(fp, 'w') as out_file:
            # noinspection PyTypeChecker
            json.dump(result, out_file, cls=CompactJSONEncoder, indent=2)
