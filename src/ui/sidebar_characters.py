from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, 
    QHBoxLayout, QInputDialog, QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt

class CharacterSidebar(QWidget):
    insert_character_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Title
        title = QLabel("Personajes")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        self.layout.addWidget(title)

        # List
        self.character_list = QListWidget()
        self.character_list.itemClicked.connect(self.on_item_clicked)
        self.layout.addWidget(self.character_list)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Agregar Personaje")
        self.add_btn.clicked.connect(self.add_character)
        
        self.edit_btn = QPushButton("✎")
        self.edit_btn.setToolTip("Editar Personaje")
        self.edit_btn.clicked.connect(self.edit_character)
        
        self.del_btn = QPushButton("🗑")
        self.del_btn.setObjectName("DeleteButton")
        self.del_btn.setToolTip("Eliminar Personaje")
        self.del_btn.clicked.connect(self.delete_character)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        
        self.layout.addLayout(btn_layout)

        # Initial Data
        self.characters = []
        self.project_manager = None

    def set_project_manager(self, pm):
        self.project_manager = pm
        self.load_characters()

    def load_characters(self):
        if self.project_manager:
            self.characters = self.project_manager.load_content("characters.json", [])
            self.refresh_list()

    def save_characters(self):
        if self.project_manager:
            self.project_manager.save_content("characters.json", self.characters)

    def refresh_list(self):
        self.character_list.clear()
        self.character_list.addItems(self.characters)

    def add_character(self):
        name, ok = QInputDialog.getText(self, "Nuevo Personaje", "Nombre del personaje:")
        if ok and name:
            self.characters.append(name)
            self.refresh_list()
            self.save_characters()

    def edit_character(self):
        current_item = self.character_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.text()
        name, ok = QInputDialog.getText(self, "Editar Personaje", "Nuevo nombre:", text=old_name)
        if ok and name:
            index = self.characters.index(old_name)
            self.characters[index] = name
            self.refresh_list()
            self.save_characters()

    def delete_character(self):
        current_item = self.character_list.currentItem()
        if not current_item:
            return
        
        name = current_item.text()
        confirm = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar a {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.characters.remove(name)
            self.refresh_list()
            self.save_characters()

    def on_item_clicked(self, item):
        # Emit signal to insert text with dialogue format
        self.insert_character_signal.emit(f"{item.text()}: ")
