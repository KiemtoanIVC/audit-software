from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                           QPushButton, QLabel, QTableWidget,
                           QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
from .materiality_dialog import MaterialityDialog
from ..utils.styles import AppTheme

class BCTCView(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = None
        self.current_job = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Bảng thông tin BCTC
        self.bctc_info_table = QTableWidget()
        self.bctc_info_table.setColumnCount(2)
        self.bctc_info_table.setHorizontalHeaderLabels(["Thông tin", "Giá trị"])
        self.bctc_info_table.horizontalHeader().setStretchLastSection(True)
        
        # Button tính MTY
        self.calc_mty_btn = QPushButton("Tính mức trọng yếu")
        self.calc_mty_btn.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        self.calc_mty_btn.clicked.connect(self.show_materiality_dialog)
        self.calc_mty_btn.setEnabled(False)
        
        layout.addWidget(self.bctc_info_table)
        layout.addWidget(self.calc_mty_btn)
        self.setLayout(layout)

    def set_bctc_data(self, processor, job_data):
        """Nhận dữ liệu BCTC từ JobView"""
        self.processor = processor
        self.current_job = job_data
        
        # Cập nhật giao diện
        self.update_bctc_info()
        self.calc_mty_btn.setEnabled(True)

    def update_bctc_info(self):
        """Cập nhật bảng thông tin BCTC"""
        if not self.current_job or not self.current_job.get('bctc_info'):
            return
            
        items = [
            ("Tên công ty", self.current_job['bctc_info']['company_name']),
            ("Mã số thuế", self.current_job['bctc_info']['tax_code']),
            ("Kỳ báo cáo", f"{self.current_job['bctc_info']['period_from']} - {self.current_job['bctc_info']['period_to']}"),
            ("Tổng tài sản", f"{self.current_job['key_metrics'].get('total_assets', 0):,.0f} VND"),
            ("Doanh thu", f"{self.current_job['key_metrics'].get('revenue', 0):,.0f} VND"),
            ("Lợi nhuận trước thuế", f"{self.current_job['key_metrics'].get('profit_before_tax', 0):,.0f} VND")
        ]
        
        self.bctc_info_table.setRowCount(len(items))
        for row, (key, value) in enumerate(items):
            self.bctc_info_table.setItem(row, 0, QTableWidgetItem(key))
            self.bctc_info_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def show_materiality_dialog(self):
        """Hiển thị dialog tính MTY"""
        if not self.current_job or not self.current_job.get('key_metrics'):
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu BCTC!")
            return
            
        dialog = MaterialityDialog(self)
        # Truyền dữ liệu BCTC cho dialog
        dialog.set_bctc_data(self.current_job)
        dialog.exec()

    def update_financial_data(self, processor):
        """Cập nhật bảng dữ liệu tài chính"""
        if not processor:
            return
            
        metrics = processor.get_key_metrics()
        if not metrics:
            return
            
        # Hiển thị các chỉ tiêu quan trọng
        data_rows = [
            ('total_assets', 'Tổng tài sản'),
            ('equity', 'Vốn chủ sở hữu'),
            ('revenue', 'Doanh thu'),
            ('profit_before_tax', 'Lợi nhuận trước thuế'),
            ('total_expenses', 'Tổng chi phí')
        ]
        
        self.data_table.setRowCount(len(data_rows))
        for row, (key, name) in enumerate(data_rows):
            value = metrics.get(key, 0)
            self.data_table.setItem(row, 0, QTableWidgetItem(key))
            self.data_table.setItem(row, 1, QTableWidgetItem(name))
            self.data_table.setItem(row, 2, QTableWidgetItem(f"{value:,.0f}")) 