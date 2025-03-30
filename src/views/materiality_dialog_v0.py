from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton,
                           QTextEdit, QMessageBox, QGridLayout, QTabWidget,
                           QTableWidget, QTableWidgetItem, QFileDialog, QWidget)
from PyQt6.QtCore import Qt
import sys
from pathlib import Path
import logging
from datetime import datetime
from src.models.materiality_result import MaterialityResult, MaterialityResultManager
from src.core.materiality_calculator import (MaterialityCalculator, UserType, 
                                           Benchmark, AuditYear, RiskLevel)
from src.core.data_processor import FinancialDataProcessor

# Thêm thư mục gốc vào PYTHONPATH
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

class MaterialityDialog(QDialog):
    """Dialog tính toán mức trọng yếu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.calculator = None
        self.processor = None
        self.company_info = None
        self.key_metrics = None
        self.result_manager = MaterialityResultManager(Path(__file__).parent.parent.parent)
        
        # Thiết lập cửa sổ
        self.setWindowTitle("Xác định mức trọng yếu")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Thiết lập window flags để có thể phóng to, thu nhỏ
        self.setWindowFlags(
            Qt.WindowType.Window |  # Cửa sổ độc lập
            Qt.WindowType.WindowMinMaxButtonsHint |  # Nút phóng to, thu nhỏ
            Qt.WindowType.WindowCloseButtonHint  # Nút đóng
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tạo tab widget
        tab_widget = QTabWidget()
        
        # Tab 1: Thông tin BCTC
        self.setup_bctc_tab(tab_widget)
        
        # Tab 2: Tính toán MTY
        self.setup_calculation_tab(tab_widget)
        
        # Tab 3: Kết quả
        self.setup_result_tab(tab_widget)
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
    def setup_bctc_tab(self, tab_widget):
        """Thiết lập tab thông tin BCTC"""
        bctc_tab = QWidget()
        layout = QVBoxLayout()
        
        # Phần chọn file
        file_group = QGroupBox("Thông tin file BCTC")
        file_layout = QGridLayout()
        
        # Button chọn file
        self.select_file_btn = QPushButton("Chọn file BCTC")
        self.select_file_btn.clicked.connect(self.load_bctc)
        
        # Bảng thông tin file
        self.file_info_table = QTableWidget()
        self.file_info_table.setColumnCount(2)
        self.file_info_table.setHorizontalHeaderLabels(["Thông tin", "Giá trị"])
        self.file_info_table.horizontalHeader().setStretchLastSection(True)
        
        file_layout.addWidget(self.select_file_btn, 0, 0)
        file_layout.addWidget(self.file_info_table, 1, 0)
        file_group.setLayout(file_layout)
        
        # Bảng thông tin cơ bản
        metrics_group = QGroupBox("Thông tin cơ bản")
        metrics_layout = QVBoxLayout()
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Chỉ tiêu", "Giá trị (VND)"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        
        metrics_layout.addWidget(self.metrics_table)
        metrics_group.setLayout(metrics_layout)
        
        layout.addWidget(file_group)
        layout.addWidget(metrics_group)
        bctc_tab.setLayout(layout)
        
        tab_widget.addTab(bctc_tab, "1. Thông tin BCTC")
        
    def setup_calculation_tab(self, tab_widget):
        """Thiết lập tab tính toán MTY"""
        calc_tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Giảm khoảng cách giữa các widget
        
        # 1. Người sử dụng BCTC
        user_group = QGroupBox("1. Người sử dụng chính của BCTC")
        user_layout = QVBoxLayout()
        user_layout.setSpacing(5)  # Giảm khoảng cách giữa các checkbox
        self.user_checkboxes = {}
        
        for user_type in UserType:
            checkbox = QCheckBox(user_type.value)
            self.user_checkboxes[user_type] = checkbox
            user_layout.addWidget(checkbox)
            
        user_group.setLayout(user_layout)
        
        # 2. Thông tin kiểm toán
        criteria_group = QGroupBox("2. Thông tin kiểm toán")
        criteria_layout = QGridLayout()
        criteria_layout.setSpacing(10)  # Giảm khoảng cách giữa các widget
        
        # Combo boxes
        self.benchmark_combo = QComboBox()
        self.year_combo = QComboBox()
        self.risk_combo = QComboBox()
        
        for benchmark in Benchmark:
            self.benchmark_combo.addItem(benchmark.value, benchmark)
        for year in AuditYear:
            self.year_combo.addItem(year.value, year)
        for risk in RiskLevel:
            self.risk_combo.addItem(risk.value, risk)
            
        # Labels
        self.value_label = QLabel()
        self.suggested_percentage_label = QLabel()
        
        # Thêm trường nhập tỷ lệ %
        self.percentage_edit = QLineEdit()
        self.percentage_edit.setPlaceholderText("Nhập tỷ lệ % (để trống để dùng tỷ lệ đề xuất)")
        
        # Layout cho các widget
        criteria_layout.addWidget(QLabel("Tiêu chí:"), 0, 0)
        criteria_layout.addWidget(self.benchmark_combo, 0, 1)
        criteria_layout.addWidget(QLabel("Năm kiểm toán:"), 1, 0)
        criteria_layout.addWidget(self.year_combo, 1, 1)
        criteria_layout.addWidget(QLabel("Mức độ rủi ro:"), 2, 0)
        criteria_layout.addWidget(self.risk_combo, 2, 1)
        criteria_layout.addWidget(QLabel("Giá trị:"), 3, 0)
        criteria_layout.addWidget(self.value_label, 3, 1)
        criteria_layout.addWidget(QLabel("Tỷ lệ % đề xuất:"), 4, 0)
        criteria_layout.addWidget(self.suggested_percentage_label, 4, 1)
        criteria_layout.addWidget(QLabel("Tỷ lệ % tùy chọn:"), 5, 0)
        criteria_layout.addWidget(self.percentage_edit, 5, 1)
        
        criteria_group.setLayout(criteria_layout)
        
        # Nút tính toán
        calculate_btn = QPushButton("Tính toán")
        calculate_btn.clicked.connect(self.calculate_materiality)
        
        # Thêm các widget vào layout chính
        layout.addWidget(user_group)
        layout.addWidget(criteria_group)
        layout.addWidget(calculate_btn)
        layout.addStretch()  # Đẩy các widget lên trên
        
        calc_tab.setLayout(layout)
        tab_widget.addTab(calc_tab, "2. Tính toán MTY")

        # Connect signals
        self.benchmark_combo.currentIndexChanged.connect(self.update_values)
        self.year_combo.currentIndexChanged.connect(self.update_values)
        self.risk_combo.currentIndexChanged.connect(self.update_values)
        
    def setup_result_tab(self, tab_widget):
        """Thiết lập tab kết quả"""
        result_tab = QWidget()
        layout = QVBoxLayout()
        
        # Bảng kết quả
        result_group = QGroupBox("Kết quả tính toán")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Chỉ tiêu", "Giá trị (VND)"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # Phần giải thích
        explanation_group = QGroupBox("Giải thích")
        explanation_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        explanation_layout.addWidget(self.result_text)
        explanation_group.setLayout(explanation_layout)
        
        # Nút tải xuống
        download_btn = QPushButton("Tải xuống kết quả")
        download_btn.clicked.connect(self.save_results)
        
        layout.addWidget(result_group)
        layout.addWidget(explanation_group)
        layout.addWidget(download_btn)
        result_tab.setLayout(layout)
        
        tab_widget.addTab(result_tab, "3. Kết quả")
        
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
                    self.company_info = self.processor.company_info
                    self.key_metrics = self.processor.get_key_metrics()
                    
                    # Cập nhật bảng thông tin file
                    self.update_file_info_table(file_name)
                    
                    # Cập nhật bảng metrics
                    self.update_metrics_table()
                    
                    # Khởi tạo calculator
                    self.calculator = MaterialityCalculator()
                    
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể xử lý file BCTC")
                    
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tải BCTC: {str(e)}")
            
    def update_file_info_table(self, file_name):
        """Cập nhật bảng thông tin file"""
        if not self.company_info:
            self.file_info_table.setRowCount(1)
            self.file_info_table.setItem(0, 0, QTableWidgetItem("Trạng thái"))
            self.file_info_table.setItem(0, 1, QTableWidgetItem("Chưa tải BCTC"))
            return
        
        self.file_info_table.setRowCount(4)
        
        # Thêm thông tin
        items = [
            ("Tên file", Path(file_name).name),
            ("Tên công ty", self.company_info['name']),
            ("Mã số thuế", self.company_info['tax_code']),
            ("Kỳ báo cáo", f"{self.company_info['period_from']} - {self.company_info['period_to']}")
        ]
        
        for row, (key, value) in enumerate(items):
            self.file_info_table.setItem(row, 0, QTableWidgetItem(key))
            self.file_info_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
    def update_metrics_table(self):
        """Cập nhật bảng thông tin cơ bản"""
        if not self.key_metrics:
            self.metrics_table.setRowCount(1)
            self.metrics_table.setItem(0, 0, QTableWidgetItem("Trạng thái"))
            self.metrics_table.setItem(0, 1, QTableWidgetItem("Chưa có dữ liệu"))
            return
        
        self.metrics_table.setRowCount(len(self.key_metrics))
        
        for row, (key, value) in enumerate(self.key_metrics.items()):
            # Chuyển key thành tên hiển thị
            display_name = {
                'total_assets': 'Tổng tài sản',
                'equity': 'Vốn chủ sở hữu',
                'revenue': 'Doanh thu',
                'profit_before_tax': 'Lợi nhuận trước thuế',
                'total_expenses': 'Tổng chi phí'
            }.get(key, key)
            
            self.metrics_table.setItem(row, 0, QTableWidgetItem(display_name))
            self.metrics_table.setItem(row, 1, QTableWidgetItem(f"{value:,.0f}"))
            
    def update_result_table(self):
        """Cập nhật bảng kết quả"""
        if not self.calculator:
            return
            
        self.result_table.setRowCount(4)
        
        # Thêm kết quả
        items = [
            ("Mức trọng yếu tổng thể", self.calculator.overall_materiality),
            ("Mức trọng yếu thực hiện", self.calculator.performance_materiality),
            ("Ngưỡng sai sót không đáng kể", self.calculator.threshold),
            ("Tỷ lệ áp dụng", f"{self.calculator.benchmark_percentage}%")
        ]
        
        for row, (key, value) in enumerate(items):
            self.result_table.setItem(row, 0, QTableWidgetItem(key))
            if isinstance(value, float):
                self.result_table.setItem(row, 1, QTableWidgetItem(f"{value:,.0f}"))
            else:
                self.result_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
    def calculate_materiality(self):
        """Tính toán mức trọng yếu"""
        try:
            # Lấy người dùng được chọn
            selected_users = [
                user_type for user_type, checkbox in self.user_checkboxes.items()
                if checkbox.isChecked()
            ]
            if not selected_users:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một người sử dụng BCTC")
                return
                
            # Thiết lập thông tin cho calculator
            self.calculator.set_users(selected_users)
            
            # Lấy tỷ lệ % (nếu có)
            percentage = None
            if self.percentage_edit.text().strip():
                try:
                    percentage = float(self.percentage_edit.text())
                except ValueError:
                    QMessageBox.warning(self, "Lỗi", "Tỷ lệ % không hợp lệ")
                    return
                    
            # Tính toán và hiển thị kết quả
            self.calculator.calculate_materiality(percentage)
            self.result_text.setText(self.calculator.get_explanation())
            self.update_result_table()  # Cập nhật bảng kết quả
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tính toán: {str(e)}")
            
    def save_results(self):
        """Lưu kết quả tính toán"""
        try:
            # Tạo đối tượng MaterialityResult
            result = MaterialityResult(
                company_name=self.company_info['name'],
                tax_code=self.company_info['tax_code'],
                calculation_date=datetime.now(),
                users=[user.value for user in self.calculator.selected_users],
                benchmark_type=self.calculator.selected_benchmark.value,
                benchmark_value=self.calculator.benchmark_value,
                audit_year=self.calculator.audit_year.value,
                risk_level=self.calculator.risk_level.value,
                percentage=self.calculator.benchmark_percentage,
                overall_materiality=self.calculator.overall_materiality,
                performance_materiality=self.calculator.performance_materiality,
                threshold=self.calculator.threshold,
                explanation=self.calculator.get_explanation()
            )
            
            # Lưu kết quả
            saved_path = self.result_manager.save_result(result)
            QMessageBox.information(
                self, 
                "Thông báo", 
                f"Đã lưu kết quả thành công\nFile: {saved_path.name}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu kết quả: {str(e)}")

    def update_values(self):
        """Cập nhật giá trị và tỷ lệ đề xuất khi thay đổi lựa chọn"""
        try:
            if not self.calculator or not self.key_metrics:
                return
            
            # Lấy benchmark được chọn
            selected_benchmark = self.benchmark_combo.currentData()
            if not selected_benchmark:
                return
            
            # Lấy giá trị tương ứng
            benchmark_key = {
                Benchmark.TOTAL_ASSETS: 'total_assets',
                Benchmark.EQUITY: 'equity',
                Benchmark.REVENUE: 'revenue',
                Benchmark.PROFIT_BEFORE_TAX: 'profit_before_tax',
                Benchmark.TOTAL_EXPENSES: 'total_expenses'
            }.get(selected_benchmark)
            
            if benchmark_key not in self.key_metrics:
                self.value_label.setText("N/A")
                self.suggested_percentage_label.setText("N/A")
                return
            
            # Hiển thị giá trị
            value = self.key_metrics[benchmark_key]
            self.value_label.setText(f"{value:,.0f} VND")
            
            # Thiết lập thông tin cho calculator
            self.calculator.set_benchmark(selected_benchmark, value)
            self.calculator.set_audit_parameters(
                self.year_combo.currentData(),
                self.risk_combo.currentData()
            )
            
            # Hiển thị tỷ lệ đề xuất
            suggested_percentage = self.calculator.get_suggested_percentage()
            if suggested_percentage is not None:
                self.suggested_percentage_label.setText(f"{suggested_percentage}%")
            else:
                self.suggested_percentage_label.setText("N/A")
            
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật giá trị: {str(e)}")
            self.value_label.setText("Lỗi")
            self.suggested_percentage_label.setText("Lỗi") 