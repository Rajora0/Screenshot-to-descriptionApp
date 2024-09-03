# Imports do PyQt5
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, 
    QAction, QApplication, QDialog
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QPen, QColor, QIcon
)
from PyQt5.QtCore import Qt, QRect, QPoint

# Imports de bibliotecas externas
from PIL import ImageGrab
import configparser
import os

# Imports de módulos específicos do projeto
import gemini_image_describer
from settings_dialog import SettingsDialog


class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = 'settings.ini'
        self.thumbnail_dir = './'
        self.settings = self.loadSettings()
        self.initUI()
        self.loadLastThumbnail()

    def initUI(self):
        self.setWindowTitle('Screenshot Tool')
        self.setWindowIcon(QIcon('app_icon.ico'))
        self.setGeometry(self.settings['windowX'], self.settings['windowY'],
                        self.settings['windowWidth'], self.settings['windowHeight'])
        
        self.stored_width = self.settings['windowWidth']
        self.stored_height = self.settings['windowHeight']

        # Create a menu bar
        menuBar = self.menuBar()
        settingsMenu = menuBar.addMenu('Settings')

        # Add settings action
        settingsAction = QAction('Configure...', self)
        settingsAction.triggered.connect(self.openSettings)
        settingsMenu.addAction(settingsAction)

        layout = QVBoxLayout()

        self.screenshotButton = QPushButton('Select Area and Take Screenshot', self)
        self.screenshotButton.clicked.connect(self.beginScreenshot)
        layout.addWidget(self.screenshotButton)

        # Add a QLabel to show the screenshot thumbnail
        self.thumbnailLabel = QLabel(self)
        self.thumbnailLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.thumbnailLabel)

        # Add a QLabel for displaying the message
        self.messageBox = QLabel(self)
        self.messageBox.setText('Response message will appear here')
        self.messageBox.setWordWrap(True)  # Allow text to wrap
        layout.addWidget(self.messageBox)

        # Add a QPushButton to generate random messages
        self.generateMessageButton = QPushButton('Generate Response Message', self)
        self.generateMessageButton.clicked.connect(self.generateResponseMessage)
        layout.addWidget(self.generateMessageButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.isSelecting = False
        self.originQPoint = QPoint()
        self.endQPoint = QPoint()

    def openSettings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:

            self.new_settings = dialog.getSettings()
            self.settings.update(self.new_settings)
            
            print(self.new_settings)
            
            current_geometry = self.geometry()
            current_x = current_geometry.x()
            current_y = current_geometry.y()
            
            self.setGeometry(current_x, current_y, self.settings['windowWidth'], self.settings['windowHeight'])
                
            self.saveSettings()
            print(f"Settings updated: {self.settings}")

    def beginScreenshot(self):
        self.hide()  # Hide the window to allow area selection

        self.isSelecting = True
        self.showFullScreen()

    def mousePressEvent(self, event):
        if self.isSelecting:
            self.originQPoint = event.pos()

    def mouseMoveEvent(self, event):
        if self.isSelecting:
            self.endQPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.isSelecting:
            self.endQPoint = event.pos()
            self.isSelecting = False
            self.captureSelectedArea()
            self.showNormal()
            self.update()
            

    def paintEvent(self, event):
        if self.isSelecting:
            painter = QPainter(self)
            self.setWindowOpacity(0.05) 

            # Draw a semi-transparent overlay over the entire screen
            overlayColor = QColor(0, 0, 0, 150)  # Semi-transparent black
            painter.fillRect(self.rect(), overlayColor)

            # Clear the selected area to make it fully transparent
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(QRect(self.originQPoint, self.endQPoint), Qt.transparent)

            # Draw the red border around the selected area
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(QRect(self.originQPoint, self.endQPoint))

    def captureSelectedArea(self):
        try:
            x1 = min(self.originQPoint.x(), self.endQPoint.x())
            y1 = min(self.originQPoint.y(), self.endQPoint.y())
            x2 = max(self.originQPoint.x(), self.endQPoint.x())
            y2 = max(self.originQPoint.y(), self.endQPoint.y())

            self.hide()  # Hide the window before capturing the screen

            # Ensure the capture area is within the screen bounds
            screen_rect = QApplication.primaryScreen().geometry()
            x1 = max(x1, screen_rect.left())
            y1 = max(y1, screen_rect.top())
            x2 = min(x2, screen_rect.right())
            y2 = min(y2, screen_rect.bottom())

            self.setWindowOpacity(1)

            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            # Create thumbnail
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((400, 800))  # Adjust the thumbnail size as needed

            # Save screenshot and thumbnail
            #screenshot.save('screenshot.png')
            thumbnail.save('thumbnail.png')

            self.show()  # Show the window again

            # Show the thumbnail in the UI
            pixmap = QPixmap('thumbnail.png')
            self.thumbnailLabel.setPixmap(pixmap)

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Clean up temporary files if desired
            if os.path.exists('screenshot.png'):
                os.remove('screenshot.png')
            # if os.path.exists('thumbnail.png'):
            #     os.remove('thumbnail.png')

    def generateResponseMessage(self):
        api_key = self.settings['apiKey']
        image_name = "thumbnail.png"  # Adjust as needed

        # Prepare optional parameters for describe_image
        optional_params = {
            'temperature': self.settings.get('temperature', 1.0),
            'top_p': self.settings.get('top_p', 0.95),
            'top_k': self.settings.get('top_k', 64),
            'max_output_tokens': self.settings.get('max_output_tokens', 8192),
            'response_mime_type': self.settings.get('response_mime_type', 'text/plain'),
            'prompt': self.settings.get('prompt', 'What is in the image?\n')
        }

        # Attempt to get image description using the describe_image function with optional parameters
        description = gemini_image_describer.describe_image(api_key, image_name, optional_params)

        # If description is "Image not found", select a random message
        if description == "Image not found":
            message = "Image not found"
        else:
            message = description

        # Update the QLabel with the message
        self.messageBox.setText(message)
        
    def loadLastThumbnail(self):
        
        if not os.path.exists(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir)
            
        files = [f for f in os.listdir(self.thumbnail_dir) if f.lower().endswith('.png')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.thumbnail_dir, x)), reverse=True)
        
        if files:
            latest_thumbnail = os.path.join(self.thumbnail_dir, files[0])
            pixmap = QPixmap(latest_thumbnail)
            self.thumbnailLabel.setPixmap(pixmap)


    def loadSettings(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        settings = {
            'screenWidth': 800,
            'screenHeight': 600,
            'apiKey': '',
            'windowX': 100,
            'windowY': 100,
            'windowWidth': 400,
            'windowHeight': 300,
            'temperature': 1.0,
            'top_p': 0.95,
            'top_k': 64,
            'max_output_tokens': 8192,
            'response_mime_type': 'text/plain',
            'prompt': 'What is in the image?\n'
        }
        
        if 'General' in config:
            settings.update({
                'screenWidth': config.getint('General', 'screenWidth', fallback=settings['screenWidth']),
                'screenHeight': config.getint('General', 'screenHeight', fallback=settings['screenHeight']),
                'apiKey': config.get('General', 'apiKey', fallback=settings['apiKey']),
                'windowX': config.getint('General', 'windowX', fallback=settings['windowX']),
                'windowY': config.getint('General', 'windowY', fallback=settings['windowY']),
                'windowWidth': config.getint('General', 'windowWidth', fallback=settings['windowWidth']),
                'windowHeight': config.getint('General', 'windowHeight', fallback=settings['windowHeight']),
                'temperature': config.getfloat('General', 'temperature', fallback=settings['temperature']),
                'top_p': config.getfloat('General', 'top_p', fallback=settings['top_p']),
                'top_k': config.getint('General', 'top_k', fallback=settings['top_k']),
                'max_output_tokens': config.getint('General', 'max_output_tokens', fallback=settings['max_output_tokens']),
                'response_mime_type': config.get('General', 'response_mime_type', fallback=settings['response_mime_type']),
                'prompt': config.get('General', 'prompt', fallback=settings['prompt'])
            })

        return settings


    def saveSettings(self):
        config = configparser.ConfigParser()
        config['General'] = {
            'screenWidth': str(self.settings['screenWidth']),
            'screenHeight': str(self.settings['screenHeight']),
            'apiKey': self.settings['apiKey'],
            'windowX': str(self.settings['windowX']),
            'windowY': str(self.settings['windowY']),
            'windowWidth': str(self.settings['windowWidth']),
            'windowHeight': str(self.settings['windowHeight'])
        }
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)
