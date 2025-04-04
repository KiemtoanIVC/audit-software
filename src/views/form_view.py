from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                           QTreeWidget, QTreeWidgetItem, QPushButton,
                           QLabel, QStackedWidget, QFrame, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from ..utils.styles import AppTheme
from .materiality_dialog import MaterialityDialog
from .audit_forms.a110_form import A110Form
from .audit_forms.a810_form import A810Form
from datetime import datetime
from ..modules.job.job_creator import JobCreator

class FormView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_job = None
        self.form_states = {}  # Lưu trạng thái các biểu mẫu
        self.current_form = None  # Biểu mẫu đang được chọn
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Tạo splitter để chia màn hình
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel bên trái (1/3 màn hình) - danh sách biểu mẫu
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)

        # TreeWidget cho danh sách biểu mẫu
        self.form_tree = QTreeWidget()
        self.form_tree.setHeaderLabels(["Biểu mẫu", "Trạng thái", "Cập nhật"])
        self.form_tree.setColumnWidth(0, 150)
        self.form_tree.setColumnWidth(1, 100)
        self.form_tree.setMinimumWidth(350)
        self.form_tree.itemClicked.connect(self.on_form_selected)

        left_layout.addWidget(self.form_tree)

        # Panel bên phải (2/3 màn hình) - chi tiết biểu mẫu
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        # Stack widget để chứa các form chi tiết
        self.form_stack = QStackedWidget()

        # Trang mặc định (hiển thị khi chưa chọn biểu mẫu)
        self.default_page = QWidget()
        default_layout = QVBoxLayout(self.default_page)
        default_label = QLabel("Chọn một biểu mẫu từ danh sách bên trái để bắt đầu.")
        default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_layout.addWidget(default_label)
        self.form_stack.addWidget(self.default_page)

        # Khởi tạo các form
        self.a110_form = A110Form()
        self.a110_form.form_saved.connect(self.on_form_saved)
        self.form_stack.addWidget(self.a110_form)

        self.a810_form = A810Form()
        self.a810_form.form_saved.connect(self.on_form_saved)
        self.form_stack.addWidget(self.a810_form)

        self.right_layout.addWidget(self.form_stack)

        # Thêm cả hai panel vào splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)

        # Thiết lập tỷ lệ ban đầu (1:2)
        self.splitter.setSizes([100, 200])

        main_layout.addWidget(self.splitter)

        # Khởi tạo cây biểu mẫu
        self.initialize_form_tree()

        # Định nghĩa style cho button
        self.button_style = f"""
            QPushButton {{
                background-color: {AppTheme.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.PRIMARY};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.DISABLED};
                color: #888888;
            }}
        """

    def initialize_form_tree(self):
        """Khởi tạo cây biểu mẫu với các nhóm và biểu mẫu con"""
        # Nhóm Lập kế hoạch
        planning_group = QTreeWidgetItem(self.form_tree, ["Lập kế hoạch"])
        planning_group.setExpanded(True)

        forms_planning = [
            ("A110", "Chấp nhận khách hàng mới & đánh giá rủi ro hợp đồng"),
            ("A120", "Chấp nhận, duy trì khách hàng cũ & đánh giá rủi ro hợp đồng"),
            ("A230", "Thư gửi khách hàng về kế hoạch kiểm toán"),
            ("A260", "Thông tin độc lập của nhóm kiểm toán"),
            ("A270", "Đánh giá yếu tố phụ thuộc"),
            ("A271", "Ký hợp đồng dịch vụ"),
            ("A272", "Tính độc lập")
        ]

        for code, name in forms_planning:
            item = QTreeWidgetItem(planning_group, [f"{code} - {name}", "Chưa làm", ""])
            item.setData(0, Qt.ItemDataRole.UserRole, code)
            self.set_status_color(item, "Chưa làm")

        # Nhóm Thực hiện
        execution_group = QTreeWidgetItem(self.form_tree, ["Thực hiện"])
        execution_group.setExpanded(True)

        forms_execution = [
            ("A510", "Phân tích sơ bộ báo cáo tài chính"),
            ("A710", "Tính Mức trọng yếu"),
            ("A810", "Đánh giá rủi ro và thiết kế thủ tục kiểm toán")
        ]

        for code, name in forms_execution:
            item = QTreeWidgetItem(execution_group, [f"{code} - {name}", "Chưa làm", ""])
            item.setData(0, Qt.ItemDataRole.UserRole, code)
            self.set_status_color(item, "Chưa làm")

        # Nhóm Phát hành báo cáo
        report_group = QTreeWidgetItem(self.form_tree, ["Phát hành báo cáo"])
        report_group.setExpanded(True)

        forms_report = [
            ("B410", "Tổng hợp kết quả kiểm toán"),
            ("B440", "Thư giải trình của Ban Giám đốc")
        ]

        for code, name in forms_report:
            item = QTreeWidgetItem(report_group, [f"{code} - {name}", "Chưa làm", ""])
            item.setData(0, Qt.ItemDataRole.UserRole, code)
            self.set_status_color(item, "Chưa làm")

        # Nhóm Khác
        other_group = QTreeWidgetItem(self.form_tree, ["Khác"])
        other_group.setExpanded(True)

        forms_other = [
            ("C001", "Đề nghị soát xét")
        ]

        for code, name in forms_other:
            item = QTreeWidgetItem(other_group, [f"{code} - {name}", "Chưa làm", ""])
            item.setData(0, Qt.ItemDataRole.UserRole, code)
            self.set_status_color(item, "Chưa làm")

    def set_status_color(self, item, status):
        """Thiết lập màu sắc dựa trên trạng thái"""
        if status == "Chưa làm":
            item.setBackground(1, QColor("#f0f0f0"))  # Xám nhạt
        elif status == "Đang làm":
            item.setBackground(1, QColor("#FFD700"))  # Vàng
        elif status == "Đã xong":
            item.setBackground(1, QColor("#90EE90"))  # Xanh lá nhạt

    def load_form_states(self):
        """Load trạng thái các biểu mẫu từ job"""
        if not self.current_job:
            return

        if 'form_states' in self.current_job:
            self.form_states = self.current_job['form_states']
            self.update_form_tree()

    def update_form_tree(self):
        """Cập nhật cây biểu mẫu từ trạng thái đã load"""
        # Duyệt tất cả các nhóm
        for group_idx in range(self.form_tree.topLevelItemCount()):
            group = self.form_tree.topLevelItem(group_idx)

            # Duyệt các biểu mẫu trong mỗi nhóm
            for form_idx in range(group.childCount()):
                form_item = group.child(form_idx)
                form_code = form_item.data(0, Qt.ItemDataRole.UserRole)

                # Nếu có thông tin trạng thái, cập nhật
                if form_code in self.form_states:
                    state_info = self.form_states[form_code]
                    form_item.setText(1, state_info['status'])
                    form_item.setText(2, state_info['updated_at'])
                    self.set_status_color(form_item, state_info['status'])

    def on_form_selected(self, item):
        """Xử lý khi người dùng chọn một biểu mẫu"""
        # Kiểm tra xem đây có phải là biểu mẫu con (không phải nhóm)
        if item.parent():
            form_code = item.data(0, Qt.ItemDataRole.UserRole)
            self.current_form = form_code
            self.open_form(form_code)

    def open_form(self, form_code):
        """Mở biểu mẫu tương ứng với mã form_code"""
        # Kiểm tra có job hiện tại không
        if not self.current_job:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo hoặc mở Job trước!")
            return

        # Cập nhật trạng thái thành "Đang làm" nếu đang "Chưa làm"
        if form_code not in self.form_states:
            self.form_states[form_code] = {
                'status': 'Đang làm',
                'updated_at': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
        elif self.form_states[form_code]['status'] == 'Chưa làm':
            self.form_states[form_code]['status'] = 'Đang làm'
            self.form_states[form_code]['updated_at'] = datetime.now().strftime('%d/%m/%Y %H:%M')

        # Cập nhật lại cây biểu mẫu
        self.update_form_tree()

        # Lưu trạng thái vào job
        self.save_form_states()

        # Mở form tương ứng
        if form_code == "A710":
            # Kiểm tra xem đã có dữ liệu BCTC chưa
            if not self.current_job.get('bctc_file'):
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file BCTC trước!")
                return

            # Mở dialog tính mức trọng yếu
            try:
                dialog = MaterialityDialog(self)

                # Truyền dữ liệu job cho dialog
                dialog.set_bctc_data(self.current_job)

                # Hiển thị dialog
                result = dialog.exec()

                # Nếu thành công, cập nhật trạng thái
                if result == QDialog.DialogCode.Accepted and self.current_job.get('materiality_result'):
                    self.form_states[form_code]['status'] = 'Đã xong'
                    self.form_states[form_code]['updated_at'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                    self.update_form_tree()
                    self.save_form_states()
                    QMessageBox.information(self, "Thành công", "Đã tính toán và lưu mức trọng yếu!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi mở dialog tính mức trọng yếu: {str(e)}")
        elif form_code == "A110":
            # Hiển thị form A110
            self.a110_form.set_job_data(self.current_job)
            self.form_stack.setCurrentWidget(self.a110_form)

            # Nếu form đã hoàn thành, chỉ cho phép xem
            # Trạng thái các nút đã được cập nhật trong a110_form.update_button_states()
        elif form_code == "A810":
            # Hiển thị form A810
            self.a810_form.set_job_data(self.current_job)
            self.form_stack.setCurrentWidget(self.a810_form)

            # Nếu form đã hoàn thành, chỉ cho phép xem
            # Trạng thái các nút đã được cập nhật trong a810_form.update_button_states()
        else:
            # Xử lý các form khác (sẽ triển khai sau)
            QMessageBox.information(self, "Thông báo", f"Biểu mẫu {form_code} đang được phát triển.")

    def save_form_states(self):
        """Lưu trạng thái biểu mẫu vào job"""
        if not self.current_job:
            return

        self.current_job['form_states'] = self.form_states

        # Lưu job config thông qua JobCreator
        try:
            JobCreator.save_job_config(self.current_job)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu trạng thái biểu mẫu: {str(e)}")

    def on_form_saved(self, form_data):
        """Xử lý khi form được lưu hoặc đóng"""
        if not self.current_job:
            return

        # Lấy mã form
        form_code = form_data.get('code')

        # Kiểm tra xem là action đóng form hay không
        if form_data.get('action') == 'close':
            # Chuyển về trang mặc định
            self.form_stack.setCurrentWidget(self.default_page)
            return

        # Cập nhật trạng thái form
        form_state = form_data.get('state')

        if form_code and form_state:
            self.form_states[form_code] = form_state
            self.update_form_tree()
            self.save_form_states()

    def set_bctc_data(self, bctc_file, job_data):
        """Nhận dữ liệu BCTC từ MainWindow"""
        self.current_job = job_data
        # Load trạng thái biểu mẫu
        self.load_form_states()
