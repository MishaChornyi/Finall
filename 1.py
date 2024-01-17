import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
import sqlite3
import requests

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.conn = sqlite3.connect('sites.db')
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS sites (url TEXT, content TEXT)')
        self.conn.commit()

        vbox = QVBoxLayout()
        self.url_edit = QLineEdit()
        self.add_button = QPushButton('Додай URL')
        self.add_button.clicked.connect(self.add_site)
        self.query_edit = QLineEdit()
        self.search_button = QPushButton('Пошук')
        self.search_button.clicked.connect(self.search)
        self.result_edit = QTextEdit()

        vbox.addWidget(self.url_edit)
        vbox.addWidget(self.add_button)
        vbox.addWidget(self.query_edit)
        vbox.addWidget(self.search_button)
        vbox.addWidget(self.result_edit)

        self.setLayout(vbox)

        self.setWindowTitle('Веб пошук')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def add_site(self):
        url = self.url_edit.text()
        try:
            res = requests.get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            self.c.execute('INSERT INTO sites (url, content) VALUES (?, ?)', (url, str(soup)))
            self.conn.commit()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while adding site: {e}")

    def search(self):
        query = self.query_edit.text()
        self.c.execute('SELECT url, content FROM sites WHERE content LIKE ?', ('%' + query + '%',))
        results = sorted([(content.count(query), url) for url, content in self.c.fetchall()], reverse=True)
        self.result_edit.setText('\n'.join(f'{url}: {count}' for count, url in results))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
