from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QTextEdit, QComboBox, QCheckBox,
                           QPushButton, QGroupBox, QGridLayout, QMessageBox,
                           QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from pathlib import Path
import json
import os

from ...utils.styles import AppTheme
from ...models.audit_form import AuditForm, FormStatus

class A810Form(QWidget):
    """
    Biểu mẫu A810 - Đánh giá rủi ro và thiết kế thủ tục kiểm toán
    """
    form_saved = pyqtSignal(dict)  # Signal khi form được lưu

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_job = None
        self.form_data = {}
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(AppTheme.SPACING_MEDIUM)

        # Tiêu đề
        title_label = QLabel("A810 - ĐÁNH GIÁ RỦI RO VÀ THIẾT KẾ THỦ TỤC KIỂM TOÁN")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {AppTheme.PRIMARY};")
        main_layout.addWidget(title_label)

        # Tạo tab widget
        self.tab_widget = QTabWidget()

        # Tab 1: Thông tin chung
        self.general_tab = QWidget()
        self.setup_general_tab()
        self.tab_widget.addTab(self.general_tab, "1. Thông tin chung")

        # Tab 2: Đánh giá rủi ro
        self.risk_tab = QWidget()
        self.setup_risk_tab()
        self.tab_widget.addTab(self.risk_tab, "2. Đánh giá rủi ro")

        # Tab 3: Thiết kế thủ tục kiểm toán
        self.procedure_tab = QWidget()
        self.setup_procedure_tab()
        self.tab_widget.addTab(self.procedure_tab, "3. Thiết kế thủ tục")

        main_layout.addWidget(self.tab_widget)

        # Các nút tác vụ
        button_layout = QHBoxLayout()
        button_layout.setSpacing(AppTheme.SPACING_MEDIUM)

        self.save_button = QPushButton("Lưu")
        self.save_button.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        self.save_button.clicked.connect(self.save_form)
        button_layout.addWidget(self.save_button)

        self.complete_button = QPushButton("Hoàn thành")
        self.complete_button.setStyleSheet(AppTheme.BUTTON_SUCCESS_STYLE)
        self.complete_button.clicked.connect(self.complete_form)
        button_layout.addWidget(self.complete_button)

        self.close_button = QPushButton("Đóng")
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
            QPushButton:pressed {{
                background-color: #bd2130;
            }}
        """)
        self.close_button.clicked.connect(self.close_form)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def setup_general_tab(self):
        """Thiết lập tab thông tin chung"""
        layout = QVBoxLayout(self.general_tab)
        layout.setSpacing(AppTheme.SPACING_MEDIUM)

        # Thông tin khách hàng
        client_group = QGroupBox("Thông tin khách hàng")
        client_layout = QGridLayout()

        # Tên khách hàng
        client_layout.addWidget(QLabel("Tên khách hàng:"), 0, 0)
        self.client_name_edit = QLineEdit()
        client_layout.addWidget(self.client_name_edit, 0, 1)

        # Mã số thuế
        client_layout.addWidget(QLabel("Mã số thuế:"), 1, 0)
        self.tax_code_edit = QLineEdit()
        client_layout.addWidget(self.tax_code_edit, 1, 1)

        # Năm tài chính
        client_layout.addWidget(QLabel("Năm tài chính:"), 2, 0)
        self.fiscal_year_edit = QLineEdit()
        client_layout.addWidget(self.fiscal_year_edit, 2, 1)

        client_group.setLayout(client_layout)
        layout.addWidget(client_group)

        # Thông tin người thực hiện
        performer_group = QGroupBox("Thông tin người thực hiện")
        performer_layout = QGridLayout()

        # Người thực hiện
        performer_layout.addWidget(QLabel("Người thực hiện:"), 0, 0)
        self.performer_edit = QLineEdit()
        performer_layout.addWidget(self.performer_edit, 0, 1)

        # Ngày thực hiện
        performer_layout.addWidget(QLabel("Ngày thực hiện:"), 1, 0)
        self.date_edit = QLineEdit()
        self.date_edit.setText(datetime.now().strftime("%d/%m/%Y"))
        performer_layout.addWidget(self.date_edit, 1, 1)

        performer_group.setLayout(performer_layout)
        layout.addWidget(performer_group)

    def setup_risk_tab(self):
        """Thiết lập tab đánh giá rủi ro"""
        layout = QVBoxLayout(self.risk_tab)
        layout.setSpacing(AppTheme.SPACING_MEDIUM)

        # Bảng đánh giá rủi ro
        risk_group = QGroupBox("Đánh giá rủi ro")
        risk_layout = QVBoxLayout()

        # Tạo bảng đánh giá rủi ro
        self.risk_table = QTableWidget()
        self.risk_table.setColumnCount(4)
        self.risk_table.setHorizontalHeaderLabels(["Khoản mục", "Rủi ro tiềm tàng", "Rủi ro kiểm soát", "Rủi ro phát hiện"])

        # Thiết lập các dòng mặc định
        default_items = [
            "Tiền và tương đương tiền",
            "Đầu tư tài chính",
            "Phải thu khách hàng",
            "Hàng tồn kho",
            "Tài sản cố định",
            "Phải trả người bán",
            "Vay và nợ thuê tài chính",
            "Doanh thu",
            "Chi phí"
        ]

        self.risk_table.setRowCount(len(default_items))

        for i, item in enumerate(default_items):
            # Khoản mục
            self.risk_table.setItem(i, 0, QTableWidgetItem(item))

            # Rủi ro tiềm tàng
            risk_combo1 = QComboBox()
            risk_combo1.addItems(["Thấp", "Trung bình", "Cao"])
            self.risk_table.setCellWidget(i, 1, risk_combo1)

            # Rủi ro kiểm soát
            risk_combo2 = QComboBox()
            risk_combo2.addItems(["Thấp", "Trung bình", "Cao"])
            self.risk_table.setCellWidget(i, 2, risk_combo2)

            # Rủi ro phát hiện
            risk_combo3 = QComboBox()
            risk_combo3.addItems(["Thấp", "Trung bình", "Cao"])
            self.risk_table.setCellWidget(i, 3, risk_combo3)

        # Thiết lập kích thước cột
        header = self.risk_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        risk_layout.addWidget(self.risk_table)
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)

        # Ghi chú đánh giá rủi ro
        note_group = QGroupBox("Ghi chú đánh giá rủi ro")
        note_layout = QVBoxLayout()

        self.risk_note = QTextEdit()
        note_layout.addWidget(self.risk_note)

        note_group.setLayout(note_layout)
        layout.addWidget(note_group)

    def setup_procedure_tab(self):
        """Thiết lập tab thiết kế thủ tục kiểm toán"""
        layout = QVBoxLayout(self.procedure_tab)
        layout.setSpacing(AppTheme.SPACING_MEDIUM)

        # Bảng thiết kế thủ tục kiểm toán
        procedure_group = QGroupBox("Thiết kế thủ tục kiểm toán")
        procedure_layout = QVBoxLayout()

        # Tạo bảng thiết kế thủ tục
        self.procedure_table = QTableWidget()
        self.procedure_table.setColumnCount(3)
        self.procedure_table.setHorizontalHeaderLabels(["Khoản mục", "Thủ tục kiểm toán", "Ghi chú"])

        # Thiết lập các dòng mặc định
        default_items = [
            "Tiền và tương đương tiền",
            "Đầu tư tài chính",
            "Phải thu khách hàng",
            "Hàng tồn kho",
            "Tài sản cố định",
            "Phải trả người bán",
            "Vay và nợ thuê tài chính",
            "Doanh thu",
            "Chi phí"
        ]

        self.procedure_table.setRowCount(len(default_items))

        for i, item in enumerate(default_items):
            # Khoản mục
            self.procedure_table.setItem(i, 0, QTableWidgetItem(item))

            # Thủ tục kiểm toán
            self.procedure_table.setItem(i, 1, QTableWidgetItem(""))

            # Ghi chú
            self.procedure_table.setItem(i, 2, QTableWidgetItem(""))

        # Thiết lập kích thước cột
        header = self.procedure_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        procedure_layout.addWidget(self.procedure_table)
        procedure_group.setLayout(procedure_layout)
        layout.addWidget(procedure_group)

        # Kết luận
        conclusion_group = QGroupBox("Kết luận")
        conclusion_layout = QVBoxLayout()

        self.conclusion_text = QTextEdit()
        conclusion_layout.addWidget(self.conclusion_text)

        conclusion_group.setLayout(conclusion_layout)
        layout.addWidget(conclusion_group)

    def set_job_data(self, job_data):
        """Thiết lập dữ liệu job và load form nếu có"""
        self.current_job = job_data
        self.load_form_data()
        self.update_button_states()

    def load_form_data(self):
        """Load dữ liệu form từ file nếu có"""
        if not self.current_job:
            return

        try:
            # Kiểm tra xem đã có file form chưa
            form_path = Path(self.current_job['path']) / "MauBieu" / "A810.json"
            if form_path.exists():
                with open(form_path, "r", encoding="utf-8") as f:
                    self.form_data = json.load(f)

                # Điền dữ liệu vào form
                self.populate_form()
            else:
                # Nếu chưa có, điền thông tin cơ bản từ job
                self.client_name_edit.setText(self.current_job.get('client_name', ''))
                self.tax_code_edit.setText(self.current_job.get('tax_code', ''))
                self.fiscal_year_edit.setText(self.current_job.get('audit_period', ''))

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi load dữ liệu form: {str(e)}")

    def populate_form(self):
        """Điền dữ liệu vào form"""
        # Tab 1: Thông tin chung
        self.client_name_edit.setText(self.form_data.get('client_name', ''))
        self.tax_code_edit.setText(self.form_data.get('tax_code', ''))
        self.fiscal_year_edit.setText(self.form_data.get('fiscal_year', ''))
        self.performer_edit.setText(self.form_data.get('performer', ''))
        self.date_edit.setText(self.form_data.get('date', ''))

        # Tab 2: Đánh giá rủi ro
        risk_data = self.form_data.get('risk_assessment', [])
        if risk_data:
            for i, item in enumerate(risk_data):
                if i < self.risk_table.rowCount():
                    # Khoản mục
                    self.risk_table.item(i, 0).setText(item.get('item', ''))

                    # Rủi ro tiềm tàng
                    combo1 = self.risk_table.cellWidget(i, 1)
                    combo1.setCurrentText(item.get('inherent_risk', 'Thấp'))

                    # Rủi ro kiểm soát
                    combo2 = self.risk_table.cellWidget(i, 2)
                    combo2.setCurrentText(item.get('control_risk', 'Thấp'))

                    # Rủi ro phát hiện
                    combo3 = self.risk_table.cellWidget(i, 3)
                    combo3.setCurrentText(item.get('detection_risk', 'Thấp'))

        self.risk_note.setText(self.form_data.get('risk_note', ''))

        # Tab 3: Thiết kế thủ tục kiểm toán
        procedure_data = self.form_data.get('audit_procedures', [])
        if procedure_data:
            for i, item in enumerate(procedure_data):
                if i < self.procedure_table.rowCount():
                    # Khoản mục
                    self.procedure_table.item(i, 0).setText(item.get('item', ''))

                    # Thủ tục kiểm toán
                    self.procedure_table.item(i, 1).setText(item.get('procedure', ''))

                    # Ghi chú
                    self.procedure_table.item(i, 2).setText(item.get('note', ''))

        self.conclusion_text.setText(self.form_data.get('conclusion', ''))

    def collect_form_data(self):
        """Thu thập dữ liệu từ form"""
        # Thu thập dữ liệu đánh giá rủi ro
        risk_assessment = []
        for i in range(self.risk_table.rowCount()):
            try:
                item_widget = self.risk_table.item(i, 0)
                item = item_widget.text() if item_widget else ""

                inherent_risk_widget = self.risk_table.cellWidget(i, 1)
                inherent_risk = inherent_risk_widget.currentText() if inherent_risk_widget else "Thấp"

                control_risk_widget = self.risk_table.cellWidget(i, 2)
                control_risk = control_risk_widget.currentText() if control_risk_widget else "Thấp"

                detection_risk_widget = self.risk_table.cellWidget(i, 3)
                detection_risk = detection_risk_widget.currentText() if detection_risk_widget else "Thấp"

                risk_assessment.append({
                    'item': item,
                    'inherent_risk': inherent_risk,
                    'control_risk': control_risk,
                    'detection_risk': detection_risk
                })
            except Exception as e:
                print(f"Lỗi khi thu thập dữ liệu đánh giá rủi ro dòng {i}: {str(e)}")

        # Thu thập dữ liệu thiết kế thủ tục kiểm toán
        audit_procedures = []
        for i in range(self.procedure_table.rowCount()):
            try:
                item_widget = self.procedure_table.item(i, 0)
                item = item_widget.text() if item_widget else ""

                procedure_widget = self.procedure_table.item(i, 1)
                procedure = procedure_widget.text() if procedure_widget else ""

                note_widget = self.procedure_table.item(i, 2)
                note = note_widget.text() if note_widget else ""

                audit_procedures.append({
                    'item': item,
                    'procedure': procedure,
                    'note': note
                })
            except Exception as e:
                print(f"Lỗi khi thu thập dữ liệu thủ tục kiểm toán dòng {i}: {str(e)}")

        return {
            'code': 'A810',
            'name': 'Đánh giá rủi ro và thiết kế thủ tục kiểm toán',
            'client_name': self.client_name_edit.text(),
            'tax_code': self.tax_code_edit.text(),
            'fiscal_year': self.fiscal_year_edit.text(),
            'performer': self.performer_edit.text(),
            'date': self.date_edit.text(),
            'risk_assessment': risk_assessment,
            'risk_note': self.risk_note.toPlainText(),
            'audit_procedures': audit_procedures,
            'conclusion': self.conclusion_text.toPlainText(),
            'updated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    def save_form(self):
        """Lưu form"""
        if not self.current_job:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo hoặc mở Job trước!")
            return

        try:
            print("Bắt đầu thu thập dữ liệu...")
            # Thu thập dữ liệu
            self.form_data = self.collect_form_data()
            print("Thu thập dữ liệu thành công")

            print("Tạo thư mục MauBieu...")
            # Tạo thư mục MauBieu nếu chưa có
            form_dir = Path(self.current_job['path']) / "MauBieu"
            form_dir.mkdir(parents=True, exist_ok=True)
            print(f"Thư mục MauBieu: {form_dir}")

            print("Lưu file...")
            # Lưu file
            form_path = form_dir / "A810.json"
            with open(form_path, "w", encoding="utf-8") as f:
                json.dump(self.form_data, f, ensure_ascii=False, indent=2)
            print(f"Lưu file thành công: {form_path}")

            print("Cập nhật trạng thái form...")
            # Cập nhật trạng thái form
            form_state = {
                'status': 'Đang làm',
                'updated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            # Emit signal để cập nhật trạng thái
            self.form_saved.emit({
                'code': 'A810',
                'state': form_state
            })
            print("Cập nhật trạng thái form thành công")

            QMessageBox.information(self, "Thông báo", "Đã lưu biểu mẫu A810!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu form: {str(e)}")

    def complete_form(self):
        """Hoàn thành form"""
        if not self.current_job:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo hoặc mở Job trước!")
            return

        try:
            print("Bắt đầu hoàn thành form...")
            # Thu thập dữ liệu
            self.form_data = self.collect_form_data()
            print("Thu thập dữ liệu thành công")

            print("Tạo thư mục MauBieu...")
            # Tạo thư mục MauBieu nếu chưa có
            form_dir = Path(self.current_job['path']) / "MauBieu"
            form_dir.mkdir(parents=True, exist_ok=True)
            print(f"Thư mục MauBieu: {form_dir}")

            print("Lưu file...")
            # Lưu file
            form_path = form_dir / "A810.json"
            with open(form_path, "w", encoding="utf-8") as f:
                json.dump(self.form_data, f, ensure_ascii=False, indent=2)
            print(f"Lưu file thành công: {form_path}")

            print("Cập nhật trạng thái form...")
            # Cập nhật trạng thái form
            form_state = {
                'status': 'Hoàn thành',
                'updated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            # Emit signal để cập nhật trạng thái
            self.form_saved.emit({
                'code': 'A810',
                'state': form_state
            })
            print("Cập nhật trạng thái form thành công")

            QMessageBox.information(self, "Thông báo", "Đã hoàn thành biểu mẫu A810!")

            # Cập nhật trạng thái các nút
            self.update_button_states()
            print("Hoàn thành form thành công")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi hoàn thành form: {str(e)}")

    def close_form(self):
        """Đóng form và quay lại trang mặc định"""
        # Emit signal để thông báo form đã được đóng
        self.form_saved.emit({
            'code': 'A810',
            'action': 'close'
        })

    def update_button_states(self):
        """Cập nhật trạng thái các nút dựa trên trạng thái form"""
        # Kiểm tra xem form đã hoàn thành chưa
        is_completed = False

        if self.current_job and 'form_states' in self.current_job:
            form_states = self.current_job['form_states']
            if 'A810' in form_states and form_states['A810']['status'] == 'Hoàn thành':
                is_completed = True

        # Cập nhật trạng thái các nút
        self.save_button.setEnabled(not is_completed)
        self.complete_button.setEnabled(not is_completed)
