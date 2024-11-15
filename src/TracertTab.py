from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel)

from src.CommandThread import CommandThread


class TracertTab(QWidget):
    """Отображает маршрут пакетов до заданного узла и получить временные
    характеристики для каждого промежуточного маршрутизатора на этом пути"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_thread = None

    def setup_ui(self):
        layout = QVBoxLayout()

        self.tracert_input = QLineEdit()
        self.tracert_input.setPlaceholderText("Введите адрес для tracert")
        self.tracert_params = QLineEdit()
        self.tracert_params.setPlaceholderText("Введите параметры (например, -h 30)")
        self.tracert_output = QTextEdit()
        self.tracert_output.setReadOnly(True)
        self.tracert_button = QPushButton("Tracert")
        self.tracert_button.clicked.connect(self.perform_tracert)

        layout.addWidget(QLabel("Адрес для Tracert:"))
        layout.addWidget(self.tracert_input)
        layout.addWidget(QLabel("Параметры:"))
        layout.addWidget(self.tracert_params)
        layout.addWidget(self.tracert_button)
        layout.addWidget(self.tracert_output)

        self.setLayout(layout)

    def perform_tracert(self):
        self.tracert_output.clear()
        target = self.tracert_input.text() or "8.8.8.8"
        params = self.tracert_params.text().strip()
        command = ["tracert"] + params.split() + [target]
        self.start_command_thread(command)

    def start_command_thread(self, command):
        """Запускает команду в отдельном потоке"""
        if self.command_thread is not None and self.command_thread.isRunning():
            self.stop_command()

        self.command_thread = CommandThread(command)
        self.command_thread.output_signal.connect(self.handle_output)
        self.command_thread.finished_signal.connect(lambda: self.tracert_output.append("Команда завершена."))
        self.command_thread.start()

    def handle_output(self, output):
        """Обрабатывает вывод"""
        self.tracert_output.append(output)

    def stop_command(self):
        """Останавливает выполнение команды"""
        if self.command_thread is not None:
            self.command_thread.stop()
            self.command_thread.wait()
            self.command_thread = None
