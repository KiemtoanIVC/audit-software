from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                           QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt
from .job_view import JobView
from .form_view import FormView
from .utility_view import UtilityView
from .bctc_view import BCTCView
from ..utils.config_manager import ConfigManager
from ..utils.styles import AppTheme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audit Software")
        self.setMinimumSize(1200, 800)

        # Thiết lập style cho main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {AppTheme.BACKGROUND};
            }}
            QTabWidget::pane {{
                border: 1px solid #cccccc;
                background-color: {AppTheme.BACKGROUND};
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: #f0f0f0;
                color: {AppTheme.TEXT};
                padding: 8px 16px;
                margin: 2px 2px 0px 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {AppTheme.BACKGROUND};
                margin-bottom: -1px;
                border-bottom: 1px solid {AppTheme.BACKGROUND};
            }}
        """)

        # Tạo central widget và layout chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(
            AppTheme.SPACING_MEDIUM,
            AppTheme.SPACING_MEDIUM,
            AppTheme.SPACING_MEDIUM,
            AppTheme.SPACING_MEDIUM
        )

        # Tạo tab widget chính
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Thiết lập các tab
        self.setup_tabs()

        # Khôi phục job cuối cùng nếu có
        self.restore_last_job()

    def setup_tabs(self):
        """Thiết lập các tab"""
        # Tab Tạo/Mở Job
        self.job_tab = JobView()
        self.tab_widget.addTab(self.job_tab, "Tạo/Mở Job")

        # Tab Mẫu biểu
        self.form_tab = FormView()
        self.tab_widget.addTab(self.form_tab, "Mẫu biểu kiểm toán")

        # Tab Tiện ích
        self.utility_tab = UtilityView()
        self.tab_widget.addTab(self.utility_tab, "Tiện ích")

        # Tab BCTC và MTY
        self.bctc_tab = BCTCView()
        self.tab_widget.addTab(self.bctc_tab, "Báo cáo tài chính")

        # Kết nối signals
        self.job_tab.job_loaded.connect(self.on_job_loaded)
        self.job_tab.bctc_loaded.connect(self.on_bctc_loaded)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def on_job_loaded(self, job_data):
        """Xử lý khi job được load"""
        # Truyền thông tin job cho các tab khác
        self.form_tab.current_job = job_data
        self.bctc_tab.current_job = job_data
        self.utility_tab.current_job = job_data

        # Cập nhật trạng thái biểu mẫu
        self.form_tab.load_form_states()

    def on_bctc_loaded(self):
        """Xử lý khi BCTC được load trong JobView"""
        if self.job_tab.current_job and self.job_tab.current_job.get('key_metrics'):
            # Truyền dữ liệu job cho các tab khác
            self.bctc_tab.set_bctc_data(None, self.job_tab.current_job)
            self.form_tab.set_bctc_data(None, self.job_tab.current_job)

    def on_tab_changed(self, index):
        """Xử lý khi chuyển tab"""
        current_tab = self.tab_widget.widget(index)

        # Kiểm tra nếu chuyển sang tab BCTC hoặc Form mà chưa có dữ liệu BCTC
        if (isinstance(current_tab, (BCTCView, FormView)) and
            (not self.job_tab.current_job or
             not self.job_tab.current_job.get('bctc_file'))):
            QMessageBox.warning(
                self,
                "Cảnh báo",
                "Vui lòng chọn file BCTC trong tab Tạo/Mở Job trước!"
            )
            # Chuyển về tab Job
            self.tab_widget.setCurrentIndex(0)

    def restore_last_job(self):
        """Khôi phục job cuối cùng"""
        try:
            last_job_path = ConfigManager.get_last_job_path()
            if last_job_path:
                if self.job_tab.restore_job(last_job_path):
                    # Thông báo cho các tab khác biết job đã được khôi phục
                    self.on_job_loaded(self.job_tab.current_job)

                    # Nếu có dữ liệu BCTC, thông báo cho các tab khác
                    if self.job_tab.current_job.get('key_metrics'):
                        self.on_bctc_loaded()
        except Exception as e:
            # Log lỗi nếu cần
            print(f"Lỗi khi khôi phục job cuối cùng: {str(e)}")
            pass

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        try:
            # Lưu trạng thái hiện tại
            if hasattr(self, 'job_tab') and self.job_tab.current_job:
                # Lưu config job
                self.job_tab._save_job_config()

                # Lưu đường dẫn job cuối cùng
                ConfigManager.save_last_job(self.job_tab.current_job['path'])

        except Exception as e:
            print(f"Lỗi khi lưu trạng thái: {str(e)}")

        event.accept()