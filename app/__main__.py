import atexit
import os
import subprocess
import sys

from PyQt6.QtCore import QSize, Qt, QTemporaryDir
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)
from tda import auth

window_title = "Gerador de Token para API da TD Ameritrade"

def open_file_explorer(file_path: str):
    # Verifica se o arquivo existe
    if os.path.exists(file_path):
        if sys.platform == 'win32':
            # Windows: abre a pasta e seleciona o arquivo
            subprocess.run(f'explorer /select,"{file_path}"', shell=True)
        elif sys.platform == 'darwin':
            # macOS: apenas abre a pasta, não seleciona o arquivo
            subprocess.run(['open', os.path.dirname(file_path)])
        else:
            # Linux e outros Unix-like: apenas abre a pasta, não seleciona o arquivo
            subprocess.run(['xdg-open', os.path.dirname(file_path)])
    else:
        print(f"O arquivo '{file_path}' não existe.")

def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle(window_title)
        self.setFixedSize(QSize(600, 400))

        # Layout principal
        layout = QVBoxLayout()

        # Instruções
        info_label = QLabel('''
            <style>
                li { margin-bottom: 30px; }
            </style>
            <ol>
                <li>Acesse <a href="https://developer.tdameritrade.com/user/me/apps">https://developer.tdameritrade.com/user/me/apps</a> e faça login com sua conta TD Ameritrade.</li>
                <li>Crie um app.
                    <table border="1" cellspacing="0" cellpadding="5">
                        <tr><th align="left">App Name</th><td>App</td></tr>
                        <tr><th align="left">Callback URL</th><td>http://localhost/auth</td></tr>
                        <tr><th align="left">What is the purpose of your application?</th><td>Managing account and trading.</td></tr>
                        <tr><th align="left">Order Limit</th><td>120</td></tr>
                    </table>
                </li>
            </ol>''')
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        # Rótulo para o campo Consumer Key
        self.label_consumer_key = QLabel("Consumer Key:")
        self.label_consumer_key.setFixedHeight(20)
        layout.addWidget(self.label_consumer_key)

        # Campo de entrada para Consumer Key
        self.consumer_key_input = QLineEdit()
        self.consumer_key_input.setPlaceholderText("Digite a Consumer Key aqui")
        layout.addWidget(self.consumer_key_input)

        # Botão para gerar token
        self.generate_token_button = QPushButton("Gerar Token")
        self.generate_token_button.clicked.connect(self.generate_token)
        layout.addWidget(self.generate_token_button)

        # Configura o widget central com o layout
        central_widget = QWidget()
        central_widget.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def generate_token(self):
        consumer_key = self.consumer_key_input.text()
        if len(consumer_key) == 32:
            print(f"Consumer Key: {consumer_key}")
            self.setWindowTitle("Gerando token...")
            self.centralWidget().setEnabled(False)

            # Cria um diretório temporário
            temp_dir = QTemporaryDir()
            if temp_dir.isValid():
                token_path = os.path.join(temp_dir.path(), "tda-api-token.json")
                auth.easy_client(
                    api_key=f"{consumer_key}@AMER.OAUTHAP",
                    redirect_uri="http://localhost/auth",
                    token_path=token_path,
                    webdriver_func=make_webdriver,
                )

                # Pergunta ao usuário onde salvar o arquivo
                save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Token", "tda-api-token.json", "JSON Files (*.json)")
                if save_path:
                    # Copia o arquivo para o local escolhido
                    os.replace(token_path, save_path)

                    msg = QMessageBox()
                    msg.setWindowTitle("Sucesso")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText(f'O token foi salvo em {save_path}')
                    msg.exec()

                    self.consumer_key_input.clear()

                    self.centralWidget().setEnabled(True)
                    self.setWindowTitle(window_title)

                    open_file_explorer(save_path)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Erro")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText('Falha ao criar pasta temporária.')
                msg.exec()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Atenção")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText('A consumer key deve ter 32 caracteres.')
            msg.setInformativeText('Exemplo: L6UMARTJYFQ253MHG6WGD7S6XZ797RD6')
            msg.exec()

if __name__ == '__main__':
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
