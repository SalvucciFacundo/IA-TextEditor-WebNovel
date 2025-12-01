from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, 
    QHBoxLayout, QInputDialog, QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt

class ChapterSidebar(QWidget):
    chapter_selected = pyqtSignal(str)  # Emits chapter filename

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Title
        title = QLabel("Capítulos")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        self.layout.addWidget(title)

        # List
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.on_item_clicked)
        self.layout.addWidget(self.chapter_list)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Nuevo Capítulo")
        self.add_btn.clicked.connect(self.add_chapter)
        
        self.rename_btn = QPushButton("✎")
        self.rename_btn.setToolTip("Renombrar Capítulo")
        self.rename_btn.clicked.connect(self.rename_chapter)
        
        self.del_btn = QPushButton("🗑")
        self.del_btn.setObjectName("DeleteButton")
        self.del_btn.setToolTip("Eliminar Capítulo")
        self.del_btn.clicked.connect(self.delete_chapter)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.rename_btn)
        btn_layout.addWidget(self.del_btn)
        
        self.layout.addLayout(btn_layout)

        # Data
        self.chapter_manager = None

    def set_chapter_manager(self, cm):
        self.chapter_manager = cm
        self.refresh_list()

    def refresh_list(self):
        self.chapter_list.clear()
        if self.chapter_manager:
            chapters = self.chapter_manager.get_chapters()
            self.chapter_list.addItems(chapters)

    def add_chapter(self):
        if not self.chapter_manager:
            return
        
        title, ok = QInputDialog.getText(self, "Nuevo Capítulo", "Título del capítulo:")
        if ok and title:
            filename = self.chapter_manager.create_chapter(title)
            self.refresh_list()
            # Select the new chapter
            items = self.chapter_list.findItems(filename, Qt.MatchFlag.MatchExactly)
            if items:
                self.chapter_list.setCurrentItem(items[0])
                self.chapter_selected.emit(filename)

    def rename_chapter(self):
        if not self.chapter_manager:
            return
        
        current_item = self.chapter_list.currentItem()
        if not current_item:
            return
        
        old_filename = current_item.text()
        # Extract current title
        parts = old_filename.replace('.txt', '').split(' - ', 1)
        current_title = parts[1] if len(parts) == 2 else ""
        
        new_title, ok = QInputDialog.getText(
            self, "Renombrar Capítulo", "Nuevo título:", text=current_title
        )
        if ok and new_title:
            new_filename = self.chapter_manager.rename_chapter(old_filename, new_title)
            self.refresh_list()
            # Reselect
            items = self.chapter_list.findItems(new_filename, Qt.MatchFlag.MatchExactly)
            if items:
                self.chapter_list.setCurrentItem(items[0])

    def delete_chapter(self):
        if not self.chapter_manager:
            return
        
        current_item = self.chapter_list.currentItem()
        if not current_item:
            return
        
        filename = current_item.text()
        confirm = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar '{filename}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.chapter_manager.delete_chapter(filename)
            self.refresh_list()

    def on_item_clicked(self, item):
        self.chapter_selected.emit(item.text())
