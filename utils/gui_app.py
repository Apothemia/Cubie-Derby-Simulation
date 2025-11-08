import json
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGraphicsView, QGraphicsScene, QMessageBox,
                             QGraphicsTextItem, QGraphicsEllipseItem, QFileDialog, QSplitter,
                             QCheckBox, QSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QBrush
from utils.widgets import CubeListWidget
from utils.game import CubieDerby

CUBE_COLOURS = {
    'Jinhsi': QColor(219, 217, 167),
    'Changli': QColor(255, 154, 99),
    'Shorekeeper': QColor(10, 145, 199),
    'Calcharo': QColor(2, 171, 83),
    'Carlotta': QColor(83, 245, 229),
    'Camellya': QColor(255, 59, 59),
    'Roccia': QColor(212, 0, 255),
    'Brant': QColor(209, 63, 72),
    'Cantarella': QColor(89, 70, 166),
    'Zani': QColor(255, 240, 143),
    'Cartethyia': QColor(143, 255, 163),
    'Phoebe': QColor(219, 201, 0)
}


class CubeVisualisation(QGraphicsEllipseItem):
    def __init__(self, name, x, y, stack_order=0, size=30):
        super().__init__(x, y, size, size)
        self.name = name
        self.stack_order = stack_order

        # Set colour based on the cube name
        self.setBrush(QBrush(CUBE_COLOURS.get(name, QColor(128, 128, 128))))

        # Add a name label
        self.label = QGraphicsTextItem(name[:3], self)
        self.label.setPos(x + 5, y + 5)
        self.label.setFont(QFont('Arial', 8))

        # Stack order indicator
        if stack_order > 0:
            self.order_label = QGraphicsTextItem(str(stack_order), self)
            self.order_label.setPos(x + 20, y)
            self.order_label.setFont(QFont('Arial', 6))


class SimulationPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Game options
        game_options_group = QGroupBox('Game Options')
        game_options_layout = QVBoxLayout()
        game_options_group.setLayout(game_options_layout)

        self.number_of_pads = QSpinBox()
        game_options_layout.addWidget(QLabel('Number of pads:'))
        game_options_layout.addWidget(self.number_of_pads)

        self.randomize_order = QCheckBox('Randomize Order')
        self.randomize_order.setChecked(True)
        game_options_layout.addWidget(self.randomize_order)

        layout.addWidget(game_options_group)

        # Available cubes group
        cubes_group = QGroupBox('Available Cubes')
        cubes_layout = QGridLayout()
        self.cube_checkboxes = {}
        for i, cube in enumerate(CUBE_COLOURS.keys()):
            cb = QCheckBox(cube)
            cb.stateChanged.connect(self.update_starting_positions)
            self.cube_checkboxes[cube] = cb
            cubes_layout.addWidget(cb, i % 6, i // 6)
        cubes_group.setLayout(cubes_layout)
        layout.addWidget(cubes_group)

        # Starting options
        self.starting_positions_group = QGroupBox('Starting Positions')
        self.starting_positions_group.setCheckable(True)
        self.starting_positions_group.setChecked(False)
        positions_layout = QVBoxLayout()
        self.starting_positions_group.setLayout(positions_layout)
        self.cube_list = CubeListWidget()
        positions_layout.addWidget(self.cube_list)
        layout.addWidget(self.starting_positions_group)

        # Simulate button
        self.simulate_button = QPushButton('Simulate Game')
        layout.addWidget(self.simulate_button)

    # noinspection PyUnresolvedReferences
    def update_starting_positions(self):
        checked_cubes = {cube for cube, cb in self.cube_checkboxes.items() if cb.isChecked()}

        for i in range(self.cube_list.count() - 1, -1, -1):
            item = self.cube_list.item(i)
            widget = self.cube_list.itemWidget(item)
            if widget.cube_name not in checked_cubes:
                self.cube_list.takeItem(i)

        current_cubes = {self.cube_list.itemWidget(self.cube_list.item(i)).cube_name
                         for i in range(self.cube_list.count())}
        for cube in checked_cubes:
            if cube not in current_cubes:
                self.cube_list.add_cube(cube)

    def get_simulation_params(self):
        cube_positions = self.cube_list.get_all_values()
        return {
            'cubes': cube_positions.keys(),
            'num_of_pads': self.number_of_pads.value(),
            'starting_positions': cube_positions if self.starting_positions_group.isChecked() else None,
            'randomize_order': self.randomize_order.isChecked()
        }


class VisualisationPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.cube_visualisations: dict | None = None
        self.cube_size = 30
        self.setup_ui()

    # noinspection PyAttributeOutsideInit
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Reading JSON
        self.open_button = QPushButton('Open JSON File', self)
        self.content_label = QLabel('No file selected')
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setWordWrap(True)

        layout.addWidget(self.open_button)
        layout.addWidget(self.content_label)

        # Information labels
        self.info_layout = QHBoxLayout()
        self.round_label = QLabel('Starting Positions')
        self.info_layout.addWidget(self.round_label)
        layout.addLayout(self.info_layout)

        self.action_info_label = QLabel('Action Info: ')
        layout.addWidget(self.action_info_label)

        # Create turn order visualisation
        self.turn_order_layout = QHBoxLayout()

        self.turn_order_label = QLabel('Turn Order')
        self.turn_order_layout.addWidget(self.turn_order_label)
        self.order_view = QGraphicsView()
        self.turn_order_layout.addWidget(self.order_view)

        self.order_scene = QGraphicsScene()
        self.order_view.setScene(self.order_scene)
        self.order_view.setFixedHeight(40)
        self.order_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.order_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addLayout(self.turn_order_layout)

        # Create track visualisation
        self.track_view = QGraphicsView()
        self.track_scene = QGraphicsScene()
        self.track_view.setScene(self.track_scene)
        layout.addWidget(self.track_view)

        # Control buttons
        self.control_layout = QHBoxLayout()
        self.next_round_button = QPushButton('Next Round')
        self.next_round_button.clicked.connect(self.next_round)
        self.next_round_button.setEnabled(False)

        self.prev_action_button = QPushButton('Previous Action')
        self.prev_action_button.clicked.connect(self.prev_action)
        self.prev_action_button.setEnabled(False)

        self.next_action_button = QPushButton('Next Action')
        self.next_action_button.clicked.connect(self.next_action)
        self.next_action_button.setEnabled(False)

        self.control_layout.addWidget(self.next_round_button)
        self.control_layout.addWidget(self.prev_action_button)
        self.control_layout.addWidget(self.next_action_button)
        layout.addLayout(self.control_layout)

        layout.addStretch()

    def update_turn_order(self, cube_size=30, spacing=10):
        self.order_scene.clear()

        if not SimulationData.rounds:
            return

        turn_order = SimulationData.rounds[SimulationData.round_index]['turn_order']

        self.order_scene.setSceneRect(0, 0, 1000, 40)

        for i, cube_name in enumerate(turn_order):
            x = spacing + i * (cube_size + spacing)
            cube = CubeVisualisation(cube_name, x, 5)
            self.order_scene.addItem(cube)

    def draw_track(self, track_height=100, track_width=950):
        self.track_scene.clear()

        if not SimulationData.num_of_pads:
            return

        self.track_scene.addRect(25, track_height, track_width, 10, brush=QBrush(QColor(139, 69, 19)))

        # Draw pads (0 to num_of_pads)
        for i in range(SimulationData.num_of_pads):
            x = 25 + (i * (track_width / (SimulationData.num_of_pads - 1)))
            self.track_scene.addRect(x - 2, track_height - 10, 4, 20, brush=QBrush(QColor(160, 82, 45)))
            pad_text = self.track_scene.addText(str(i))
            pad_text.setPos(x - 5, track_height + 15)

    def update_cube_positions(self, positions: dict,
                              track_height=100, track_width=950, cube_size=30):

        # Clear cubes but keep track
        for item in self.track_scene.items():
            if isinstance(item, CubeVisualisation):
                self.track_scene.removeItem(item)

        # Group cubes by position and sort by stack order
        position_groups = defaultdict(list)
        for cube_name, (pos, stack_order) in positions.items():
            position_groups[pos].append((cube_name, stack_order))

        for pos, cubes in position_groups.items():
            # Sort by stack order (lowest first)
            cubes.sort(key=lambda x: x[1])

            x_pos = 25 + (pos * (track_width / (SimulationData.num_of_pads - 1)))
            y_base = track_height - cube_size

            for i, (cube_name, stack_order) in enumerate(cubes):
                y_offset = y_base - (i * 25)
                cube = CubeVisualisation(cube_name, x_pos - 15, y_offset, stack_order, size=cube_size)
                self.track_scene.addItem(cube)

    def update_action_info(self, action):
        if not action:
            return

        cube_name = action['cube_name']
        die_rolled = action['die_rolled']
        skill_activated = action.get('skill_activated', None)
        info_text = (f'{cube_name} rolled {die_rolled}'
                     + (f' - Skill activated: {skill_activated}' if skill_activated else ''))
        self.action_info_label.setText(info_text)
        self.update_cube_positions(action['positions'])

    def next_action(self):
        self.prev_action_button.setEnabled(True)

        if SimulationData.next_action():
            action = SimulationData.get_current_action()
            self.update_action_info(action)

            if SimulationData.action_index == 0:
                self.round_label.setText(f'Round: {SimulationData.round_index + 1}')
                self.update_turn_order()

            if (SimulationData.round_index == len(SimulationData.rounds) - 1 and
                    SimulationData.action_index == len(SimulationData.rounds[-1]['actions']) - 1):
                self.standings_popup()
                self.next_action_button.setEnabled(False)

    def prev_action(self):
        self.next_action_button.setEnabled(True)

        if SimulationData.prev_action():
            action = SimulationData.get_current_action()
            self.update_action_info(action)

            # Update round info if we moved to the previous round
            self.round_label.setText(f'Round: {SimulationData.round_index + 1}')
            self.update_turn_order()

        elif SimulationData.round_index == 0 and SimulationData.action_index == 0:
            self.prev_action_button.setEnabled(False)
            SimulationData.reset_indices()
            self.round_label.setText('Starting Positions')
            self.action_info_label.setText('Initial positions')
            self.update_cube_positions(SimulationData.starting_positions)
            self.update_turn_order()


    def next_round(self):
        self.prev_action_button.setEnabled(True)

        # Move to the start of the next round
        while SimulationData.next_action():
            if SimulationData.action_index == 0:
                break

        action = SimulationData.get_current_action()
        if action:
            self.update_action_info(action)
            self.round_label.setText(f'Round: {SimulationData.round_index + 1}')
            self.update_turn_order()
        else:
            self.standings_popup()
            self.next_action_button.setEnabled(False)

    def standings_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle('Final Standings')
        msg.setText('\n'.join(SimulationData.standings))
        msg.exec_()


class CubieDerbyVisualiser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cubie Derby Visualiser')
        self.setGeometry(100, 100, 1200, 600)

        # Create UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        # Add panels
        self.simulation_panel = SimulationPanel()
        self.simulation_panel.setFixedWidth(300)
        self.simulation_panel.simulate_button.clicked.connect(self.on_start_simulation)
        splitter.addWidget(self.simulation_panel)

        self.visualisation_panel = VisualisationPanel()
        self.visualisation_panel.open_button.clicked.connect(self.on_open_json_file)
        splitter.addWidget(self.visualisation_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def on_open_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open JSON File', '../examples', 'JSON Files (*.json);;All Files (*)')

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                self.visualisation_panel.content_label.setText('Error: The selected file is not a valid JSON file.')
            except Exception as e:
                print(e)
                self.visualisation_panel.content_label.setText(f'Error: {str(e)}')
        else:
            self.visualisation_panel.content_label.setText('No file selected.')

        SimulationData.load_data(data)
        self.update_visualization()

    def on_start_simulation(self):
        params = self.simulation_panel.get_simulation_params()
        simulation = CubieDerby(record_actions=True, **params)
        simulation.play_game()
        SimulationData.load_data(simulation.get_game_data())
        self.update_visualization()

    def update_visualization(self):
        self.visualisation_panel.draw_track()
        self.visualisation_panel.update_cube_positions(SimulationData.starting_positions)
        self.enable_controls()

    def enable_controls(self):
        self.visualisation_panel.next_round_button.setEnabled(True)
        self.visualisation_panel.next_action_button.setEnabled(True)


class SimulationData:
    num_of_cubes = None
    num_of_pads = None
    starting_positions = None
    rounds = None
    standings = None
    round_index = 0
    action_index = -1

    @classmethod
    def load_data(cls, data):
        cls.num_of_cubes = data['number_of_cubes']
        cls.num_of_pads = data['number_of_pads']
        cls.starting_positions = data['starting_positions']
        cls.rounds = data['rounds']
        cls.standings = data['standings']
        cls.reset_indices()

    @classmethod
    def reset_indices(cls):
        cls.round_index = 0
        cls.action_index = -1

    @classmethod
    def get_current_action(cls):
        if cls.round_index >= 0 and cls.action_index >= 0:
            return cls.rounds[cls.round_index]['actions'][cls.action_index]
        return None

    @classmethod
    def next_action(cls):
        if cls.round_index < 0:
            cls.round_index = 0
            cls.action_index = 0
            return True

        if cls.action_index + 1 < len(cls.rounds[cls.round_index]['actions']):
            cls.action_index += 1
            return True

        elif cls.round_index + 1 < len(cls.rounds):
            cls.round_index += 1
            cls.action_index = 0
            return True

        return False

    @classmethod
    def prev_action(cls):
        if cls.action_index > 0:
            cls.action_index -= 1
            return True
        elif cls.round_index > 0:
            cls.round_index -= 1
            cls.action_index = len(cls.rounds[cls.round_index]['actions']) - 1
            return True
        return False


def run_app():
    app = QApplication([])
    visualizer = CubieDerbyVisualiser()
    visualizer.show()
    app.exec_()


if __name__ == '__main__':
    run_app()
