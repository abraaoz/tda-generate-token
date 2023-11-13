import atexit
import os
import subprocess
import sys

from PyQt6.QtCore import QSize, Qt, QTemporaryDir
from PyQt6.QtWidgets import (QApplication, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)
from tda import auth

window_title = "TD Ameritrade API Token Generator"

def open_file_explorer(file_path: str):
    # Check if the file exists
    if os.path.exists(file_path):
        if sys.platform == 'win32':
            # Windows: open the folder and select the file
            subprocess.run(f'explorer /select,"{file_path}"', shell=True)
        elif sys.platform == 'darwin':
            # macOS: just opens the folder, does not select the file
            subprocess.run(['open', os.path.dirname(file_path)])
        else:
            # Linux and other Unix-like: just opens the folder, does not select the file
            subprocess.run(['xdg-open', os.path.dirname(file_path)])
    else:
        print(f"The file '{file_path}' does not exist.")

def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(window_title)
        self.setFixedSize(QSize(600, 400))

        # Main layout
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel('''
            <style>
                li { margin-bottom: 20px; }
                a { color: blue; }
            </style>
            <ol>
                <li>Go to <a href="https://developer.tdameritrade.com/user/me/apps">https://developer.tdameritrade.com/user/me/apps</a> and log in with your TD Ameritrade account.</li>
                <li>Create an app.
                    <table border="1" cellspacing="0" cellpadding="5">
                        <tr><th align="left">App Name</th><td>App</td></tr>
                        <tr><th align="left">Callback URL</th><td>http://localhost/auth</td></tr>
                        <tr><th align="left">What is the purpose of your application?</th><td>Managing account and trading.</td></tr>
                        <tr><th align="left">Order Limit</th><td>120</td></tr>
                    </table>
                </li>
            </ol>
            <br><br>
            <small>Developed by <a href="https://github.com/abraaoz">abraaoz</a></small>
        ''')
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        # Label for the Consumer Key field
        self.label_consumer_key = QLabel("Consumer Key:")
        self.label_consumer_key.setFixedHeight(20)
        layout.addWidget(self.label_consumer_key)

        # Input field for Consumer Key
        self.consumer_key_input = QLineEdit()
        self.consumer_key_input.setPlaceholderText("Enter the Consumer Key here")
        layout.addWidget(self.consumer_key_input)

        # Button to generate token
        self.generate_token_button = QPushButton("Generate Token")
        self.generate_token_button.clicked.connect(self.generate_token)
        layout.addWidget(self.generate_token_button)

        # Set the central widget with the layout
        central_widget = QWidget()
        central_widget.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def generate_token(self):
        consumer_key = self.consumer_key_input.text()
        if len(consumer_key) == 32:
            print(f"Consumer Key: {consumer_key}")
            self.setWindowTitle("Generating token...")
            self.centralWidget().setEnabled(False)

            # Create a temporary directory
            temp_dir = QTemporaryDir()
            if temp_dir.isValid():
                token_path = os.path.join(temp_dir.path(), "tda-api-token.json")
                auth.easy_client(
                    api_key=f"{consumer_key}@AMER.OAUTHAP",
                    redirect_uri="http://localhost/auth",
                    token_path=token_path,
                    webdriver_func=make_webdriver,
                )

                # Ask the user where to save the file
                save_path, _ = QFileDialog.getSaveFileName(self, "Save Token", "tda-api-token.json", "JSON Files (*.json)")
                if save_path:
                    # Copy the file to the chosen location
                    os.replace(token_path, save_path)

                    msg = QMessageBox()
                    msg.setWindowTitle("Success")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText(f'The token has been saved at {save_path}')
                    msg.exec()

                    self.consumer_key_input.clear()

                    self.centralWidget().setEnabled(True)
                    self.setWindowTitle(window_title)

                    open_file_explorer(save_path)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText('Failed to create a temporary folder.')
                msg.exec()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Attention")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText('The consumer key must have 32 characters.')
            msg.setInformativeText('Example: L6UMARTJYFQ253MHG6WGD7S6XZ797RD6')
            msg.exec()

if __name__ == '__main__':
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
