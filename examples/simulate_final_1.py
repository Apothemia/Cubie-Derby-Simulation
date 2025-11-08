from utils.game import CubieDerby

REGION = 'eu'
NUMBER_OF_SIMULATIONS = 1_000_000
CUBES = {'eu': ['Calcharo', 'Carlotta', 'Roccia', 'Cantarella']}


if __name__ == '__main__':

    rankings = {cube: 0 for cube in CUBES[REGION]}
    # for result in results:
    #     for cube, wins in result.items():
    #         rankings[cube] += wins

    print('\nResults of the simulation:')
    rankings = sorted(rankings.items(), key=lambda item: item[1], reverse=True)

    for i, (cube, wins) in enumerate(rankings):
        print(f'{i + 1}. {cube} ({wins / NUMBER_OF_SIMULATIONS * 100:4.2f}%)')
