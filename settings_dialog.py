
import configparser

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QLineEdit, 
    QPushButton, QDoubleSpinBox, QTextEdit
)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings or {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Settings')
        layout = QFormLayout()

        # Input fields for general settings
        self.screenWidthInput = QSpinBox(self)
        self.screenWidthInput.setRange(100, 1920)
        self.screenWidthInput.setValue(self.settings.get('screenWidth', 800))
        layout.addRow('Screen Width:', self.screenWidthInput)

        self.screenHeightInput = QSpinBox(self)
        self.screenHeightInput.setRange(100, 1080)
        self.screenHeightInput.setValue(self.settings.get('screenHeight', 600))
        layout.addRow('Screen Height:', self.screenHeightInput)

        self.apiKeyInput = QLineEdit(self)
        self.apiKeyInput.setText(self.settings.get('apiKey', ''))
        layout.addRow('API Key:', self.apiKeyInput)

        self.windowXInput = QSpinBox(self)
        self.windowXInput.setRange(0, 1920)
        self.windowXInput.setValue(self.settings.get('windowX', 100))
        layout.addRow('Window X:', self.windowXInput)

        self.windowYInput = QSpinBox(self)
        self.windowYInput.setRange(0, 1080)
        self.windowYInput.setValue(self.settings.get('windowY', 100))
        layout.addRow('Window Y:', self.windowYInput)

        self.windowWidthInput = QSpinBox(self)
        self.windowWidthInput.setRange(100, 1920)
        self.windowWidthInput.setValue(self.settings.get('windowWidth', 400))
        layout.addRow('Window Width:', self.windowWidthInput)

        self.windowHeightInput = QSpinBox(self)
        self.windowHeightInput.setRange(100, 1080)
        self.windowHeightInput.setValue(self.settings.get('windowHeight', 300))
        layout.addRow('Window Height:', self.windowHeightInput)

        # Input fields for model parameters
        self.temperatureInput = QDoubleSpinBox(self)
        self.temperatureInput.setRange(0.0, 2.0)
        self.temperatureInput.setSingleStep(0.1)
        self.temperatureInput.setValue(self.settings.get('temperature', 1.0))
        layout.addRow('Temperature:', self.temperatureInput)

        self.topPInput = QDoubleSpinBox(self)
        self.topPInput.setRange(0.0, 1.0)
        self.topPInput.setSingleStep(0.01)
        self.topPInput.setValue(self.settings.get('top_p', 0.95))
        layout.addRow('Top P:', self.topPInput)

        self.topKInput = QSpinBox(self)
        self.topKInput.setRange(0, 1000)
        self.topKInput.setValue(self.settings.get('top_k', 64))
        layout.addRow('Top K:', self.topKInput)

        self.maxTokensInput = QSpinBox(self)
        self.maxTokensInput.setRange(1, 10000)
        self.maxTokensInput.setValue(self.settings.get('max_output_tokens', 8192))
        layout.addRow('Max Output Tokens:', self.maxTokensInput)

        self.mimeTypeInput = QLineEdit(self)
        self.mimeTypeInput.setText(self.settings.get('response_mime_type', 'text/plain'))
        layout.addRow('Response MIME Type:', self.mimeTypeInput)

        # Input field for custom prompt
        self.promptInput = QTextEdit(self)
        self.promptInput.setText(self.settings.get('prompt', 'What is in the image?\n'))
        layout.addRow('Custom Prompt:', self.promptInput)

        # OK and Cancel buttons
        self.okButton = QPushButton('OK', self)
        self.okButton.clicked.connect(self.accept)
        layout.addWidget(self.okButton)

        self.setLayout(layout)

    def getSettings(self):
        return {
            'screenWidth': self.screenWidthInput.value(),
            'screenHeight': self.screenHeightInput.value(),
            'apiKey': self.apiKeyInput.text(),
            'windowX': self.windowXInput.value(),
            'windowY': self.windowYInput.value(),
            'windowWidth': self.windowWidthInput.value(),
            'windowHeight': self.windowHeightInput.value(),
            'temperature': self.temperatureInput.value(),
            'top_p': self.topPInput.value(),
            'top_k': self.topKInput.value(),
            'max_output_tokens': self.maxTokensInput.value(),
            'response_mime_type': self.mimeTypeInput.text(),
            'prompt': self.promptInput.toPlainText(),
        }
