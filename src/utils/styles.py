# Modern Dark Theme for the Editor

DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Text Editor */
QTextEdit {
    background-color: #252526;
    color: #d4d4d4;
    border: none;
    padding: 20px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 16px;
    selection-background-color: #264f78;
}

/* Sidebars (Lists and Chat) */
QListWidget, QListView {
    background-color: #252526;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    padding: 5px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #37373d;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #094771;
}

QPushButton#DeleteButton {
    background-color: #ce3838;
}

QPushButton#DeleteButton:hover {
    background-color: #d94545;
}

/* Input Fields */
QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #3e3e42;
    color: #cccccc;
    padding: 6px;
    border-radius: 4px;
}

QLineEdit:focus {
    border: 1px solid #0e639c;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #424242;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #3e3e42;
}

/* Toolbar */
QToolBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3e3e42;
    spacing: 10px;
    padding: 5px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px;
}

QToolButton:hover {
    background-color: #3e3e42;
    border: 1px solid #505050;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
    color: #000000;
}

QWidget {
    background-color: #f5f5f5;
    color: #2c2c2c;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Text Editor */
QTextEdit {
    background-color: #ffffff;
    color: #1a1a1a;
    border: 1px solid #d0d0d0;
    padding: 20px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 16px;
    selection-background-color: #b3d7ff;
}

/* Sidebars (Lists and Chat) */
QListWidget, QListView {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 5px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #e3f2fd;
    color: #000000;
}

QListWidget::item:hover {
    background-color: #f0f0f0;
}

/* Buttons */
QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton#DeleteButton {
    background-color: #d13438;
}

QPushButton#DeleteButton:hover {
    background-color: #e81123;
}

/* Input Fields */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    color: #1a1a1a;
    padding: 6px;
    border-radius: 4px;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #f5f5f5;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #d0d0d0;
}

/* Toolbar */
QToolBar {
    background-color: #f0f0f0;
    border-bottom: 1px solid #d0d0d0;
    spacing: 10px;
    padding: 5px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px;
}

QToolButton:hover {
    background-color: #e0e0e0;
    border: 1px solid #c0c0c0;
}

/* Menu Bar */
QMenuBar {
    background-color: #f0f0f0;
    color: #1a1a1a;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
}

QMenu::item:selected {
    background-color: #e3f2fd;
}

/* Status Bar */
QStatusBar {
    background-color: #f0f0f0;
    color: #1a1a1a;
}
"""
