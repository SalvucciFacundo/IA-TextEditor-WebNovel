from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, 
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import requests
import json
from utils.settings import load_ollama_url, save_ollama_url, load_ollama_model, save_ollama_model
from .ollama_config_dialog import OllamaConfigDialog

class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, prompt, url, model, context=""):
        super().__init__()
        self.prompt = prompt
        self.url = url
        self.model = model
        self.context = context

    def run(self):
        try:
            # Include model in payload
            payload = {
                "model": self.model,
                "prompt": f"Context: {self.context}\n\nUser: {self.prompt}\n\nAssistant:",
                "stream": False
            }
            
            response = requests.post(self.url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                reply = data.get("response", "No response content.")
                self.finished.emit(reply)
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
            self.error.emit("Tiempo de espera agotado. El servidor tardó demasiado en responder.")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class AIChatSidebar(QWidget):
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

        # Chat History
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("El historial del chat aparecerá aquí...")
        self.layout.addWidget(self.chat_history)

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
            self.append_message("Sistema", "⚠ Por favor configura un modelo primero (haz clic en ⚙️)")
            return

        # Display user message
        self.append_message("Tú", msg)
        self.input_field.clear()
        self.input_field.setDisabled(True)
        self.send_btn.setDisabled(True)
        
        # Start worker with selected model
        self.worker = AIWorker(msg, self.ollama_url, self.ollama_model)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, reply):
        self.append_message("IA", reply)
        self.input_field.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.input_field.setFocus()

    def handle_error(self, error_msg):
        self.append_message("Sistema", f"❌ {error_msg}")
        self.input_field.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.input_field.setFocus()

    def append_message(self, sender, text):
        colors = {
            "IA": "#4ec9b0",
            "Tú": "#ce9178",
            "Sistema": "#f48771"
        }
        color = colors.get(sender, "#ffffff")
        self.chat_history.append(f"<b style='color:{color}'>{sender}:</b> {text}<br>")


