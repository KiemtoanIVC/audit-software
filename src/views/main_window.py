from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt
from .job_view import JobView
from .form_view import FormView
from .utility_view import UtilityView
from ..utils.config_manager import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần mềm Kiểm toán")
        self.setMinimumSize(1024, 768)
        
        # Widget chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout chính
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.setup_tabs()
        
        layout.addWidget(self.tab_widget)
        
        # Khôi phục job cuối cùng
        self.restore_last_job()

    def setup_tabs(self):
        """Thiết lập các tab"""
        # Tab Tạo/Mở Job
        self.job_tab = JobView()
        self.tab_widget.addTab(self.job_tab, "Tạo/Mở Job")
        
        # Tab Mẫu biểu
        form_tab = FormView()
        self.tab_widget.addTab(form_tab, "Mẫu biểu kiểm toán")
        
        # Tab Tiện ích
        utility_tab = UtilityView()
        self.tab_widget.addTab(utility_tab, "Tiện ích")

    def restore_last_job(self):
        """Khôi phục job cuối cùng"""
        last_job_path = ConfigManager.get_last_job_path()
        if last_job_path:
            self.job_tab.restore_job(last_job_path) 