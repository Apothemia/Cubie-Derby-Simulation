from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                             QHBoxLayout, QLabel, QSpinBox)


class CubeListWidgetItem(QWidget):
    def __init__(self, cube_name, parent=None):
        super().__init__(parent)
        self.cube_name = cube_name

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        self.setLayout(layout)

        # Cube name label
        name_label = QLabel(cube_name)
        layout.addWidget(name_label)

        # Position spinbox
        self.position_spin = QSpinBox()
        self.position_spin.setRange(0, 22)
        layout.addWidget(self.position_spin)

        # Stack order spinbox
        self.stack_spin = QSpinBox()
        self.stack_spin.setRange(0, 12)
        layout.addWidget(self.stack_spin)

    def get_values(self):
        return {
            'cube_name': self.cube_name,
            'position': self.position_spin.value(),
            'stack_order': self.stack_spin.value()
        }


class CubeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(2)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        
    def add_cube(self, cube_name):
        item = QListWidgetItem(self)
        widget = CubeListWidgetItem(cube_name)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
        
    def remove_cube(self, cube_name):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget.cube_name == cube_name:
                self.takeItem(i)
                break
                
    def get_all_values(self):
        values = {}
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            values[widget.cube_name] = [widget.position_spin.value(), 
                                      widget.stack_spin.value()]
        return values

    def dropEvent(self, event):
        source_row = self.currentRow()
        super().dropEvent(event)
        dest_row = self.currentRow()
        
        if source_row != dest_row:
            # The order changed, you can handle this if needed
            pass