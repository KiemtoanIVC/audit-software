from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class UtilityView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tab Tiện ích"))
        self.setLayout(layout)
