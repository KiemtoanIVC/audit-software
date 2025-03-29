from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QDialog, QLabel, QLineEdit,
                           QDateEdit, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from pathlib import Path
from ..utils.styles import AppTheme
from ..utils.config_manager import ConfigManager

class JobCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo Job Mới")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppTheme.BACKGROUND};
            }}
        """)
        self.base_path = None
        
        # Khởi tạo các controls
        self.client_input = QLineEdit()
        self.contract_input = QLineEdit()
        self.date_input = QDateEdit()
        self.period_input = QLineEdit()
        self.industry_input = QLineEdit()
        self.path_input = QLineEdit()
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(AppTheme.SPACING_MEDIUM)
        layout.setContentsMargins(AppTheme.SPACING_LARGE, 
                                AppTheme.SPACING_LARGE, 
                                AppTheme.SPACING_LARGE, 
                                AppTheme.SPACING_LARGE)

        # Form container
        form_container = QWidget()
        form_container.setObjectName("panel")
        form_container.setStyleSheet(AppTheme.PANEL_STYLE)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(AppTheme.SPACING_MEDIUM)

        # Path selection
        path_layout = self._create_path_section()
        form_layout.addLayout(path_layout)

        # Form fields
        fields = [
            ("Tên khách hàng:", self.client_input),
            ("Số hợp đồng:", self.contract_input),
            ("Ngày hợp đồng:", self.date_input),
            ("Kỳ kiểm toán:", self.period_input),
            ("Ngành nghề:", self.industry_input)
        ]

        for label_text, widget in fields:
            field_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet(AppTheme.LABEL_STYLE)
            widget.setStyleSheet(AppTheme.INPUT_STYLE)
            field_layout.addWidget(label, 1)
            field_layout.addWidget(widget, 2)
            form_layout.addLayout(field_layout)

        layout.addWidget(form_container)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet(AppTheme.BUTTON_STYLE)
        save_btn.clicked.connect(self.validate_and_accept)
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet(AppTheme.BUTTON_STYLE.replace(AppTheme.PRIMARY, AppTheme.SECONDARY))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_path_section(self):
        path_layout = QHBoxLayout()
        path_label = QLabel("Thư mục lưu job:")
        path_label.setStyleSheet(AppTheme.LABEL_STYLE)
        
        self.path_input = QLineEdit()
        self.path_input.setStyleSheet(AppTheme.INPUT_STYLE)
        self.path_input.setReadOnly(True)
        
        browse_btn = QPushButton("Chọn thư mục")
        browse_btn.setStyleSheet(AppTheme.BUTTON_STYLE)
        browse_btn.clicked.connect(self.browse_directory)
        
        path_layout.addWidget(path_label, 1)
        path_layout.addWidget(self.path_input, 2)
        path_layout.addWidget(browse_btn)
        
        return path_layout

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục lưu Job",
            str(Path.home())
        )
        if dir_path:
            self.base_path = dir_path
            self.path_input.setText(dir_path)

    def validate_and_accept(self):
        if not self.base_path:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn thư mục lưu job!")
            return
        if not self.client_input.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên khách hàng!")
            return
        if not self.contract_input.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số hợp đồng!")
            return
        self.accept()

    def get_job_data(self):
        contract_date = self.date_input.date().toPyDate()
        return {
            "client_name": self.client_input.text(),
            "contract_number": self.contract_input.text(),
            "contract_date": contract_date.strftime("%Y-%m-%d"),
            "audit_period": self.period_input.text(),
            "industry": self.industry_input.text(),
            "base_path": self.base_path
        }

class JobView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_job = None

    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {AppTheme.BACKGROUND};
            }}
        """)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(AppTheme.SPACING_LARGE)
        main_layout.setContentsMargins(AppTheme.SPACING_LARGE, 
                                     AppTheme.SPACING_LARGE, 
                                     AppTheme.SPACING_LARGE, 
                                     AppTheme.SPACING_LARGE)

        # Left panel
        left_panel = self._create_left_panel()
        main_layout.addLayout(left_panel, 1)

        # Right panel
        right_panel = self._create_right_panel()
        main_layout.addLayout(right_panel, 2)

        self.setLayout(main_layout)

    def _create_left_panel(self):
        panel = QVBoxLayout()
        
        # Button container
        button_container = QWidget()
        button_container.setObjectName("panel")
        button_container.setStyleSheet(AppTheme.PANEL_STYLE)
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(AppTheme.SPACING_MEDIUM)

        create_btn = QPushButton("Tạo Job Mới")
        create_btn.setStyleSheet(AppTheme.BUTTON_STYLE)
        create_btn.clicked.connect(self.show_create_dialog)
        button_layout.addWidget(create_btn)

        open_btn = QPushButton("Mở Job")
        open_btn.setStyleSheet(AppTheme.BUTTON_STYLE)
        open_btn.clicked.connect(self.open_job)
        button_layout.addWidget(open_btn)

        button_layout.addStretch()
        panel.addWidget(button_container)
        panel.addStretch()
        
        return panel

    def _create_right_panel(self):
        panel = QVBoxLayout()
        
        # Info container
        info_container = QWidget()
        info_container.setObjectName("panel")
        info_container.setStyleSheet(AppTheme.PANEL_STYLE)
        info_layout = QVBoxLayout(info_container)

        title = QLabel("Thông tin Job")
        title.setStyleSheet(f"""
            QLabel {{
                color: {AppTheme.PRIMARY};
                font-size: {AppTheme.FONT_LARGE}px;
                font-weight: bold;
            }}
        """)
        info_layout.addWidget(title)

        self.job_info = QLabel("Chưa có job nào được chọn")
        self.job_info.setObjectName("info_panel")
        self.job_info.setStyleSheet(AppTheme.INFO_PANEL_STYLE)
        self.job_info.setWordWrap(True)
        info_layout.addWidget(self.job_info)

        panel.addWidget(info_container)
        panel.addStretch()
        
        return panel

    def show_create_dialog(self):
        dialog = JobCreationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            job_data = dialog.get_job_data()
            try:
                from src.modules.job.job_creator import JobCreator
                creator = JobCreator()
                job = creator.create_job(job_data)
                self.current_job = job
                self.update_job_info()
                ConfigManager.save_last_job(job['path'])
                QMessageBox.information(self, "Thành công", "Đã tạo job mới!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tạo job: {str(e)}")

    def open_job(self):
        job_path = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục Job",
            str(Path.home())
        )
        if job_path:
            self.restore_job(job_path)

    def restore_job(self, job_path: str):
        """Khôi phục job từ đường dẫn"""
        try:
            from src.modules.job.job_creator import JobCreator
            creator = JobCreator()
            job = creator.open_job(job_path)
            self.current_job = job
            self.update_job_info()
            ConfigManager.save_last_job(job_path)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở job: {str(e)}")

    def update_job_info(self):
        if self.current_job:
            info_text = f"""
            <h3>Thông tin Job</h3>
            <p><b>Khách hàng:</b> {self.current_job.get('client_name')}</p>
            <p><b>Số hợp đồng:</b> {self.current_job.get('contract_number')}</p>
            <p><b>Ngày hợp đồng:</b> {self.current_job.get('contract_date')}</p>
            <p><b>Kỳ kiểm toán:</b> {self.current_job.get('audit_period')}</p>
            <p><b>Ngành nghề:</b> {self.current_job.get('industry')}</p>
            <p><b>Trạng thái:</b> {self.current_job.get('status')}</p>
            """
            self.job_info.setText(info_text) 