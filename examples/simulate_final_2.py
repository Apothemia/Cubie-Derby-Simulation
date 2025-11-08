from utils.game import CubieDerby
import multiprocessing as mp

NUMBER_OF_SIMULATIONS = 1_000_000
REGION = 'eu'
CUBES = {'eu': {'Carlotta': [3, 0],
                'Calcharo': [2, 0],
                'Cantarella': [1, 0],
                'Roccia': [0, 0]},
         'na': {
             'Roccia': [3, 0],
             'Phoebe': [2, 0],
             'Brant': [1, 0],
             'Zani': [0, 0]
         }}


def _run_sim_batch(p_id, simulation_count, ):
    local_rankings = {c: 0 for c in CUBES[REGION].keys()}

    for _ in range(simulation_count):
        race = CubieDerby(cubes=list(local_rankings.keys()),
                          num_of_pads=27,
                          starting_positions=CUBES[REGION])
        race.play_game()
        data = race.get_game_data()
        standings = data['standings']
        local_rankings[standings[0]] += 1

    return local_rankings


def run_full_simulation(number_of_simulations: int):
    num_processes = max(1, mp.cpu_count() - 1)
    sims_per_process = number_of_simulations // num_processes

    rankings = {c: 0 for c in CUBES[REGION].keys()}

    with mp.Pool(processes=num_processes) as pool:
        results = pool.starmap(_run_sim_batch, [(i, sims_per_process,) for i in range(num_processes)])

    for result in results:
        for c, w in result.items():
            rankings[c] += w

    return rankings


if __name__ == '__main__':
    simulation_rankings = run_full_simulation(NUMBER_OF_SIMULATIONS)

    print('\nResults of the simulation:')
    simulation_rankings = sorted(simulation_rankings.items(), key=lambda item: item[1], reverse=True)

    for i, (cube, wins) in enumerate(simulation_rankings):
        print(f'{i + 1}. {cube} ({wins / NUMBER_OF_SIMULATIONS * 100:4.2f}%)')
