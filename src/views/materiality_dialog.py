from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                           QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton,
                           QTextEdit, QMessageBox, QGridLayout, QTableWidget,
                           QTableWidgetItem, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from datetime import datetime
from ..core.materiality_calculator import MaterialityCalculator, UserType, Benchmark, AuditYear, RiskLevel
from ..utils.styles import AppTheme
from ..core.financial_data_processor import FinancialDataProcessor

class MaterialityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tính mức trọng yếu")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        # Thiết lập window flags để có thể phóng to, thu nhỏ
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinMaxButtonsHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.current_job = None
        self.calculator = MaterialityCalculator()
        self.processor = FinancialDataProcessor()
        self.user_checkboxes = {}

        # Khởi tạo UI
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Tạo tab widget
        self.tab_widget = QTabWidget()

        # Tab tính toán
        self.calc_tab = QWidget()
        self.setup_calc_tab()
        self.tab_widget.addTab(self.calc_tab, "Tính toán")

        # Tab kết quả
        self.result_tab = QWidget()
        self.setup_result_tab()
        self.tab_widget.addTab(self.result_tab, "Kết quả")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def setup_calc_tab(self):
        layout = QVBoxLayout()
        self.calc_tab.setLayout(layout)

        # Thêm các nhóm controls
        self.setup_user_group()
        self.setup_criteria_group()

        # Thêm nút tính toán
        calculate_btn = QPushButton("Tính toán mức trọng yếu")
        calculate_btn.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        calculate_btn.clicked.connect(self.calculate_materiality)
        layout.addWidget(calculate_btn)

    def setup_user_group(self):
        """Thiết lập group box người sử dụng BCTC"""
        group = QGroupBox("1. Người sử dụng chính của BCTC")
        layout = QVBoxLayout()

        for user_type in UserType:
            checkbox = QCheckBox(user_type.value)
            self.user_checkboxes[user_type] = checkbox
            layout.addWidget(checkbox)

        group.setLayout(layout)
        self.calc_tab.layout().addWidget(group)

    def setup_criteria_group(self):
        """Thiết lập group box thông tin kiểm toán"""
        group = QGroupBox("2. Thông tin kiểm toán")
        layout = QGridLayout()

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

        # Layout
        layout.addWidget(QLabel("Tiêu chí:"), 0, 0)
        layout.addWidget(self.benchmark_combo, 0, 1)
        layout.addWidget(QLabel("Năm kiểm toán:"), 1, 0)
        layout.addWidget(self.year_combo, 1, 1)
        layout.addWidget(QLabel("Mức độ rủi ro:"), 2, 0)
        layout.addWidget(self.risk_combo, 2, 1)
        layout.addWidget(QLabel("Giá trị:"), 3, 0)
        layout.addWidget(self.value_label, 3, 1)
        layout.addWidget(QLabel("Tỷ lệ % đề xuất:"), 4, 0)
        layout.addWidget(self.suggested_percentage_label, 4, 1)
        layout.addWidget(QLabel("Tỷ lệ % tùy chọn:"), 5, 0)
        layout.addWidget(self.percentage_edit, 5, 1)

        # Thêm kết nối signals
        self.benchmark_combo.currentIndexChanged.connect(self.update_values)
        self.year_combo.currentIndexChanged.connect(self.update_values)
        self.risk_combo.currentIndexChanged.connect(self.update_values)

        group.setLayout(layout)
        self.calc_tab.layout().addWidget(group)

    def setup_result_tab(self):
        layout = QVBoxLayout()

        # Thêm các controls cho tab kết quả
        result_label = QLabel("Kết quả tính toán mức trọng yếu")
        result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(result_label)

        # Thêm bảng kết quả chi tiết
        self.result_detail_table = QTableWidget()
        self.result_detail_table.setColumnCount(2)
        self.result_detail_table.setHorizontalHeaderLabels(["Chỉ tiêu", "Giá trị"])
        self.result_detail_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.result_detail_table)

        # Text giải thích
        explanation_label = QLabel("Giải thích:")
        explanation_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(explanation_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(150)
        layout.addWidget(self.result_text)

        # Thêm nút tính lại, đồng ý và hủy
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        recalculate_btn = QPushButton("Tính lại")
        recalculate_btn.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        recalculate_btn.clicked.connect(self.recalculate)

        accept_btn = QPushButton("Đồng ý")
        accept_btn.setStyleSheet(AppTheme.BUTTON_SUCCESS_STYLE)
        accept_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet(AppTheme.BUTTON_SECONDARY_STYLE)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(recalculate_btn)
        button_layout.addWidget(accept_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.result_tab.setLayout(layout)

    def set_bctc_data(self, job_data):
        """Nhận dữ liệu BCTC từ job"""
        try:
            self.current_job = job_data

            # Kiểm tra dữ liệu key_metrics có sẵn
            if self.current_job and self.current_job.get('key_metrics'):
                # Cập nhật giá trị cho calculator từ key_metrics
                self.key_metrics = self.current_job['key_metrics']
                self.update_values()

                # Kiểm tra xem đã có kết quả tính toán trước đó chưa
                if self.current_job.get('materiality_result'):
                    self.load_saved_result()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi load dữ liệu BCTC: {str(e)}")

    def load_saved_result(self):
        """Tải kết quả đã lưu"""
        try:
            result = self.current_job['materiality_result']

            # Thiết lập các giá trị cho calculator
            # Chọn benchmark
            benchmark_type = result['benchmark_type']
            for i in range(self.benchmark_combo.count()):
                if self.benchmark_combo.itemText(i) == benchmark_type:
                    self.benchmark_combo.setCurrentIndex(i)
                    break

            # Chọn mức độ rủi ro
            risk_level = result['risk_level']
            for i in range(self.risk_combo.count()):
                if self.risk_combo.itemText(i) == risk_level:
                    self.risk_combo.setCurrentIndex(i)
                    break

            # Chọn người dùng
            users = result['users']
            for user_type, checkbox in self.user_checkboxes.items():
                checkbox.setChecked(user_type.value in users)

            # Thiết lập các giá trị khác
            self.calculator.benchmark_value = result['benchmark_value']
            self.calculator.benchmark_percentage = result['percentage']
            self.calculator.overall_materiality = result['overall_materiality']
            self.calculator.performance_materiality = result['performance_materiality']
            self.calculator.threshold = result['threshold']

            # Cập nhật giao diện
            self.update_result_table()
            self.result_text.setText(result['explanation'])

            # Hiển thị thông báo
            QMessageBox.information(self, "Thông báo", "Kết quả tính toán trước đã được tải.")

            # Chuyển sang tab kết quả
            self.tab_widget.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo", f"Không thể tải kết quả đã lưu: {str(e)}")

    def update_values(self):
        """Cập nhật giá trị và tỷ lệ đề xuất khi thay đổi lựa chọn"""
        try:
            if not self.current_job or not self.current_job.get('key_metrics'):
                return

            # Lấy benchmark được chọn
            selected_benchmark = self.benchmark_combo.currentData()
            if not selected_benchmark:
                return

            # Lấy giá trị từ key_metrics
            metrics = self.current_job['key_metrics']

            # Lấy giá trị tương ứng
            benchmark_key = {
                Benchmark.TOTAL_ASSETS: 'total_assets',
                Benchmark.EQUITY: 'equity',
                Benchmark.REVENUE: 'revenue',
                Benchmark.PROFIT_BEFORE_TAX: 'profit_before_tax',
                Benchmark.TOTAL_EXPENSES: 'total_expenses'
            }.get(selected_benchmark)

            if benchmark_key not in metrics:
                self.value_label.setText("N/A")
                self.suggested_percentage_label.setText("N/A")
                return

            # Hiển thị giá trị
            value = metrics[benchmark_key]
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
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi cập nhật giá trị: {str(e)}")

    def calculate_materiality(self):
        """Tính toán mức trọng yếu"""
        try:
            if not self.current_job or not self.current_job.get('key_metrics'):
                QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu BCTC!")
                return

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

            # Cập nhật bảng kết quả
            self.update_result_table()

            # Cập nhật phần giải thích
            self.result_text.setText(self.calculator.get_explanation())

            # Lưu kết quả vào job
            self.save_result_to_job()

            # Hiển thị thông báo thành công
            QMessageBox.information(self, "Thành công", "Đã tính toán xong mức trọng yếu!")

            # Chuyển sang tab kết quả
            self.tab_widget.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tính toán: {str(e)}")

    def update_result_table(self):
        """Cập nhật bảng kết quả"""
        # Cập nhật bảng kết quả chi tiết trong tab kết quả
        self.result_detail_table.setRowCount(8)

        # Thêm kết quả chi tiết
        detail_items = [
            ("Tiêu chí", self.calculator.selected_benchmark.value),
            ("Giá trị tiêu chí", f"{self.calculator.benchmark_value:,.0f}"),
            ("Năm kiểm toán", self.calculator.audit_year.value),
            ("Mức độ rủi ro", self.calculator.risk_level.value),
            ("Tỷ lệ áp dụng", f"{self.calculator.benchmark_percentage}%"),
            ("Mức trọng yếu tổng thể", f"{self.calculator.overall_materiality:,.0f}"),
            ("Mức trọng yếu thực hiện", f"{self.calculator.performance_materiality:,.0f}"),
            ("Ngưỡng sai sót không đáng kể", f"{self.calculator.threshold:,.0f}")
        ]

        for row, (key, value) in enumerate(detail_items):
            self.result_detail_table.setItem(row, 0, QTableWidgetItem(key))
            self.result_detail_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def recalculate(self):
        """Tính lại mức trọng yếu"""
        # Chuyển về tab tính toán
        self.tab_widget.setCurrentIndex(0)

        # Hiển thị thông báo
        QMessageBox.information(self, "Thông báo", "Bạn có thể thay đổi các tham số và tính toán lại.")

    def save_result_to_job(self):
        """Lưu kết quả tính toán vào job"""
        if not self.current_job:
            return

        result = {
            'calculation_date': str(datetime.now()),
            'users': [user.value for user in self.calculator.selected_users],
            'benchmark_type': self.calculator.selected_benchmark.value,
            'benchmark_value': self.calculator.benchmark_value,
            'risk_level': self.calculator.risk_level.value,
            'percentage': self.calculator.benchmark_percentage,
            'overall_materiality': self.calculator.overall_materiality,
            'performance_materiality': self.calculator.performance_materiality,
            'threshold': self.calculator.threshold,
            'explanation': self.calculator.get_explanation()
        }

        # Thêm kết quả vào job
        self.current_job['materiality_result'] = result

        # Lưu job config (thông qua parent widget)
        if hasattr(self.parent(), 'current_job'):
            self.parent().current_job = self.current_job

            # Lưu trạng thái form
            if hasattr(self.parent(), 'save_form_states'):
                self.parent().save_form_states()