from utils.game import CubieDerby

NUMBER_OF_SIMULATIONS = 1_000_000
pos_for_6_man_race = {0: [3, 0], 1: [2, 1], 2: [2, 0], 3: [1, 1], 4: [1, 0], 5: [0, 0]}

previous_standings = {
    'eu': ['Roccia', 'Cantarella', 'Brant', 'Phoebe', 'Zani', 'Cartethyia'],
    'na': ['Zani', 'Cantarella', 'Roccia', 'Cartethyia', 'Brant', 'Phoebe'],
    'sea': ['Brant', 'Zani', 'Phoebe', 'Cartethyia', 'Roccia', 'Cantarella']
}

if __name__ == '__main__':
    current_standings = previous_standings['eu']

    new_starting_positions = {current_standings[i]: pos_for_6_man_race[i]
                              for i in range(len(current_standings))}

    rankings = {cube: 0 for cube in current_standings}

    for i in range(NUMBER_OF_SIMULATIONS):
        race = CubieDerby(cubes=current_standings, pad_num=27)
        race.play_game(starting_positions=new_starting_positions)

        # Only give points to the first place
        standings = race.standings
        rankings[standings[0]] += 1

        if i % (NUMBER_OF_SIMULATIONS // 10) == 0:
            print(f'> {i} simulations done')

    for ranking in sorted(rankings.items(), key=lambda item: item[1]):
        print(ranking)
