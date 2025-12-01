    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, 
    QHBoxLayout, QMessageBox, QCheckBox, QScrollArea, QFrame, QSizePolicy,
    QSpacerItem, QComboBox
)
from PyQt6.QtGui import QTextCursor, QDesktopServices
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
import requests
import json
import os
import re
from utils.settings import (
    load_ollama_url, save_ollama_url, load_ollama_model, save_ollama_model,
    load_style_preference, save_style_preference
)
from .ollama_config_dialog import OllamaConfigDialog

class AIWorker(QThread):
    finished = pyqtSignal(str)
    stream_update = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, prompt, url, model, system_template="", context=""):
        super().__init__()
        self.prompt = prompt
        self.url = url
        self.model = model
        self.system_template = system_template
        self.context = context

    def run(self):
        try:
            # Construct final prompt with system template if present
            final_prompt = self.prompt
            if self.system_template:
                # Replace {{ .Prompt }} in template or prepend it
                if "{{ .Prompt }}" in self.system_template:
                    final_prompt = self.system_template.replace("{{ .Prompt }}", self.prompt)
                else:
                    final_prompt = f"{self.system_template}\n\n{self.prompt}"

            # Include model in payload
            payload = {
                "model": self.model,
                "prompt": final_prompt,
                "stream": True,
                "options": {
                    "temperature": 0.95,
                    "top_p": 0.95,
                    "top_k": 50,
                    "repeat_penalty": 1.1
                }
            }
            
            # Increased timeout to 120s (wait for connection/first byte)
            with requests.post(self.url, json=payload, stream=True, timeout=120) as response:
                if response.status_code == 200:
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            try:
                                json_response = json.loads(line)
                                chunk = json_response.get("response", "")
                                if chunk:
                                    full_response += chunk
                                    self.stream_update.emit(chunk)
                                if json_response.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                    self.finished.emit(full_response)
                else:
                    # Parse error message
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", response.text)
                    except:
                        error_msg = response.text
                    
                    if "no model" in error_msg.lower() or "model not found" in error_msg.lower():
                        self.error.emit(f"Modelo '{self.model}' no encontrado. Verifica que esté disponible en Ollama.")
                    else:
                        self.error.emit(f"Error API ({response.status_code}): {error_msg}")

        except requests.exceptions.ConnectionError:
            self.error.emit("No se pudo conectar al servidor Ollama. Verifica que esté corriendo en la URL configurada.")
        except requests.exceptions.Timeout:
            self.error.emit("TIMEOUT")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class ChatBubble(QFrame):
    action_requested = pyqtSignal(str, str) # type, content
    regenerate_requested = pyqtSignal()
    reject_requested = pyqtSignal()

    def __init__(self, sender, text="", parent=None):
        super().__init__(parent)
        self.sender_name = sender
        self.full_text = text
        self.action_type = "text" # text, create_chapter
        self.action_data = ""
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        
        # Styles
        if sender == "IA":
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #2d2d2d;
                    border-radius: 10px;
                    border: 1px solid #3e3e3e;
                }
                QLabel { color: #e0e0e0; }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #3e3e3e;
                    border-radius: 10px;
                }
                QLabel { color: #ffffff; }
            """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel(sender)
        header.setStyleSheet(f"font-weight: bold; color: {'#4ec9b0' if sender == 'IA' else '#ce9178'};")
        self.layout.addWidget(header)
        
        # Content
        self.content_label = QLabel(text)
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layout.addWidget(self.content_label)
        
        # Action Buttons (Only for IA)
        if sender == "IA":
            self.buttons_layout = QHBoxLayout()
            self.buttons_layout.setSpacing(5)
            
            self.btn_accept = QPushButton("✅ Aceptar")
            self.btn_accept.setToolTip("Insertar en el editor")
            self.btn_accept.clicked.connect(self.on_accept)
            self.btn_accept.setStyleSheet("background-color: #2d4d3d; border: none; padding: 5px; border-radius: 4px;")
            
            self.btn_regen = QPushButton("🔁 Regenerar")
            self.btn_regen.setToolTip("Volver a generar respuesta")
            self.btn_regen.clicked.connect(self.regenerate_requested.emit)
            self.btn_regen.setStyleSheet("background-color: #2d2d4d; border: none; padding: 5px; border-radius: 4px;")
            
            self.btn_reject = QPushButton("❌ Rechazar")
            self.btn_reject.setToolTip("Descartar")
            self.btn_reject.clicked.connect(self.reject_requested.emit)
            self.btn_reject.setStyleSheet("background-color: #4d2d2d; border: none; padding: 5px; border-radius: 4px;")
            
            self.buttons_layout.addWidget(self.btn_accept)
            self.buttons_layout.addWidget(self.btn_regen)
            self.buttons_layout.addWidget(self.btn_reject)
            
            self.layout.addLayout(self.buttons_layout)
            
            # Hide buttons initially until generation is done
            self.set_buttons_visible(False)

    def set_text(self, text):
        self.full_text = text
        
        # Check for actions
        if "<<CREATE_CHAPTER:" in text:
            try:
                start = text.index("<<CREATE_CHAPTER:") + 17
                end = text.index(">>", start)
                title = text[start:end].strip()
                self.action_type = "create_chapter"
                self.action_data = title
                display_text = f"📂 <b>Acción Propuesta:</b> Crear capítulo titulado <i>'{title}'</i>"
                self.content_label.setText(display_text)
                self.btn_accept.setText("✅ Crear Capítulo")
            except:
                self.content_label.setText(text)
        else:
            self.action_type = "text"
            self.action_data = text
            self.content_label.setText(text)

    def append_text(self, chunk):
        self.full_text += chunk
        self.set_text(self.full_text)

    def set_buttons_visible(self, visible):
        for i in range(self.buttons_layout.count()):
            widget = self.buttons_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(visible)

    def on_accept(self):
        self.action_requested.emit(self.action_type, self.action_data)

class AIChatSidebar(QWidget):
    insert_text_requested = pyqtSignal(str)
    create_chapter_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Load saved configuration
        self.ollama_url = load_ollama_url()
        self.ollama_model = load_ollama_model()

        # Title and Connection Button
        header_layout = QHBoxLayout()
        title = QLabel("Asistente IA")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(title)
        
        self.connect_btn = QPushButton("⚙️")
        self.connect_btn.setToolTip("Configurar conexión Ollama")
        self.connect_btn.setMaximumWidth(40)
        self.connect_btn.clicked.connect(self.configure_connection)
        header_layout.addWidget(self.connect_btn)
        
        self.layout.addLayout(header_layout)
        
        # Status label
        self.status_label = QLabel("No conectado")
        self.status_label.setStyleSheet("font-size: 11px; color: #888;")
        self.layout.addWidget(self.status_label)

        # Style Selection Area
        style_layout = QHBoxLayout()
        
        self.auto_style_cb = QCheckBox("Auto Estilo")
        self.auto_style_cb.setToolTip("Detectar automáticamente el estilo narrativo")
        self.auto_style_cb.stateChanged.connect(self.toggle_style_mode)
        style_layout.addWidget(self.auto_style_cb)
        
        self.style_combo = QComboBox()
        self.style_combo.setToolTip("Seleccionar estilo narrativo manualmente")
        self.style_combo.addItem("Normal") # Default
        self.load_modelfiles()
        style_layout.addWidget(self.style_combo)
        
        self.layout.addLayout(style_layout)

        # Agent Mode Checkbox
        self.agent_mode_cb = QCheckBox("Modo Agente")
        self.agent_mode_cb.setToolTip("Permite a la IA ejecutar acciones como crear capítulos")
        self.layout.addWidget(self.agent_mode_cb)
        
        # Load preferences
        prefs = load_style_preference()
        self.auto_style_cb.setChecked(prefs['auto_style'])
        current_style = prefs['last_style']
        index = self.style_combo.findText(current_style)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
        
        self.toggle_style_mode() # Apply initial state

        # Chat History (Scroll Area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch() # Push messages to bottom
        
        self.scroll_area.setWidget(self.chat_container)
        self.layout.addWidget(self.scroll_area)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe tu consulta...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Enviar")
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        self.layout.addLayout(input_layout)
        
        # Update status
        self.update_status()

        self.current_ai_bubble = None
        self.last_prompt = ""

    def configure_connection(self):
        """Open dialog to configure Ollama connection"""
        dialog = OllamaConfigDialog(self.ollama_url, self.ollama_model, self)
        
        if dialog.exec():
            url, model = dialog.get_config()
            self.ollama_url = url
            self.ollama_model = model
            
            save_ollama_url(url)
            save_ollama_model(model)
            
            self.update_status()
            QMessageBox.information(
                self, 
                "Configuración guardada", 
                f"URL: {url}\nModelo: {model if model else 'No seleccionado'}"
            )

    def update_status(self):
        """Update connection status label"""
        if self.ollama_model:
            self.status_label.setText(f"Modelo: {self.ollama_model}")
            self.status_label.setStyleSheet("font-size: 11px; color: #4ec9b0;")
        else:
            self.status_label.setText("⚠ Modelo no configurado")
            self.status_label.setStyleSheet("font-size: 11px; color: #f48771;")

    def send_message(self):
        msg = self.input_field.text().strip()
        if not msg:
            return
        
        # Check if model is configured
        if not self.ollama_model:
            self.add_system_message("⚠ Por favor configura un modelo primero (haz clic en ⚙️)")
            return

        self.last_prompt = msg
        self.process_message(msg)

    def load_modelfiles(self):
        """Load available Modelfiles from directory"""
        modelfiles_dir = r"d:\Kuno\Web Novel\modelfiles"
        if os.path.exists(modelfiles_dir):
            files = [f.replace(".Modelfile", "") for f in os.listdir(modelfiles_dir) if f.endswith(".Modelfile")]
            self.style_combo.addItems(sorted(files))

    def toggle_style_mode(self):
        """Enable/Disable combo based on auto mode"""
        is_auto = self.auto_style_cb.isChecked()
        self.style_combo.setEnabled(not is_auto)
        
        # Save preference
        save_style_preference(is_auto, self.style_combo.currentText())

    def get_modelfile_content(self, style_name):
        """Read TEMPLATE from Modelfile"""
        if style_name == "Normal":
            return ""
            
        path = os.path.join(r"d:\Kuno\Web Novel\modelfiles", f"{style_name}.Modelfile")
        if not os.path.exists(path):
            return ""
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract TEMPLATE content between quotes
                match = re.search(r'TEMPLATE """(.*?)"""', content, re.DOTALL)
                if match:
                    return match.group(1).strip()
        except Exception as e:
            print(f"Error reading modelfile: {e}")
        return ""

    def detect_style(self, prompt):
        """Simple keyword detection for style"""
        prompt = prompt.lower()
        keywords = {
            "Peleas": ["pelea", "combate", "golpe", "sangre", "ataque", "lucha", "batalla"],
            "Paisajes": ["paisaje", "lugar", "ambiente", "cielo", "bosque", "montaña", "descripción", "entorno"],
            "Erotismo": ["erotico", "sexo", "deseo", "pasión", "cuerpo", "piel", "beso", "íntimo"],
            "Dialogos": ["diálogo", "conversación", "hablar", "discusión", "charla"],
            "Humor": ["chiste", "gracioso", "humor", "risa", "broma", "sátira", "cómico"],
            "Suspenso": ["miedo", "terror", "suspenso", "tensión", "oscuro", "sombra", "peligro"],
            "Romance": ["amor", "romance", "corazón", "sentimiento", "pareja", "enamorad"],
            "SciFi": ["futuro", "tecnología", "robot", "espacio", "nave", "ciencia ficción", "cyber"],
            "Fantasia": ["magia", "dragón", "hechizo", "reino", "espada", "fantasía", "elfo"],
            "Misterio": ["misterio", "crimen", "pista", "detective", "asesino", "enigma"],
            "Filosofia": ["filosofía", "reflexión", "vida", "muerte", "existencia", "pensamiento"],
            "Historica": ["historia", "pasado", "siglo", "época", "antiguo", "medieval"],
            "Lirica": ["poema", "poesía", "verso", "lírico", "bello", "hermoso"]
        }
        
        for style, keys in keywords.items():
            if any(k in prompt for k in keys):
                return style
        return "Normal"

    def process_message(self, msg):
        # Display user message
        self.add_message_bubble("Tú", msg)
        self.input_field.clear()
        self.input_field.setDisabled(True)
        self.send_btn.setDisabled(True)
        
        # Prepare AI bubble
        self.current_ai_bubble = self.add_message_bubble("IA", "")
        
        # Determine Style
        style = "Normal"
        if self.auto_style_cb.isChecked():
            style = self.detect_style(msg)
            # Update combo visually to show detected style (optional, but good feedback)
            index = self.style_combo.findText(style)
            if index >= 0:
                self.style_combo.setCurrentIndex(index)
        else:
            style = self.style_combo.currentText()
            # Save manual selection
            save_style_preference(False, style)

        # Get Template
        system_template = self.get_modelfile_content(style)
        
        # Agent Mode Override/Injection
        if self.agent_mode_cb.isChecked():
            agent_instr = (
                "INSTRUCCIÓN DEL SISTEMA: Eres un asistente narrativo. "
                "Si el usuario pide crear un capítulo, responde ÚNICAMENTE con el formato: <<CREATE_CHAPTER: Título del Capítulo>>. "
                "Si pide texto, genéralo normalmente sin comillas."
            )
            if system_template:
                system_template = f"{system_template}\n\n{agent_instr}"
            else:
                system_template = agent_instr

        # Start worker
        self.worker = AIWorker(msg, self.ollama_url, self.ollama_model, system_template=system_template)
        self.worker.stream_update.connect(self.handle_stream_update)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def add_message_bubble(self, sender, text):
        bubble = ChatBubble(sender, text)
        if sender == "IA":
            bubble.action_requested.connect(self.handle_action)
            bubble.regenerate_requested.connect(self.handle_regenerate)
            bubble.reject_requested.connect(lambda: self.handle_reject(bubble))
        
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
        
        return bubble

    def add_system_message(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: #f48771; font-size: 11px; margin: 5px;")
        label.setWordWrap(True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, label)

    def handle_stream_update(self, chunk):
        if self.current_ai_bubble:
            self.current_ai_bubble.append_text(chunk)
            # Auto scroll
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )

    def handle_response(self, reply):
        if self.current_ai_bubble:
            self.current_ai_bubble.set_buttons_visible(True)
            
        self.input_field.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.input_field.setFocus()

    def handle_error(self, error_msg):
        if error_msg == "TIMEOUT":
            self.add_system_message("⚠ El modelo está tardando demasiado.")
            self.input_field.setText(self.last_prompt)
        else:
            self.add_system_message(f"❌ {error_msg}")
        
        if self.current_ai_bubble:
            self.current_ai_bubble.deleteLater()
            self.current_ai_bubble = None

        self.input_field.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.input_field.setFocus()

    def handle_action(self, action_type, data):
        if action_type == "text":
            self.insert_text_requested.emit(data)
        elif action_type == "create_chapter":
            self.create_chapter_requested.emit(data)

    def handle_regenerate(self):
        # Remove current bubble and retry
        if self.current_ai_bubble:
            self.current_ai_bubble.deleteLater()
        self.process_message(self.last_prompt)

    def handle_reject(self, bubble):
        bubble.deleteLater()

    def append_message(self, sender, text):
        # Deprecated, kept for compatibility if needed
        self.add_message_bubble(sender, text)



