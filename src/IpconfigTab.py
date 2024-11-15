import re
from PyQt5.QtWidgets import (QTabWidget, QWidget,
                             QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel)

from src.CommandThread import CommandThread


class IpconfigTab(QWidget):
    """Отображает и настраивает настройки протоколов TCP/IP"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_thread = None
        self.output_buffer = []

    def setup_ui(self):
        layout = QVBoxLayout()

        self.ipconfig_params = QLineEdit()
        self.ipconfig_params.setPlaceholderText("Введите параметры для ipconfig (например, /all)")
        self.ipconfig_output = QTextEdit()
        self.ipconfig_output.setReadOnly(True)
        self.ipconfig_button = QPushButton("Ipconfig")
        self.ipconfig_button.clicked.connect(self.perform_ipconfig)

        layout.addWidget(QLabel("Параметры Ipconfig:"))
        layout.addWidget(self.ipconfig_params)
        layout.addWidget(self.ipconfig_button)
        layout.addWidget(self.ipconfig_output)

        self.interface_tabs = QTabWidget()
        layout.addWidget(self.interface_tabs)

        self.setLayout(layout)

    def perform_ipconfig(self):
        self.ipconfig_output.clear()
        self.output_buffer.clear()
        self.interface_tabs.clear()
        params = self.ipconfig_params.text().strip() or "/all"
        command = ["ipconfig"] + params.split()
        self.start_command_thread(command)

    def start_command_thread(self, command):
        """Запускает команду в отдельном потоке"""
        if self.command_thread is not None and self.command_thread.isRunning():
            self.stop_command()

        self.command_thread = CommandThread(command)
        self.command_thread.output_signal.connect(self.handle_output)
        self.command_thread.finished_signal.connect(self.process_output)
        self.command_thread.start()

    def handle_output(self, output):
        """Обрабатывает вывод, добавляет в буфер"""
        self.ipconfig_output.append(output)
        self.output_buffer.append(output)

    def process_output(self):
        """Обрабатывает вывод после завершения команды"""
        for line in self.output_buffer:
            if "адаптер" in line.lower():
                adapter_name = re.search(r'адаптер (.*?):', line, re.IGNORECASE)
                if adapter_name:
                    tab_name = adapter_name.group(1).strip()
                    content_widget = QTextEdit()
                    content_widget.setReadOnly(True)

                    adapter_content = [line]
                    for next_line in self.output_buffer[self.output_buffer.index(line)+1:]:
                        if "адаптер" in next_line.lower():
                            break
                        adapter_content.append(next_line)

                    content_widget.setPlainText("\n".join(adapter_content))
                    self.interface_tabs.addTab(content_widget, tab_name)

        self.ipconfig_output.append("Команда завершена.")

    def stop_command(self):
        """Останавливает выполнение команды"""
        if self.command_thread is not None:
            self.command_thread.stop()
            self.command_thread.wait()
            self.command_thread = None
