from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

class AppTheme:
    # Colors
    PRIMARY = "#2196F3"  # Xanh dương nhạt
    PRIMARY_DARK = "#1976D2"
    SECONDARY = "#757575"  # Xám
    BACKGROUND = "#FFFFFF"  # Trắng
    SURFACE = "#F5F5F5"  # Xám nhạt
    ERROR = "#D32F2F"  # Đỏ
    SUCCESS = "#4CAF50"  # Xanh lá
    TEXT_PRIMARY = "#212121"  # Đen nhạt
    TEXT_SECONDARY = "#757575"  # Xám
    BORDER = "#E0E0E0"  # Xám nhạt

    # Font sizes
    FONT_LARGE = 14
    FONT_MEDIUM = 12
    FONT_SMALL = 10

    # Spacing
    SPACING_SMALL = 8
    SPACING_MEDIUM = 16
    SPACING_LARGE = 24

    # Styles
    BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {PRIMARY_DARK};
        }}
        QPushButton:pressed {{
            background-color: {SECONDARY};
        }}
        QPushButton:disabled {{
            background-color: {SECONDARY};
            color: {TEXT_SECONDARY};
        }}
    """

    INPUT_STYLE = f"""
        QLineEdit, QDateEdit {{
            padding: 8px;
            border: 1px solid {BORDER};
            border-radius: 4px;
            background-color: {BACKGROUND};
        }}
        QLineEdit:focus, QDateEdit:focus {{
            border: 2px solid {PRIMARY};
        }}
    """

    LABEL_STYLE = f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: {FONT_MEDIUM}px;
        }}
    """

    TAB_STYLE = f"""
        QTabWidget::pane {{
            border: 1px solid {BORDER};
            background: {BACKGROUND};
        }}
        QTabBar::tab {{
            background: {SURFACE};
            padding: 8px 16px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {PRIMARY};
            color: white;
        }}
    """

    PANEL_STYLE = f"""
        QWidget#panel {{
            background-color: {SURFACE};
            border-radius: 8px;
            padding: 16px;
        }}
    """

    INFO_PANEL_STYLE = f"""
        QLabel#info_panel {{
            background-color: {SURFACE};
            padding: 16px;
            border-radius: 8px;
            color: {TEXT_PRIMARY};
        }}
    """ 