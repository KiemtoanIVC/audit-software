from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QTextEdit, QComboBox, QCheckBox,
                           QPushButton, QGroupBox, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from pathlib import Path
import json
import os

from ...utils.styles import AppTheme
from ...models.audit_form import AuditForm, FormStatus

class A110Form(QWidget):
    """
    Biểu mẫu A110 - Chấp nhận khách hàng mới & đánh giá rủi ro hợp đồng
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
        title_label = QLabel("A110 - CHẤP NHẬN KHÁCH HÀNG MỚI & ĐÁNH GIÁ RỦI RO HỢP ĐỒNG")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {AppTheme.PRIMARY};")
        main_layout.addWidget(title_label)

        # Phần 1: Thông tin khách hàng
        client_group = QGroupBox("1. Thông tin khách hàng")
        client_layout = QGridLayout()

        # Tên khách hàng
        client_layout.addWidget(QLabel("Tên khách hàng:"), 0, 0)
        self.client_name_edit = QLineEdit()
        client_layout.addWidget(self.client_name_edit, 0, 1)

        # Mã số thuế
        client_layout.addWidget(QLabel("Mã số thuế:"), 1, 0)
        self.tax_code_edit = QLineEdit()
        client_layout.addWidget(self.tax_code_edit, 1, 1)

        # Địa chỉ
        client_layout.addWidget(QLabel("Địa chỉ:"), 2, 0)
        self.address_edit = QLineEdit()
        client_layout.addWidget(self.address_edit, 2, 1)

        # Lĩnh vực kinh doanh
        client_layout.addWidget(QLabel("Lĩnh vực kinh doanh:"), 3, 0)
        self.business_field_edit = QLineEdit()
        client_layout.addWidget(self.business_field_edit, 3, 1)

        client_group.setLayout(client_layout)
        main_layout.addWidget(client_group)

        # Phần 2: Đánh giá rủi ro
        risk_group = QGroupBox("2. Đánh giá rủi ro hợp đồng")
        risk_layout = QVBoxLayout()

        # Câu hỏi 1
        self.risk_q1 = QCheckBox("Khách hàng có uy tín tốt trong ngành?")
        risk_layout.addWidget(self.risk_q1)

        # Câu hỏi 2
        self.risk_q2 = QCheckBox("Ban lãnh đạo khách hàng có uy tín và đáng tin cậy?")
        risk_layout.addWidget(self.risk_q2)

        # Câu hỏi 3
        self.risk_q3 = QCheckBox("Công ty kiểm toán có đủ năng lực và nguồn lực để thực hiện hợp đồng?")
        risk_layout.addWidget(self.risk_q3)

        # Câu hỏi 4
        self.risk_q4 = QCheckBox("Không có xung đột lợi ích giữa công ty kiểm toán và khách hàng?")
        risk_layout.addWidget(self.risk_q4)

        # Câu hỏi 5
        self.risk_q5 = QCheckBox("Phí kiểm toán được đề xuất là hợp lý?")
        risk_layout.addWidget(self.risk_q5)

        risk_group.setLayout(risk_layout)
        main_layout.addWidget(risk_group)

        # Phần 3: Kết luận
        conclusion_group = QGroupBox("3. Kết luận")
        conclusion_layout = QVBoxLayout()

        # Quyết định
        decision_layout = QHBoxLayout()
        decision_layout.addWidget(QLabel("Quyết định:"))
        self.decision_combo = QComboBox()
        self.decision_combo.addItems(["Chấp nhận", "Từ chối"])
        decision_layout.addWidget(self.decision_combo)
        conclusion_layout.addLayout(decision_layout)

        # Lý do
        conclusion_layout.addWidget(QLabel("Lý do:"))
        self.reason_text = QTextEdit()
        self.reason_text.setMaximumHeight(100)
        conclusion_layout.addWidget(self.reason_text)

        # Người thực hiện
        performer_layout = QHBoxLayout()
        performer_layout.addWidget(QLabel("Người thực hiện:"))
        self.performer_edit = QLineEdit()
        performer_layout.addWidget(self.performer_edit)
        conclusion_layout.addLayout(performer_layout)

        # Ngày thực hiện
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Ngày thực hiện:"))
        self.date_edit = QLineEdit()
        self.date_edit.setText(datetime.now().strftime("%d/%m/%Y"))
        date_layout.addWidget(self.date_edit)
        conclusion_layout.addLayout(date_layout)

        conclusion_group.setLayout(conclusion_layout)
        main_layout.addWidget(conclusion_group)

        # Nút lưu
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Lưu")
        self.save_button.setStyleSheet(AppTheme.BUTTON_PRIMARY_STYLE)
        self.save_button.clicked.connect(self.save_form)
        button_layout.addWidget(self.save_button)

        self.complete_button = QPushButton("Hoàn thành")
        self.complete_button.setStyleSheet(AppTheme.BUTTON_SUCCESS_STYLE)
        self.complete_button.clicked.connect(self.complete_form)
        button_layout.addWidget(self.complete_button)

        self.close_button = QPushButton("Đóng")
        self.close_button.setStyleSheet(AppTheme.BUTTON_SECONDARY_STYLE)
        self.close_button.clicked.connect(self.close_form)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def set_job_data(self, job_data):
        """Thiết lập dữ liệu job"""
        self.current_job = job_data
        self.load_form_data()

        # Cập nhật trạng thái các nút dựa trên trạng thái form
        self.update_button_states()

    def load_form_data(self):
        """Load dữ liệu form từ file nếu có"""
        if not self.current_job:
            return

        try:
            # Kiểm tra xem đã có file form chưa
            form_path = Path(self.current_job['path']) / "MauBieu" / "A110.json"
            if form_path.exists():
                with open(form_path, "r", encoding="utf-8") as f:
                    self.form_data = json.load(f)

                # Điền dữ liệu vào form
                self.populate_form()
            else:
                # Nếu chưa có, điền thông tin cơ bản từ job
                self.client_name_edit.setText(self.current_job.get('client_name', ''))
                self.tax_code_edit.setText(self.current_job.get('tax_code', ''))

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi load dữ liệu form: {str(e)}")

    def populate_form(self):
        """Điền dữ liệu vào form"""
        # Thông tin khách hàng
        self.client_name_edit.setText(self.form_data.get('client_name', ''))
        self.tax_code_edit.setText(self.form_data.get('tax_code', ''))
        self.address_edit.setText(self.form_data.get('address', ''))
        self.business_field_edit.setText(self.form_data.get('business_field', ''))

        # Đánh giá rủi ro
        self.risk_q1.setChecked(self.form_data.get('risk_q1', False))
        self.risk_q2.setChecked(self.form_data.get('risk_q2', False))
        self.risk_q3.setChecked(self.form_data.get('risk_q3', False))
        self.risk_q4.setChecked(self.form_data.get('risk_q4', False))
        self.risk_q5.setChecked(self.form_data.get('risk_q5', False))

        # Kết luận
        index = self.decision_combo.findText(self.form_data.get('decision', 'Chấp nhận'))
        if index >= 0:
            self.decision_combo.setCurrentIndex(index)

        self.reason_text.setText(self.form_data.get('reason', ''))
        self.performer_edit.setText(self.form_data.get('performer', ''))
        self.date_edit.setText(self.form_data.get('date', datetime.now().strftime("%d/%m/%Y")))

        # Cập nhật trạng thái các nút
        self.update_button_states()

    def collect_form_data(self):
        """Thu thập dữ liệu từ form"""
        return {
            'code': 'A110',
            'name': 'Chấp nhận khách hàng mới & đánh giá rủi ro hợp đồng',
            'client_name': self.client_name_edit.text(),
            'tax_code': self.tax_code_edit.text(),
            'address': self.address_edit.text(),
            'business_field': self.business_field_edit.text(),
            'risk_q1': self.risk_q1.isChecked(),
            'risk_q2': self.risk_q2.isChecked(),
            'risk_q3': self.risk_q3.isChecked(),
            'risk_q4': self.risk_q4.isChecked(),
            'risk_q5': self.risk_q5.isChecked(),
            'decision': self.decision_combo.currentText(),
            'reason': self.reason_text.toPlainText(),
            'performer': self.performer_edit.text(),
            'date': self.date_edit.text(),
            'updated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    def save_form(self):
        """Lưu form"""
        if not self.current_job:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo hoặc mở job trước!")
            return

        try:
            # Thu thập dữ liệu
            self.form_data = self.collect_form_data()

            # Tạo thư mục MauBieu nếu chưa có
            form_dir = Path(self.current_job['path']) / "MauBieu"
            form_dir.mkdir(parents=True, exist_ok=True)

            # Lưu file
            form_path = form_dir / "A110.json"
            with open(form_path, "w", encoding="utf-8") as f:
                json.dump(self.form_data, f, ensure_ascii=False, indent=2)

            # Cập nhật trạng thái form
            form_state = {
                'status': 'Đang làm',
                'updated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            # Emit signal để cập nhật trạng thái
            self.form_saved.emit({
                'code': 'A110',
                'state': form_state
            })

            QMessageBox.information(self, "Thông báo", "Đã lưu biểu mẫu A110!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu form: {str(e)}")

    def complete_form(self):
        """Hoàn thành form"""
        if not self.current_job:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo hoặc mở job trước!")
            return

        # Kiểm tra các trường bắt buộc
        if not self.client_name_edit.text() or not self.tax_code_edit.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng điền đầy đủ thông tin khách hàng!")
            return

        try:
            # Thu thập dữ liệu
            self.form_data = self.collect_form_data()

            # Tạo thư mục MauBieu nếu chưa có
            form_dir = Path(self.current_job['path']) / "MauBieu"
            form_dir.mkdir(parents=True, exist_ok=True)

            # Lưu file
            form_path = form_dir / "A110.json"
            with open(form_path, "w", encoding="utf-8") as f:
                json.dump(self.form_data, f, ensure_ascii=False, indent=2)

            # Cập nhật trạng thái form
            form_state = {
                'status': 'Hoàn thành',
                'updated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            # Emit signal để cập nhật trạng thái
            self.form_saved.emit({
                'code': 'A110',
                'state': form_state
            })

            QMessageBox.information(self, "Thông báo", "Đã hoàn thành biểu mẫu A110!")

            # Cập nhật trạng thái các nút
            self.update_button_states()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi hoàn thành form: {str(e)}")

    def close_form(self):
        """Đóng form và quay lại trang mặc định"""
        # Emit signal để thông báo form đã được đóng
        self.form_saved.emit({
            'code': 'A110',
            'action': 'close'
        })

    def update_button_states(self):
        """Cập nhật trạng thái các nút dựa trên trạng thái form"""
        # Kiểm tra xem form đã hoàn thành chưa
        is_completed = False

        if self.current_job and 'form_states' in self.current_job:
            form_states = self.current_job['form_states']
            if 'A110' in form_states and form_states['A110']['status'] == 'Hoàn thành':
                is_completed = True

        # Nếu form đã hoàn thành, chỉ cho phép xem và đóng
        if is_completed:
            # Vô hiệu hóa các trường nhập liệu
            self.client_name_edit.setReadOnly(True)
            self.tax_code_edit.setReadOnly(True)
            self.address_edit.setReadOnly(True)
            self.business_field_edit.setReadOnly(True)
            self.risk_q1.setEnabled(False)
            self.risk_q2.setEnabled(False)
            self.risk_q3.setEnabled(False)
            self.risk_q4.setEnabled(False)
            self.risk_q5.setEnabled(False)
            self.decision_combo.setEnabled(False)
            self.reason_text.setReadOnly(True)
            self.performer_edit.setReadOnly(True)
            self.date_edit.setReadOnly(True)

            # Ẩn các nút lưu và hoàn thành
            self.save_button.setVisible(False)
            self.complete_button.setVisible(False)
            self.close_button.setText("Đóng")
        else:
            # Bật các trường nhập liệu
            self.client_name_edit.setReadOnly(False)
            self.tax_code_edit.setReadOnly(False)
            self.address_edit.setReadOnly(False)
            self.business_field_edit.setReadOnly(False)
            self.risk_q1.setEnabled(True)
            self.risk_q2.setEnabled(True)
            self.risk_q3.setEnabled(True)
            self.risk_q4.setEnabled(True)
            self.risk_q5.setEnabled(True)
            self.decision_combo.setEnabled(True)
            self.reason_text.setReadOnly(False)
            self.performer_edit.setReadOnly(False)
            self.date_edit.setReadOnly(False)

            # Hiện các nút lưu và hoàn thành
            self.save_button.setVisible(True)
            self.complete_button.setVisible(True)
            self.close_button.setText("Đóng")
