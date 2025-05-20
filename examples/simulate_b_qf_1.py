from utils.game import CubieDerby

NUMBER_OF_SIMULATIONS = 1_000_000
CUBES = ['Roccia', 'Brant', 'Phoebe', 'Cantarella']

if __name__ == '__main__':
    rankings = {cube: 0 for cube in CUBES}

    for i in range(NUMBER_OF_SIMULATIONS):
        race = CubieDerby()
        race.play_game(cubes=CUBES, num_of_pads=23)

        # Only give points to the first place
        standings = race.game_summary['standings']
        rankings[standings[0]] += 1

        if i % (NUMBER_OF_SIMULATIONS // 10) == 0:
            print(f'> {i} simulations done')

    print('\nResults of the simulation:')
    rankings = sorted(rankings.items(), key=lambda item: item[1], reverse=True)

    for i, (cube, wins) in enumerate(rankings):
        print(f'{i + 1}. {cube} ({wins / NUMBER_OF_SIMULATIONS * 100:4.2f}%)')
