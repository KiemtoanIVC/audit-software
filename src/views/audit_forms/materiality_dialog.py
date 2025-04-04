from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton,
                           QTextEdit, QMessageBox, QGridLayout, QTableWidget,
                           QTableWidgetItem)
from PyQt6.QtCore import Qt
from datetime import datetime
from ...utils.styles import AppTheme
from enum import Enum

class UserType(Enum):
    SHAREHOLDER = "Cổ đông, nhà đầu tư"
    BANK = "Ngân hàng, tổ chức tín dụng"
    GOVERNMENT = "Cơ quan nhà nước"
    MANAGEMENT = "Ban điều hành"
    OTHER = "Đối tượng khác"

class Benchmark(Enum):
    TOTAL_ASSETS = "Tổng tài sản"
    EQUITY = "Vốn chủ sở hữu"
    REVENUE = "Doanh thu"
    PROFIT_BEFORE_TAX = "Lợi nhuận trước thuế"
    TOTAL_EXPENSES = "Tổng chi phí"

class AuditYear(Enum):
    FIRST_YEAR = "Năm đầu tiên"
    SUBSEQUENT_YEAR = "Năm tiếp theo"

class RiskLevel(Enum):
    LOW = "Thấp"
    MEDIUM = "Trung bình"
    HIGH = "Cao"

class MaterialityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_job = None
        self.user_checkboxes = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.setWindowTitle("Tính Mức Trọng Yếu")
        self.setMinimumWidth(800)
        
        # Layout chính
        layout = QVBoxLayout(self)
        layout.setSpacing(AppTheme.SPACING_MEDIUM)
        
        # Tạo tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Tính toán
        calculation_tab = QWidget()
        calc_layout = QVBoxLayout()
        
        # 1. Người sử dụng BCTC
        user_group = self.setup_user_group()
        calc_layout.addWidget(user_group)
        
        # 2. Thông tin kiểm toán
        criteria_group = self.setup_criteria_group()
        calc_layout.addWidget(criteria_group)
        
        # Nút tính toán
        calculate_btn = QPushButton("Tính toán")
        calculate_btn.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        calculate_btn.clicked.connect(self.calculate_materiality)
        calc_layout.addWidget(calculate_btn)
        
        calculation_tab.setLayout(calc_layout)
        
        # Tab 2: Kết quả
        result_tab = QWidget()
        result_layout = QVBoxLayout()
        
        # 3. Kết quả
        result_group = self.setup_result_group()
        result_layout.addWidget(result_group)
        
        result_tab.setLayout(result_layout)
        
        # Thêm các tab
        self.tab_widget.addTab(calculation_tab, "1. Tính toán MTY")
        self.tab_widget.addTab(result_tab, "2. Kết quả")
        
        layout.addWidget(self.tab_widget)

    def setup_user_group(self):
        """Thiết lập nhóm người sử dụng BCTC"""
        group = QGroupBox("1. Người sử dụng BCTC")
        layout = QVBoxLayout()
        
        for user_type in UserType:
            checkbox = QCheckBox(user_type.value)
            self.user_checkboxes[user_type] = checkbox
            layout.addWidget(checkbox)
            
        group.setLayout(layout)
        return group

    def setup_criteria_group(self):
        """Thiết lập nhóm tiêu chí tính MTY"""
        group = QGroupBox("2. Thông tin kiểm toán")
        layout = QGridLayout()
        
        # Benchmark
        layout.addWidget(QLabel("Tiêu chí:"), 0, 0)
        self.benchmark_combo = QComboBox()
        for benchmark in Benchmark:
            self.benchmark_combo.addItem(benchmark.value, benchmark)
        layout.addWidget(self.benchmark_combo, 0, 1)
        
        # Giá trị
        layout.addWidget(QLabel("Giá trị:"), 1, 0)
        self.value_label = QLabel("N/A")
        layout.addWidget(self.value_label, 1, 1)
        
        # Năm kiểm toán
        layout.addWidget(QLabel("Năm kiểm toán:"), 2, 0)
        self.year_combo = QComboBox()
        for year in AuditYear:
            self.year_combo.addItem(year.value, year)
        layout.addWidget(self.year_combo, 2, 1)
        
        # Mức độ rủi ro
        layout.addWidget(QLabel("Mức độ rủi ro:"), 3, 0)
        self.risk_combo = QComboBox()
        for risk in RiskLevel:
            self.risk_combo.addItem(risk.value, risk)
        layout.addWidget(self.risk_combo, 3, 1)
        
        # Tỷ lệ đề xuất
        layout.addWidget(QLabel("Tỷ lệ đề xuất:"), 4, 0)
        self.suggested_percentage_label = QLabel("N/A")
        layout.addWidget(self.suggested_percentage_label, 4, 1)
        
        # Tỷ lệ tự chọn
        layout.addWidget(QLabel("Tỷ lệ tự chọn (%):"), 5, 0)
        self.percentage_edit = QLineEdit()
        self.percentage_edit.setPlaceholderText("Nhập tỷ lệ % (nếu muốn)")
        layout.addWidget(self.percentage_edit, 5, 1)
        
        group.setLayout(layout)
        return group

    def setup_result_group(self):
        """Thiết lập nhóm kết quả"""
        group = QGroupBox("3. Kết quả tính toán")
        layout = QVBoxLayout()
        
        # Bảng kết quả
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Chỉ tiêu", "Giá trị"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.result_table)
        
        # Giải thích
        layout.addWidget(QLabel("Giải thích:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        group.setLayout(layout)
        return group

    def set_bctc_data(self, job_data):
        """Nhận dữ liệu BCTC từ job"""
        try:
            self.current_job = job_data
            if self.current_job and self.current_job.get('key_metrics'):
                self.update_values()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi load dữ liệu BCTC: {str(e)}")

    def update_values(self):
        """Cập nhật giá trị và tỷ lệ đề xuất"""
        try:
            if not self.current_job or not self.current_job.get('key_metrics'):
                return
                
            metrics = self.current_job['key_metrics']
            selected_benchmark = self.benchmark_combo.currentData()
            
            # Lấy giá trị tương ứng
            benchmark_mapping = {
                Benchmark.TOTAL_ASSETS: 'total_assets',
                Benchmark.EQUITY: 'equity',
                Benchmark.REVENUE: 'revenue',
                Benchmark.PROFIT_BEFORE_TAX: 'profit_before_tax',
                Benchmark.TOTAL_EXPENSES: 'total_expenses'
            }
            
            key = benchmark_mapping.get(selected_benchmark)
            if key and key in metrics:
                value = metrics[key]
                self.value_label.setText(f"{value:,.0f} VND")
                
                # Tính tỷ lệ đề xuất
                base_percentages = {
                    Benchmark.TOTAL_ASSETS: 1.0,
                    Benchmark.EQUITY: 2.0,
                    Benchmark.REVENUE: 0.5,
                    Benchmark.PROFIT_BEFORE_TAX: 5.0,
                    Benchmark.TOTAL_EXPENSES: 0.5
                }
                
                risk_factors = {
                    RiskLevel.LOW: 1.2,
                    RiskLevel.MEDIUM: 1.0,
                    RiskLevel.HIGH: 0.8
                }
                
                base = base_percentages.get(selected_benchmark, 1.0)
                factor = risk_factors.get(self.risk_combo.currentData(), 1.0)
                suggested = round(base * factor, 2)
                
                self.suggested_percentage_label.setText(f"{suggested}%")
            else:
                self.value_label.setText("N/A")
                self.suggested_percentage_label.setText("N/A")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi cập nhật giá trị: {str(e)}")

    def calculate_materiality(self):
        """Tính toán mức trọng yếu"""
        try:
            if not self.current_job or not self.current_job.get('key_metrics'):
                QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu BCTC!")
                return
                
            # Kiểm tra người dùng được chọn
            selected_users = [
                user_type for user_type, checkbox in self.user_checkboxes.items()
                if checkbox.isChecked()
            ]
            
            if not selected_users:
                QMessageBox.warning(self, "Cảnh báo", 
                                  "Vui lòng chọn ít nhất một người sử dụng BCTC")
                return
                
            # Lấy giá trị benchmark
            metrics = self.current_job['key_metrics']
            selected_benchmark = self.benchmark_combo.currentData()
            benchmark_mapping = {
                Benchmark.TOTAL_ASSETS: 'total_assets',
                Benchmark.EQUITY: 'equity',
                Benchmark.REVENUE: 'revenue',
                Benchmark.PROFIT_BEFORE_TAX: 'profit_before_tax',
                Benchmark.TOTAL_EXPENSES: 'total_expenses'
            }
            
            key = benchmark_mapping.get(selected_benchmark)
            if not key or key not in metrics:
                QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu cho tiêu chí đã chọn!")
                return
                
            benchmark_value = metrics[key]
            
            # Lấy tỷ lệ %
            if self.percentage_edit.text().strip():
                try:
                    percentage = float(self.percentage_edit.text())
                except ValueError:
                    QMessageBox.warning(self, "Lỗi", "Tỷ lệ % không hợp lệ")
                    return
            else:
                percentage = float(self.suggested_percentage_label.text().replace('%', ''))
                
            # Tính toán
            overall_materiality = benchmark_value * (percentage / 100)
            performance_materiality = overall_materiality * 0.75
            threshold = overall_materiality * 0.05
            
            # Cập nhật bảng kết quả
            self.result_table.setRowCount(4)
            items = [
                ("Mức trọng yếu tổng thể", f"{overall_materiality:,.0f}"),
                ("Mức trọng yếu thực hiện", f"{performance_materiality:,.0f}"),
                ("Ngưỡng sai sót không đáng kể", f"{threshold:,.0f}"),
                ("Tỷ lệ áp dụng", f"{percentage}%")
            ]
            
            for row, (key, value) in enumerate(items):
                self.result_table.setItem(row, 0, QTableWidgetItem(key))
                self.result_table.setItem(row, 1, QTableWidgetItem(value))
                
            # Cập nhật giải thích
            explanation = f"""
1. Xác định mức trọng yếu tổng thể:
- Tiêu chí được chọn: {selected_benchmark.value}
- Giá trị: {benchmark_value:,.0f} VND
- Tỷ lệ áp dụng: {percentage}%
- Mức trọng yếu tổng thể: {overall_materiality:,.0f} VND

2. Xác định mức trọng yếu thực hiện:
- 75% mức trọng yếu tổng thể
- Giá trị: {performance_materiality:,.0f} VND

3. Ngưỡng sai sót không đáng kể:
- 5% mức trọng yếu tổng thể
- Giá trị: {threshold:,.0f} VND
"""
            self.result_text.setText(explanation)
            
            # Lưu kết quả vào job
            self.current_job['materiality'] = {
                'overall': overall_materiality,
                'performance': performance_materiality,
                'threshold': threshold,
                'percentage': percentage,
                'benchmark': selected_benchmark.value,
                'benchmark_value': benchmark_value,
                'calculation_date': datetime.now().isoformat()
            }
            
            # Hiển thị thông báo thành công
            QMessageBox.information(self, "Thành công", "Đã tính toán xong mức trọng yếu!")
            
            # Chuyển sang tab kết quả
            self.tab_widget.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tính toán: {str(e)}") 