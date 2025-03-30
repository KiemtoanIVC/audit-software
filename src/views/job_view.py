from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                           QPushButton, QDialog, QLabel, QLineEdit,
                           QDateEdit, QMessageBox, QFileDialog, QTableWidget,
                           QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from ..utils.styles import AppTheme
from ..utils.config_manager import ConfigManager
from ..core.data_processor import FinancialDataProcessor
import json
from datetime import datetime

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
    # Thêm signal
    bctc_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.processor = None
        self.current_job = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(AppTheme.SPACING_MEDIUM)

        # Phần Job
        job_group = QGroupBox("Thông tin Job")
        job_layout = QVBoxLayout()

        # Buttons cho job
        job_buttons = QHBoxLayout()
        
        self.create_job_btn = QPushButton("Tạo Job mới")
        self.create_job_btn.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        self.create_job_btn.clicked.connect(self.create_job)
        
        self.open_job_btn = QPushButton("Mở Job")
        self.open_job_btn.setStyleSheet(AppTheme.BUTTON_STYLE)
        self.open_job_btn.clicked.connect(self.open_job)
        
        job_buttons.addWidget(self.create_job_btn)
        job_buttons.addWidget(self.open_job_btn)
        
        # Thông tin job hiện tại
        self.job_info_table = QTableWidget()
        self.job_info_table.setColumnCount(2)
        self.job_info_table.setHorizontalHeaderLabels(["Thông tin", "Giá trị"])
        self.job_info_table.horizontalHeader().setStretchLastSection(True)
        
        job_layout.addLayout(job_buttons)
        job_layout.addWidget(self.job_info_table)
        job_group.setLayout(job_layout)

        # Phần BCTC
        bctc_group = QGroupBox("Thông tin BCTC")
        bctc_layout = QVBoxLayout()
        
        # Button chọn BCTC
        bctc_header = QHBoxLayout()
        self.select_bctc_btn = QPushButton("Chọn file BCTC")
        self.select_bctc_btn.setStyleSheet(AppTheme.BUTTON_STYLE)
        self.select_bctc_btn.clicked.connect(self.load_bctc)
        self.select_bctc_btn.setEnabled(False)  # Chỉ enable khi đã có job
        bctc_header.addWidget(self.select_bctc_btn)
        
        # Bảng thông tin BCTC
        self.bctc_info_table = QTableWidget()
        self.bctc_info_table.setColumnCount(2)
        self.bctc_info_table.setHorizontalHeaderLabels(["Thông tin", "Giá trị"])
        self.bctc_info_table.horizontalHeader().setStretchLastSection(True)
        
        bctc_layout.addLayout(bctc_header)
        bctc_layout.addWidget(self.bctc_info_table)
        bctc_group.setLayout(bctc_layout)

        # Thêm vào layout chính
        layout.addWidget(job_group)
        layout.addWidget(bctc_group)
        self.setLayout(layout)

    def create_job(self):
        """Tạo job mới"""
        try:
            # Chọn thư mục gốc cho job mới
            dir_path = QFileDialog.getExistingDirectory(
                self,
                "Chọn thư mục lưu Job",
                str(Path.home())
            )
            
            if dir_path:
                # Tạo thư mục job với tên mặc định
                job_path = Path(dir_path) / "New_Job"
                counter = 1
                while job_path.exists():
                    job_path = Path(dir_path) / f"New_Job_{counter}"
                    counter += 1
                
                # Tạo cấu trúc thư mục
                job_path.mkdir(parents=True)
                (job_path / "MauBieu").mkdir()
                (job_path / "DuLieu").mkdir()
                (job_path / "BangChung").mkdir()
                
                # Tạo và lưu thông tin job
                self.current_job = {
                    "path": str(job_path),
                    "name": job_path.name,
                    "created_at": str(datetime.now())
                }
                
                # Lưu thông tin job vào file config trong thư mục job
                self._save_job_config()
                
                # Cập nhật giao diện
                self.update_job_info()
                self.select_bctc_btn.setEnabled(True)
                
                QMessageBox.information(self, "Thành công", "Đã tạo job mới thành công!")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo job: {str(e)}")

    def open_job(self):
        """Mở job đã tồn tại"""
        try:
            dir_path = QFileDialog.getExistingDirectory(
                self,
                "Chọn thư mục Job",
                str(Path.home())
            )
            
            if dir_path:
                job_path = Path(dir_path)
                
                # Kiểm tra cấu trúc thư mục
                required_folders = ["MauBieu", "DuLieu", "BangChung"]
                if not all((job_path / folder).exists() for folder in required_folders):
                    # Tự động tạo các thư mục còn thiếu
                    for folder in required_folders:
                        (job_path / folder).mkdir(exist_ok=True)
                
                # Đọc thông tin job từ file config hoặc tạo mới
                self.current_job = self._load_job_config(job_path)
                if not self.current_job:
                    self.current_job = {
                        "path": str(job_path),
                        "name": job_path.name,
                        "opened_at": str(datetime.now())
                    }
                    self._save_job_config()
                
                # Cập nhật giao diện
                self.update_job_info()
                self.select_bctc_btn.setEnabled(True)
                
                # Lưu đường dẫn job vào config chung
                ConfigManager.save_last_job(str(job_path))
                
                QMessageBox.information(self, "Thành công", "Đã mở job thành công!")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi mở job: {str(e)}")

    def _save_job_config(self):
        """Lưu thông tin job vào file config"""
        if not self.current_job:
            return
            
        try:
            job_path = Path(self.current_job["path"])
            config_file = job_path / "job_config.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_job, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Lỗi khi lưu config job: {str(e)}")

    def _load_job_config(self, job_path: Path) -> dict:
        """Đọc thông tin job từ file config"""
        try:
            config_file = job_path / "job_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Lỗi khi đọc config job: {str(e)}")
        return None

    def restore_job(self, job_path: str):
        """Khôi phục job từ đường dẫn"""
        try:
            path = Path(job_path)
            if path.exists():
                self.current_job = self._load_job_config(path)
                if not self.current_job:
                    self.current_job = {
                        "path": str(path),
                        "name": path.name,
                        "restored_at": str(datetime.now())
                    }
                    self._save_job_config()
                
                # Cập nhật giao diện
                self.update_job_info()
                self.select_bctc_btn.setEnabled(True)
                
                # Khôi phục thông tin BCTC nếu có
                if self.current_job.get('bctc_file'):
                    if Path(self.current_job['bctc_file']).exists():
                        self.update_bctc_info(self.current_job['bctc_file'])
                        
                        # Khởi tạo lại processor với dữ liệu đã lưu
                        self.processor = FinancialDataProcessor()
                        self.processor.company_info = self.current_job['bctc_info']
                        self.processor.key_metrics = self.current_job['key_metrics']
                    else:
                        # File BCTC không còn tồn tại
                        self.current_job.pop('bctc_file', None)
                        self.current_job.pop('bctc_info', None)
                        self.current_job.pop('key_metrics', None)
                        self.current_job.pop('bctc_updated_at', None)
                        self._save_job_config()
                
                return True
                
        except Exception as e:
            print(f"Lỗi khi khôi phục job: {str(e)}")
        return False

    def update_job_info(self):
        """Cập nhật bảng thông tin job"""
        if not self.current_job:
            return
            
        # Cập nhật bảng thông tin
        items = [
            ("Đường dẫn", self.current_job.get("path", "")),
            ("Tên Job", self.current_job.get("name", "")),
            ("Ngày tạo", self.current_job.get("created_at", "")),
            ("Lần mở cuối", self.current_job.get("opened_at", ""))
        ]
        
        self.job_info_table.setRowCount(len(items))
        for row, (key, value) in enumerate(items):
            self.job_info_table.setItem(row, 0, QTableWidgetItem(key))
            self.job_info_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def load_bctc(self):
        """Tải và xử lý file BCTC"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Chọn file BCTC",
                "",
                "XML Files (*.xml)"
            )
            
            if file_name:
                # Khởi tạo processor
                self.processor = FinancialDataProcessor()
                
                # Load và xử lý dữ liệu
                if self.processor.load_xml_data(file_name):
                    # Cập nhật thông tin BCTC vào current_job
                    self.current_job.update({
                        "bctc_file": file_name,
                        "bctc_info": {
                            "company_name": self.processor.company_info['name'],
                            "tax_code": self.processor.company_info['tax_code'],
                            "period_from": self.processor.company_info['period_from'],
                            "period_to": self.processor.company_info['period_to']
                        },
                        "key_metrics": self.processor.get_key_metrics(),
                        "bctc_updated_at": str(datetime.now())
                    })
                    
                    # Lưu thông tin job
                    self._save_job_config()
                    
                    # Emit signal để thông báo BCTC đã được load
                    self.bctc_loaded.emit()
                    
                    # Cập nhật giao diện
                    self.update_bctc_info(file_name)
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể xử lý file BCTC")
                    
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tải BCTC: {str(e)}")

    def update_bctc_info(self, file_name):
        """Cập nhật bảng thông tin BCTC"""
        if not self.current_job.get('bctc_info'):
            return
            
        self.bctc_info_table.setRowCount(6)
        
        # Thêm thông tin
        items = [
            ("Tên file", Path(file_name).name),
            ("Tên công ty", self.current_job['bctc_info']['company_name']),
            ("Mã số thuế", self.current_job['bctc_info']['tax_code']),
            ("Kỳ báo cáo", f"{self.current_job['bctc_info']['period_from']} - {self.current_job['bctc_info']['period_to']}"),
            ("Tổng tài sản", f"{self.current_job['key_metrics'].get('total_assets', 0):,.0f} VND"),
            ("Cập nhật lúc", self.current_job.get('bctc_updated_at', ''))
        ]
        
        for row, (key, value) in enumerate(items):
            self.bctc_info_table.setItem(row, 0, QTableWidgetItem(key))
            self.bctc_info_table.setItem(row, 1, QTableWidgetItem(str(value))) 