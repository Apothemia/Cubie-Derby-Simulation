from utils.game import CubieDerby

if __name__ == '__main__':
    playing_cubes = ['Brant', 'Zani', 'Cantarella', 'Phoebe', 'Roccia', 'Cartethyia']

    placement_race = CubieDerby(cubes=playing_cubes, pad_num=23)
    placement_race.play_game()
    placement_race.write_results_to_json('./placement_race_results.json')
