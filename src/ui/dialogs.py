from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QLineEdit, QTextEdit, QGridLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

class ProjectDialog(QDialog):
    project_selected = pyqtSignal(str)

    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestor de Proyectos")
        self.resize(400, 300)
        self.pm = project_manager
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.pm.get_projects())
        self.list_widget.itemDoubleClicked.connect(self.open_project)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton("Nuevo Proyecto")
        new_btn.clicked.connect(self.create_project)
        
        open_btn = QPushButton("Abrir")
        open_btn.clicked.connect(self.open_project)
        
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(open_btn)
        
        layout.addLayout(btn_layout)

    def create_project(self):
        name, ok = QInputDialog.getText(self, "Nuevo Proyecto", "Nombre del proyecto:")
        if ok and name:
            success, msg = self.pm.create_project(name)
            if success:
                self.list_widget.clear()
                self.list_widget.addItems(self.pm.get_projects())
            else:
                QMessageBox.warning(self, "Error", msg)

    def open_project(self):
        item = self.list_widget.currentItem()
        if item:
            self.project_selected.emit(item.text())
            self.accept()

class SymbolDialog(QDialog):
    symbol_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Símbolos")
        self.resize(300, 200)
        
        layout = QGridLayout()
        self.setLayout(layout)

        symbols = [
            "♥", "♡", "★", "☆", "♪", "♫", "♭", "♯", 
            "«", "»", "—", "–", "…", "°", "∞", "†",
            "‡", "§", "¶", "©", "®", "™", "←", "→"
        ]

        row = 0
        col = 0
        for sym in symbols:
            btn = QPushButton(sym)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, s=sym: self.symbol_selected.emit(s))
            layout.addWidget(btn, row, col)
            col += 1
            if col > 5:
                col = 0
                row += 1

class NotesDialog(QDialog):
    def __init__(self, initial_content="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notas del Autor")
        self.resize(400, 500)
        # Non-modal to allow typing in editor while viewing notes
        self.setWindowModality(Qt.WindowModality.NonModal)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.editor = QTextEdit()
        self.editor.setPlainText(initial_content)
        layout.addWidget(self.editor)
        
        save_btn = QPushButton("Guardar y Cerrar")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

    def get_content(self):
        return self.editor.toPlainText()
