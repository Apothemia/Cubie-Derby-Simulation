from dataclasses import dataclass
from typing import List
import random


@dataclass
class Cube:
    name: str
    skill_effect: str
    position: int = 0
    stack_order: int = 0
    skill_activated: bool = False
    die_rolled: int = 0
    extra_moves: int = 0
    last_action: dict | None = None

    def __init__(self, game):
        self.game = game

    def take_turn(self) -> None | dict:
        self.last_action = {'cube_name': self.name}

        self.roll_die()
        self._apply_skill_before_move()

        # Find all cubes in the same stack that will move together
        new_position = min(self.position + self.die_rolled + self.extra_moves, self.game.num_of_pads - 1)
        stack = self.game.get_stack_at_position(self.position)
        moving_stack = sorted([c for c in stack if c.stack_order >= self.stack_order],
                              key=lambda x: x.stack_order)

        self._move_stack_to_position(moving_stack, new_position)

        self._apply_skill_after_move()

        return self.last_action

    def roll_die(self) -> None:
        self.die_rolled = random.randint(1, 3)
        self.last_action['die_rolled'] = self.die_rolled

    def _apply_skill_before_move(self) -> None:
        pass

    def _move_stack_to_position(self, moving_stack: List['Cube'], target_position: int):
        target_stack = self.game.get_stack_at_position(target_position)
        for c in target_stack:
            if isinstance(c, Jinhsi):
                c.apply_jinhsi_skill(moving_stack, target_stack)
                break
        max_stack_order = (max(c.stack_order for c in target_stack) + 1) if target_stack else 0
        for i, c in enumerate(moving_stack):
            c.position = target_position
            c.stack_order = max_stack_order + i

    def _apply_skill_after_move(self) -> None:
        self.extra_moves = 0
        self.skill_activated = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Roccia(Cube):
    name = 'Roccia'
    skill_effect = 'Last to move (+2)'

    def _apply_skill_before_move(self) -> None:
        if self == self.game.cubes[-1]:
            self.skill_activated = True
            self.extra_moves = 2
            self.last_action['skill_activated'] = self.skill_effect


class Brant(Cube):
    name = 'Brant'
    skill_effect = 'First to move (+2)'

    def _apply_skill_before_move(self) -> None:
        if self == self.game.cubes[0]:
            self.skill_activated = True
            self.extra_moves = 2
            self.last_action['skill_activated'] = self.skill_effect


class Phoebe(Cube):
    name = 'Phoebe'
    skill_effect = '50% chance for extra (+1)'

    def _apply_skill_before_move(self) -> None:
        if random.random() < 0.5:
            self.skill_activated = True
            self.extra_moves = 1
            self.last_action['skill_activated'] = self.skill_effect


class Zani(Cube):
    name = 'Zani'
    skill_effect = 'Stacked move, next turn (+2)'

    def roll_die(self) -> None:
        self.die_rolled = random.choice([1, 3])
        self.last_action['die_rolled'] = self.die_rolled

    def _move_stack_to_position(self, moving_stack, target_position) -> None:
        if self.skill_activated:
            self.skill_activated = False
            self.extra_moves = 0

        super()._move_stack_to_position(moving_stack, target_position)

        if len(moving_stack) > 1 and random.random() < 0.4:
            self.skill_activated = True
            self.extra_moves = 2
            self.last_action['skill_activated'] = self.skill_effect

    def _apply_skill_after_move(self) -> None:
        pass


class Cartethyia(Cube):
    name = 'Cartethyia'
    skill_effect = 'Ranked last, permanent (+2)'

    def _apply_skill_after_move(self) -> None:
        if not self.skill_activated and self.stack_order == 0 and random.random() < 0.6:
            sorted_cubes = sorted(self.game.cubes, key=lambda x: x.position)
            if self.position == sorted_cubes[0].position:
                self.skill_activated = True
                self.extra_moves = 2
                self.last_action['skill_activated'] = self.skill_effect

    def _apply_skill_before_move(self) -> None:
        pass


