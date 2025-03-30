from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

class AppTheme:
    # Colors
    PRIMARY = "#2196F3"
    SECONDARY = "#757575"
    BACKGROUND = "#FFFFFF"
    TEXT = "#212121"
    
    # Font sizes
    FONT_SMALL = 12
    FONT_MEDIUM = 14
    FONT_LARGE = 16
    
    # Spacing
    SPACING_SMALL = 4
    SPACING_MEDIUM = 8
    SPACING_LARGE = 16
    
    # Styles
    BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #1976D2;
        }}
        QPushButton:pressed {{
            background-color: #0D47A1;
        }}
    """
    
    BUTTON_PRIMARY_STYLE = BUTTON_STYLE
    
    BUTTON_SECONDARY_STYLE = f"""
        QPushButton {{
            background-color: {SECONDARY};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #616161;
        }}
        QPushButton:pressed {{
            background-color: #424242;
        }}
    """
    
    INPUT_STYLE = f"""
        QLineEdit, QDateEdit {{
            padding: 6px;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            background-color: white;
        }}
        QLineEdit:focus, QDateEdit:focus {{
            border-color: {PRIMARY};
        }}
    """
    
    CHECKBOX_STYLE = f"""
        QCheckBox {{
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
    """
    
    TEXT_AREA_STYLE = f"""
        QTextEdit {{
            padding: 8px;
            border: 1px solid {SECONDARY};
            border-radius: 4px;
        }}
    """

    # Styles
    LABEL_STYLE = f"""
        QLabel {{
            color: {TEXT};
        }}
    """

    TAB_STYLE = f"""
        QTabWidget::pane {{
            border: 1px solid {SECONDARY};
            background: {BACKGROUND};
        }}
        QTabBar::tab {{
            background: {SECONDARY};
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
            background-color: {BACKGROUND};
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 16px;
        }}
    """

    INFO_PANEL_STYLE = f"""
        QLabel#info_panel {{
            background-color: #F5F5F5;
            padding: {SPACING_MEDIUM}px;
            border-radius: 4px;
            color: {TEXT};
        }}
    """ 