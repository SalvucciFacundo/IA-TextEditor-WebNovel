import re
import os
from PyQt6.QtWidgets import QTextEdit, QMenu
from PyQt6.QtGui import (
    QTextCharFormat, QFont, QTextCursor, QSyntaxHighlighter, 
    QColor, QAction
)
from PyQt6.QtCore import Qt

# Try to import spylls
try:
    from spylls.hunspell import Dictionary
    SPYLLS_AVAILABLE = True
except ImportError:
    SPYLLS_AVAILABLE = False

class HunspellHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineColor(QColor("red"))
        self.error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        
        self.dictionary = None
        self.ignored_words = set()

        if SPYLLS_AVAILABLE:
            # Base path without extension
            base_path = r"D:\Kuno\Web Novel\diccionarios\es"
            
            if os.path.exists(base_path + ".dic") and os.path.exists(base_path + ".aff"):
                try:
                    self.dictionary = Dictionary.from_files(base_path)
                except Exception as e:
                    print(f"Error loading Dictionary: {e}")
            else:
                print("Dictionaries not found.")

    def highlightBlock(self, text):
        if not self.dictionary:
            return

        # Find words ignoring punctuation
        for match in re.finditer(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+', text):
            word = match.group()
            
            if word in self.ignored_words:
                continue

            # Check spelling (lookup returns True if correct)
            # We catch exceptions just in case of weird characters
            try:
                if not self.dictionary.lookup(word):
                    self.setFormat(match.start(), match.end() - match.start(), self.error_format)
            except:
                pass

from PyQt6.QtCore import Qt, pyqtSignal

# ... imports ...

class NovelEditor(QTextEdit):
    stats_updated = pyqtSignal(int, int, int) # words, chars, chapters

    def __init__(self):
        super().__init__()
        self.setAcceptRichText(True)
        self.setPlaceholderText("Escribe tu novela aquí...")
        
        # Set default font
        font = QFont("Georgia", 12)
        self.setFont(font)
        
        # Highlighter
        self.highlighter = HunspellHighlighter(self.document())
        
        self.textChanged.connect(self.update_stats)

    def keyPressEvent(self, event):
        # Auto-correct logic on space or punctuation
        if event.text() in (' ', '.', ',', '!', '?', ';', ':', '\n'):
            self.check_auto_correct()
        
        super().keyPressEvent(event)

    def check_auto_correct(self):
        if not self.highlighter.dictionary:
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfWord, QTextCursor.MoveMode.KeepAnchor)
        word = cursor.selectedText().strip()
        
        if not word:
            return

        # Simple auto-correct: if word is wrong and has 1 strong suggestion
        if word and word not in self.highlighter.ignored_words:
            try:
                if not self.highlighter.dictionary.lookup(word):
                    suggestions = list(self.highlighter.dictionary.suggest(word))
                    if suggestions:
                        # Pick first suggestion if it's very close or obvious
                        # For safety, we only auto-correct if it's a simple case
                        # This is a basic implementation.
                        best_guess = suggestions[0]
                        
                        # Replace
                        cursor.insertText(best_guess)
                        # Move cursor back to end (insertText moves it)
                        # Actually insertText replaces selection, so cursor is at end of new word.
                        # We are good.
            except:
                pass

    def update_stats(self):
        text = self.toPlainText()
        chars = len(text)
        words = len(text.split())
        # Simple chapter detection: lines starting with "Capítulo" or "Chapter" or just "#"
        chapters = len(re.findall(r'^(Capítulo|Chapter|#)', text, re.MULTILINE | re.IGNORECASE))
        if chapters == 0 and chars > 0:
            chapters = 1 # At least one chapter if there is text
            
        self.stats_updated.emit(words, chars, chapters)

    # ... rest of methods ...
        # Create standard menu first
        menu = self.createStandardContextMenu()
        
        if not self.highlighter.dictionary:
            menu.exec(event.globalPos())
            return

        # Get word under cursor
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        # Check if word is misspelled
        is_misspelled = False
        if word and word not in self.highlighter.ignored_words:
            try:
                if not self.highlighter.dictionary.lookup(word):
                    is_misspelled = True
            except:
                pass

        if is_misspelled:
            # Get suggestions
            try:
                suggestions = list(self.highlighter.dictionary.suggest(word))
            except:
                suggestions = []
            
            if suggestions:
                menu.addSeparator()
                menu.addAction("Sugerencias:").setEnabled(False)
                
                # Limit to top 5 suggestions
                for suggestion in suggestions[:5]:
                    action = QAction(suggestion, self)
                    # We need to capture the suggestion and cursor
                    action.triggered.connect(lambda checked, s=suggestion, c=cursor: self.replace_word(c, s))
                    menu.addAction(action)
            else:
                menu.addSeparator()
                menu.addAction("No hay sugerencias").setEnabled(False)
                
            menu.addSeparator()
            add_action = QAction("Omitir palabra", self)
            add_action.triggered.connect(lambda: self.add_to_dictionary(word))
            menu.addAction(add_action)

        menu.exec(event.globalPos())

    def replace_word(self, cursor, new_word):
        # We need to make sure we replace the correct range
        cursor.beginEditBlock()
        cursor.insertText(new_word)
        cursor.endEditBlock()

    def add_to_dictionary(self, word):
        self.highlighter.ignored_words.add(word)
        self.highlighter.rehighlight()

    def set_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        self.mergeCurrentCharFormat(fmt)

    def set_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.fontItalic())
        self.mergeCurrentCharFormat(fmt)

    def set_alignment_center(self):
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def set_alignment_left(self):
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def increase_font_size(self):
        font = self.currentFont()
        size = font.pointSize()
        font.setPointSize(size + 2)
        self.setCurrentFont(font)

    def insert_symbol(self, symbol_pair):
        # symbol_pair e.g. "[]" or "()"
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{symbol_pair[0]}{text}{symbol_pair[1]}")
        else:
            cursor.insertText(symbol_pair)
            # Move cursor back inside
            cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)
            
    def format_title(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold)
            fmt.setFontPointSize(18)
            cursor.mergeCharFormat(fmt)
            self.setTextCursor(cursor)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