class Cantarella(Cube):
    name = 'Cantarella'
    skill_effect = 'Carrying passed cubes forward'

    def _move_stack_to_position(self, moving_stack, target_position) -> None:
        if not self.skill_activated:
            # Check if she passed any cubes
            passed_cubes = [c for c in self.game.cubes
                            if self.position < c.position < target_position]
            if len(passed_cubes) > 0:
                passed_cubes = sorted(passed_cubes, key=lambda c: (-c.position, c.stack_order))
                for i, c in enumerate(passed_cubes):
                    c.position = self.position

                moving_stack = passed_cubes + moving_stack
                self.skill_activated = True
                self.last_action['skill_activated'] = self.skill_effect

        super()._move_stack_to_position(moving_stack, target_position)

    def _apply_skill_after_move(self) -> None:
        pass


class Jinhsi(Cube):
    name = 'Jinhsi'
    skill_effect = 'Cubes above, 40% chance to move to top'

    def apply_jinhsi_skill(self, moving_stack: List['Cube'], target_stack: List['Cube']):
        if random.random() < 0.4:
            target_stack.remove(self)
            moving_stack.append(self)


class Changli(Cube):
    name = 'Changli'
    skill_effect = 'Cubes below, 65% chance to move last next turn'

    def _move_stack_to_position(self, moving_stack: List['Cube'], target_position: int):
        target_stack = self.game.get_stack_at_position(target_position)

        # I don't know which skill triggers first, Changli's or Jinhsi's
        for c in target_stack:
            if isinstance(c, Jinhsi):
                c.apply_jinhsi_skill(moving_stack, target_stack)
                break

        max_stack_order = (max(c.stack_order for c in target_stack) + 1) if target_stack else 0

        if max_stack_order > 0 and random.random() < 0.65:
            self.last_action['skill_activated'] = self.skill_effect

        for i, c in enumerate(moving_stack):
            c.position = target_position
            c.stack_order = max_stack_order + i


class Calcharo(Cube):
    name = 'Calcharo'
    skill_effect = 'Last place (+3)'

    def _apply_skill_before_move(self) -> None:
        self.game.determine_standings()
        if self == self.game.standings[-1]:
            self.extra_moves = 3
            self.last_action['skill_activated'] = self.skill_effect


class Shorekeeper(Cube):
    name = 'Shorekeeper'
    skill_effect = 'Rolls only 2 or 3'

    def roll_die(self) -> None:
        self.die_rolled = random.choice([2, 3])
        self.last_action['die_rolled'] = self.die_rolled


class Camellya(Cube):
    name = 'Camellya'
    skill_effect = '50% chance to get +1 per cube on same pad'

    def take_turn(self) -> None | dict:
        self.last_action = {'cube_name': self.name}

        self.roll_die()
        self._apply_skill_before_move()

        # Find all cubes in the same stack that will move together
        new_position = min(self.position + self.die_rolled + self.extra_moves, self.game.num_of_pads - 1)
        stack = self.game.get_stack_at_position(self.position)

        # Trigger skill
        if len(stack) > 1 and random.random() < 0.5:
            new_position += len(stack) - 1
            for cube in stack:
                if cube.stack_order > self.stack_order:
                    cube.stack_order -= 1
            self.last_action['skill_activated'] = self.skill_effect
            moving_stack = [self]
        else:
            moving_stack = sorted([c for c in stack if c.stack_order >= self.stack_order],
                                  key=lambda x: x.stack_order)

        self._move_stack_to_position(moving_stack, new_position)

        self._apply_skill_after_move()

        return self.last_action


class Carlotta(Cube):
    name = 'Carlotta'
    skill_effect = '28% chance to move twice'

    def _apply_skill_before_move(self) -> None:
        if random.random() < 0.28:
            self.extra_moves = self.die_rolled
            self.last_action['skill_activated'] = self.skill_effect


CUBE_CLASSES = {
    'Roccia': Roccia,
    'Brant': Brant,
    'Phoebe': Phoebe,
    'Zani': Zani,
    'Cartethyia': Cartethyia,
    'Cantarella': Cantarella,
    'Jinhsi': Jinhsi,
    'Changli': Changli,
    'Calcharo': Calcharo,
    'Shorekeeper': Shorekeeper,
    'Camellya': Camellya,
    'Carlotta': Carlotta
}
