from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class FormView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tab Mẫu biểu kiểm toán"))
        self.setLayout(layout)
