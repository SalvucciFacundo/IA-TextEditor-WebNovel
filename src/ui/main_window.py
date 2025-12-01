from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QToolBar, QFileDialog, QMessageBox, QLabel, QStatusBar, QMenu
)
from PyQt6.QtGui import QAction, QIcon, QTextDocument
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtPrintSupport import QPrinter

from .editor import NovelEditor
from .sidebar_characters import CharacterSidebar
from .sidebar_chapters import ChapterSidebar
from .sidebar_ai import AIChatSidebar
from .dialogs import SymbolDialog, NotesDialog, ProjectDialog
from utils.project_manager import ProjectManager
from utils.chapter_manager import ChapterManager
from utils.styles import DARK_THEME, LIGHT_THEME
from utils.logger import log_info
from utils.settings import load_theme_preference, save_theme_preference

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kuno Writer - Editor de Novelas con IA")
        self.resize(1200, 800)
        
        # Project Manager
        self.project_manager = ProjectManager()
        self.chapter_manager = None
        self.current_chapter = None
        
        # Dialogs
        self.symbol_dialog = None
        self.notes_dialog = None
        
        # Theme
        self.is_dark_mode = load_theme_preference()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter for 4-pane layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: Chapters and Characters
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        self.chapter_sidebar = ChapterSidebar()
        self.char_sidebar = CharacterSidebar()
        
        left_layout.addWidget(self.chapter_sidebar, 1)
        left_layout.addWidget(self.char_sidebar, 1)
        
        splitter.addWidget(left_panel)
        
        # Center: Editor
        self.editor = NovelEditor()
        splitter.addWidget(self.editor)
        
        # Right: AI Chat
        self.ai_sidebar = AIChatSidebar()
        splitter.addWidget(self.ai_sidebar)

        # Set initial sizes (20%, 60%, 20%)
        splitter.setSizes([250, 600, 250])
        splitter.setCollapsible(0, True)
        splitter.setCollapsible(2, True)

        main_layout.addWidget(splitter)

        # Toolbar
        self.create_toolbar()
        
        # Menu Bar (Project)
        self.create_menu()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.stats_label = QLabel("Palabras: 0 | Caracteres: 0 | Capítulos: 0")
        self.status_bar.addPermanentWidget(self.stats_label)

        # Connect Signals
        self.char_sidebar.insert_character_signal.connect(self.editor.insertPlainText)
        self.chapter_sidebar.chapter_selected.connect(self.load_chapter)
        self.editor.stats_updated.connect(self.update_stats_label)
        self.editor.textChanged.connect(self.auto_save_chapter)
        
        # Auto-save timer (every 60 seconds)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.save_current_chapter)
        self.auto_save_timer.start(60000)  # 60 seconds
        
        # Initial Project Check - Deferred to ensure window is shown first
        QTimer.singleShot(100, self.open_project_manager)
        
        # Apply saved theme
        self.apply_theme()

    def create_menu(self):
        menubar = self.menuBar()
        project_menu = menubar.addMenu("Proyecto")
        
        pm_action = QAction("Gestor de Proyectos", self)
        pm_action.triggered.connect(self.open_project_manager)
        project_menu.addAction(pm_action)
        
        close_project_action = QAction("Cerrar Proyecto", self)
        close_project_action.triggered.connect(self.close_project)
        project_menu.addAction(close_project_action)
        
        # View menu for theme
        view_menu = menubar.addMenu("Ver")
        self.theme_action = QAction("🌙 Modo Oscuro" if not self.is_dark_mode else "☀️ Modo Claro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

    def open_project_manager(self):
        dialog = ProjectDialog(self.project_manager, self)
        dialog.project_selected.connect(self.load_project)
        dialog.exec()

    def load_project(self, project_name):
        log_info(f"Loading project: {project_name}")
        try:
            success, path = self.project_manager.open_project(project_name)
            if success:
                self.setWindowTitle(f"Kuno Writer - {project_name}")
                
                # Initialize Chapter Manager
                self.chapter_manager = ChapterManager(path)
                self.chapter_sidebar.set_chapter_manager(self.chapter_manager)
                log_info("Chapter manager initialized.")
                
                # Load Characters
                self.char_sidebar.set_project_manager(self.project_manager)
                log_info("Characters loaded.")
                
                # Clear editor
                self.editor.clear()
                self.current_chapter = None
                
                # Load first chapter if exists
                chapters = self.chapter_manager.get_chapters()
                if chapters:
                    self.load_chapter(chapters[0])
                
                # Reset Notes Dialog if open
                if self.notes_dialog:
                    self.notes_dialog.close()
                    self.notes_dialog = None
            else:
                log_info(f"Failed to open project: {path}")
        except Exception as e:
            log_info(f"CRITICAL ERROR loading project: {e}")
            QMessageBox.critical(self, "Error Fatal", f"Error al cargar el proyecto: {e}")

    def load_chapter(self, filename):
        """Load a chapter into the editor"""
        if not self.chapter_manager:
            return
        
        # Save current chapter first
        if self.current_chapter:
            self.save_current_chapter()
        
        # Load new chapter
        content = self.chapter_manager.load_chapter(filename)
        self.editor.setPlainText(content)
        self.current_chapter = filename
        log_info(f"Loaded chapter: {filename}")

    def save_current_chapter(self):
        """Save the current chapter"""
        if self.chapter_manager and self.current_chapter:
            content = self.editor.toPlainText()
            self.chapter_manager.save_chapter(self.current_chapter, content)

    def auto_save_chapter(self):
        """Auto-save on text change (debounced)"""
        if hasattr(self, '_save_timer'):
            self._save_timer.stop()
        
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self.save_current_chapter)
        self._save_timer.start(2000)  # Save after 2 seconds of inactivity

    def save_project_data(self):
        # Save current chapter
        self.save_current_chapter()

    def close_project(self):
        """Close current project and return to project manager"""
        # Save everything first
        self.save_project_data()
        
        # Clear editor and reset state
        self.editor.clear()
        self.current_chapter = None
        self.chapter_manager = None
        self.project_manager.current_project_path = None
        
        # Clear sidebars
        self.chapter_sidebar.chapter_list.clear()
        self.char_sidebar.character_list.clear()
        
        # Reset title
        self.setWindowTitle("Kuno Writer - Editor de Novelas con IA")
        
        # Open project manager
        self.open_project_manager()

    def closeEvent(self, event):
        self.save_project_data()
        super().closeEvent(event)

    def create_toolbar(self):
        toolbar = QToolBar("Herramientas")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # File Actions
        save_action = QAction("💾 Guardar", self)
        save_action.setToolTip("Guardar capítulo actual")
        save_action.triggered.connect(self.quick_save)
        toolbar.addAction(save_action)
        
        export_action = QAction("📤 Exportar", self)
        export_action.setToolTip("Exportar a TXT o PDF")
        export_action.triggered.connect(self.save_file)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()

        # Formatting Actions
        bold_action = QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.editor.set_bold)
        toolbar.addAction(bold_action)

        italic_action = QAction("I", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.editor.set_italic)
        toolbar.addAction(italic_action)

        center_action = QAction("≡", self)
        center_action.triggered.connect(self.editor.set_alignment_center)
        toolbar.addAction(center_action)

        size_action = QAction("A+", self)
        size_action.triggered.connect(self.editor.increase_font_size)
        toolbar.addAction(size_action)

        toolbar.addSeparator()

        # Symbols
        brackets_action = QAction("[ ]", self)
        brackets_action.triggered.connect(lambda: self.editor.insert_symbol("[]"))
        toolbar.addAction(brackets_action)

        parens_action = QAction("( )", self)
        parens_action.triggered.connect(lambda: self.editor.insert_symbol("()"))
        toolbar.addAction(parens_action)

        quotes_action = QAction('“ ”', self)
        quotes_action.triggered.connect(lambda: self.editor.insert_symbol('“”'))
        toolbar.addAction(quotes_action)

        title_action = QAction("TÍTULO", self)
        title_action.triggered.connect(self.editor.format_title)
        toolbar.addAction(title_action)
        
        toolbar.addSeparator()
        
        # New Features
        symbols_btn = QAction("★ Símbolos", self)
        symbols_btn.triggered.connect(self.show_symbols)
        toolbar.addAction(symbols_btn)
        
        notes_btn = QAction("📝 Notas", self)
        notes_btn.triggered.connect(self.show_notes)
        toolbar.addAction(notes_btn)

    def show_symbols(self):
        if not self.symbol_dialog:
            self.symbol_dialog = SymbolDialog(self)
            self.symbol_dialog.symbol_selected.connect(self.editor.insertPlainText)
        self.symbol_dialog.show()
        self.symbol_dialog.raise_()
        self.symbol_dialog.activateWindow()

    def show_notes(self):
        if not self.notes_dialog:
            content = self.project_manager.load_content("notes.txt", "")
            self.notes_dialog = NotesDialog(content, self)
            self.notes_dialog.finished.connect(self.save_notes)
        self.notes_dialog.show()
        self.notes_dialog.raise_()
        self.notes_dialog.activateWindow()

    def save_notes(self):
        if self.notes_dialog:
            content = self.notes_dialog.get_content()
            self.project_manager.save_content("notes.txt", content)

    def update_stats_label(self, words, chars, chapters):
        # Get total chapters from project
        total_chapters = 0
        if self.chapter_manager:
            total_chapters = len(self.chapter_manager.get_chapters())
        
        self.stats_label.setText(f"Palabras: {words} | Caracteres: {chars} | Capítulos: {total_chapters}")

    def quick_save(self):
        """Quick save current chapter"""
        self.save_current_chapter()
        self.statusBar().showMessage("Capítulo guardado", 2000)

    def save_file(self):
        # Save to project first
        self.save_project_data()
        
        # Export option
        file_path, filter_type = QFileDialog.getSaveFileName(
            self, "Exportar Archivo", "", "Texto (*.txt);;PDF (*.pdf)"
        )
        
        if not file_path:
            return

        if filter_type == "PDF (*.pdf)" or file_path.endswith(".pdf"):
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"
            self.export_pdf(file_path)
        else:
            if not file_path.endswith(".txt"):
                file_path += ".txt"
            self.export_txt(file_path)

    def export_txt(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Éxito", "Archivo exportado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")

    def export_pdf(self, path):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        self.editor.document().print(printer)
        QMessageBox.information(self, "Éxito", "PDF exportado correctamente.")

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.is_dark_mode = not self.is_dark_mode
        save_theme_preference(self.is_dark_mode)
        self.apply_theme()
        
        # Update menu text
        self.theme_action.setText("🌙 Modo Oscuro" if not self.is_dark_mode else "☀️ Modo Claro")

    def apply_theme(self):
        """Apply the current theme"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if self.is_dark_mode:
            app.setStyleSheet(DARK_THEME)
        else:
            app.setStyleSheet(LIGHT_THEME)

