from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
import requests

class OllamaConfigDialog(QDialog):
    def __init__(self, current_url, current_model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Ollama")
        self.resize(450, 200)
        
        self.selected_model = current_model
        self.selected_url = current_url
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # URL Configuration
        url_label = QLabel("URL del endpoint de Ollama:")
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setText(current_url)
        layout.addWidget(self.url_input)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Detectar modelos")
        refresh_btn.clicked.connect(self.refresh_models)
        layout.addWidget(refresh_btn)
        
        # Model Selection
        model_label = QLabel("Modelo disponible:")
        layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setPlaceholderText("Selecciona un modelo...")
        layout.addWidget(self.model_combo)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_config)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Auto-refresh on open
        self.refresh_models()

    def refresh_models(self):
        """Fetch available models from Ollama"""
        self.status_label.setText("Detectando modelos...")
        self.model_combo.clear()
        
        try:
            # Get base URL for tags endpoint
            base_url = self.url_input.text().strip()
            if base_url.endswith('/api/generate'):
                base_url = base_url.replace('/api/generate', '')
            
            tags_url = f"{base_url}/api/tags"
            
            response = requests.get(tags_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                if models:
                    model_names = [model['name'] for model in models]
                    self.model_combo.addItems(model_names)
                    self.status_label.setText(f"✓ {len(model_names)} modelo(s) encontrado(s)")
                    self.status_label.setStyleSheet("color: #4ec9b0; font-size: 11px;")
                    
                    # Select previously selected model if available
                    if self.selected_model and self.selected_model in model_names:
                        self.model_combo.setCurrentText(self.selected_model)
                else:
                    self.status_label.setText("⚠ No hay modelos disponibles. Ejecuta 'ollama pull <modelo>' primero.")
                    self.status_label.setStyleSheet("color: #f48771; font-size: 11px;")
            else:
                self.status_label.setText(f"❌ Error al obtener modelos: {response.status_code}")
                self.status_label.setStyleSheet("color: #f48771; font-size: 11px;")
                
        except requests.exceptions.ConnectionError:
            self.status_label.setText("❌ No se pudo conectar a Ollama. Verifica que esté corriendo.")
            self.status_label.setStyleSheet("color: #f48771; font-size: 11px;")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: #f48771; font-size: 11px;")

    def save_config(self):
        """Save configuration and close dialog"""
        url = self.url_input.text().strip()
        model = self.model_combo.currentText()
        
        if not url:
            QMessageBox.warning(self, "URL requerida", "Por favor ingresa la URL del endpoint.")
            return
        
        if not model:
            reply = QMessageBox.question(
                self, 
                "Modelo no seleccionado", 
                "No has seleccionado ningún modelo. ¿Deseas continuar de todos modos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.selected_url = url
        self.selected_model = model
        self.accept()

    def get_config(self):
        """Return selected configuration"""
        return self.selected_url, self.selected_model
