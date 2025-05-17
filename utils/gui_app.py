import json
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGraphicsView, QGraphicsScene, QMessageBox,
                             QGraphicsTextItem, QGraphicsEllipseItem, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QBrush


class CubeVisualisation(QGraphicsEllipseItem):
    def __init__(self, name, x, y, stack_order=0):
        size = 30
        super().__init__(x, y, size, size)
        self.name = name
        self.stack_order = stack_order

        # Set color based on cube name
        colors = {
            'Roccia': QColor(212, 0, 255),
            'Brant': QColor(209, 63, 72),
            'Cantarella': QColor(89, 70, 166),
            'Zani': QColor(255, 240, 143),
            'Cartethyia': QColor(143, 255, 163),
            'Phoebe': QColor(219, 201, 0)
        }
        self.setBrush(QBrush(colors.get(name, QColor(128, 128, 128))))

        # Add name label
        self.label = QGraphicsTextItem(name[:3], self)
        self.label.setPos(x + 5, y + 5)
        self.label.setFont(QFont('Arial', 8))

        # Stack order indicator
        if stack_order > 0:
            self.order_label = QGraphicsTextItem(str(stack_order), self)
            self.order_label.setPos(x + 20, y)
            self.order_label.setFont(QFont('Arial', 6))


class CubieDerbyVisualiser(QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cubie Derby Visualiser')
        self.setGeometry(100, 100, 1000, 600)

        # Variables for visualisation
        self.num_of_cubes = None
        self.rounds = None
        self.standings = None
        self.num_of_pads = None
        self.round_index = -1
        self.action_index = -1

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Reading JSON
        self.open_button = QPushButton('Open JSON File', self)
        self.open_button.clicked.connect(self.open_json_file)

        self.content_label = QLabel('No file selected')
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setWordWrap(True)

        layout.addWidget(self.open_button)
        layout.addWidget(self.content_label)

        # Information labels
        self.info_layout = QHBoxLayout()
        self.round_label = QLabel('Starting Positions')

        self.turn_order_label = QLabel('Turn Order: ')
        self.action_info_label = QLabel('Action Info: ')

        self.info_layout.addWidget(self.round_label)
        self.info_layout.addWidget(self.turn_order_label)
        self.info_layout.addWidget(self.action_info_label)
        layout.addLayout(self.info_layout)

        # Create track visualization
        self.track_view = QGraphicsView()
        self.track_scene = QGraphicsScene()
        self.track_view.setScene(self.track_scene)

        layout.addWidget(self.track_view)

        # Control buttons
        self.control_layout = QHBoxLayout()
        self.next_round_button = QPushButton('Next Round')
        self.next_round_button.clicked.connect(self.next_round)
        self.next_round_button.setEnabled(False)
        self.next_action_button = QPushButton('Next Action')
        self.next_action_button.clicked.connect(self.next_action)
        self.next_action_button.setEnabled(False)

        self.control_layout.addWidget(self.next_round_button)
        self.control_layout.addWidget(self.next_action_button)
        layout.addLayout(self.control_layout)

    def open_json_file(self):
        # Open race results json file
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON File', '', 'JSON Files (*.json);;All Files (*)')

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)

                self.content_label.setText(f'File loaded successfully! {file_path}\n\n')
                self.num_of_cubes = data['number_of_cubes']
                self.rounds = data['rounds']
                self.standings = data['standings']
                self.num_of_pads = data['number_of_pads']
                self.round_index = -1
                self.action_index = -1
                self.draw_track()
                self.update_cube_positions(data['starting_positions'])
                self.next_round_button.setEnabled(True)

            except json.JSONDecodeError:
                self.content_label.setText('Error: The selected file is not a valid JSON file.')
            except Exception as e:
                self.content_label.setText(f'Error: {str(e)}')
        else:
            self.content_label.setText('No file selected.')

    def draw_track(self):
        self.track_scene.clear()

        track_height = 100
        track_width = 950
        self.track_scene.addRect(25, track_height, track_width, 10, brush=QBrush(QColor(139, 69, 19)))

        # Draw pads (0 to num_of_pads)
        for i in range(self.num_of_pads):
            x = 25 + (i * (track_width / (self.num_of_pads - 1)))
            self.track_scene.addRect(x - 2, track_height - 10, 4, 20, brush=QBrush(QColor(160, 82, 45)))
            pad_text = self.track_scene.addText(str(i))
            pad_text.setPos(x - 5, track_height + 15)

    def update_cube_positions(self, positions: dict):
        # Clear cubes but keep track
        for item in self.track_scene.items():
            if isinstance(item, CubeVisualisation):
                self.track_scene.removeItem(item)

        track_height = 100
        track_width = 950

        # Group cubes by position and sort by stack order
        position_groups = defaultdict(list)
        for cube_name, (pos, stack_order) in positions.items():
            position_groups[pos].append((cube_name, stack_order))

        for pos, cubes in position_groups.items():
            # Sort by stack order (lowest first)
            cubes.sort(key=lambda x: x[1])

            x_pos = 25 + (pos * (track_width / (self.num_of_pads - 1)))
            y_base = track_height - 30

            for i, (cube_name, stack_order) in enumerate(cubes):
                y_offset = y_base - (i * 25)
                cube = CubeVisualisation(cube_name, x_pos - 15, y_offset, stack_order)
                self.track_scene.addItem(cube)

    def next_action(self):
        self.action_index += 1
        action = self.rounds[self.round_index]['actions'][self.action_index]

        # Update action info
        cube_name = action['cube_name']
        die_rolled = action['die_rolled']
        skill_activated = action['skill_activated']

        info_text = (f'{cube_name} rolled {die_rolled}'
                     + (f' - Skill activated: {skill_activated}' if skill_activated else ''))
        self.action_info_label.setText(info_text)

        self.update_cube_positions(action['positions'])

        # Check if the action is the last action in that round
        if self.action_index + 1 == len(self.rounds[self.round_index]['actions']):
            self.next_action_button.setEnabled(False)
            # Check if it's also the last round -> The game has ended
            if self.round_index + 1 == len(self.rounds):
                self.next_round_button.setEnabled(False)
                msg = QMessageBox()
                msg.setWindowTitle('Final Standings')
                msg.setText('\n'.join(self.standings))
                msg.exec_()

    def next_round(self):
        self.action_index = -1
        self.round_index += 1

        # Update round info
        self.round_label.setText(f'Round: {self.round_index + 1}')
        self.turn_order_label.setText(f'Turn Order: {self.rounds[self.round_index]["turn_order"]}')
        self.next_action_button.setEnabled(True)


def run_app():
    app = QApplication([])
    visualizer = CubieDerbyVisualiser()
    visualizer.show()
    app.exec_()
