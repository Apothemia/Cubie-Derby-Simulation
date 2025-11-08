from utils.game import CubieDerby

if __name__ == '__main__':
    playing_cubes = ['Jinhsi', 'Shorekeeper', 'Carlotta', 'Calcharo']
    placement_race = CubieDerby(record_actions=True, cubes=playing_cubes, num_of_pads=23)
    placement_race.play_game()
    placement_race.write_results_to_json('./placement_race_results.json')
