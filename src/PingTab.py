import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from src.CommandThread import CommandThread
import pygame
import sys


class PingTab(QWidget):
    """Тестирует сетевое соединение путем посылки пакетов"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_thread = None
        self.G = nx.Graph()
        self.current_node = "127.0.0.1"
        self.target_node = None
        self.animation = None

    def setup_ui(self):
        layout = QVBoxLayout()

        self.ping_input = QLineEdit()
        self.ping_input.setPlaceholderText("Введите адрес для ping")
        self.ping_params = QLineEdit()
        self.ping_params.setPlaceholderText("Введите параметры (например, -n 4 -l 32)")
        self.ping_output = QTextEdit()
        self.ping_output.setReadOnly(True)
        self.ping_table = QTableWidget(0, 4)
        self.ping_table.setHorizontalHeaderLabels(["IP", "Байты", "Время", "TTL"])
        self.ping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ping_button = QPushButton("Ping")
        self.ping_button.clicked.connect(self.perform_ping)
        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_command)

        layout.addWidget(QLabel("Адрес для Ping:"))
        layout.addWidget(self.ping_input)
        layout.addWidget(QLabel("Параметры:"))
        layout.addWidget(self.ping_params)
        layout.addWidget(self.ping_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.ping_output)
        layout.addWidget(self.ping_table)

        self.setLayout(layout)

    def perform_ping(self):
        self.ping_output.clear()
        self.ping_table.setRowCount(0)
        target = self.ping_input.text() or "8.8.8.8"
        params = self.ping_params.text().strip()
        command = ["ping"] + params.split() + [target]
        self.target_node = target
        self.start_command_thread(command)
        self.visualize_packet_movement()

    def start_command_thread(self, command):
        """Запускает команду в отдельном потоке"""
        if self.command_thread is not None and self.command_thread.isRunning():
            self.stop_command()

        self.command_thread = CommandThread(command)
        self.command_thread.output_signal.connect(self.handle_output)
        self.command_thread.finished_signal.connect(lambda: self.finished_signal())
        self.command_thread.start()

    def finished_signal(self):
        self.ping_output.append("Команда завершена.")
        self.command_thread = None

    def handle_output(self, output):
        """Обрабатывает вывод и добавляет данные в таблицу"""
        self.ping_output.append(output)

        match = re.search(r"Ответ от (\d+\.\d+\.\d+\.\d+): число байт=(\d+) время[<>=](\d+мс) TTL=(\d+)", output)
        if match:
            ip, bytes_, time_, ttl = match.groups()
            row_position = self.ping_table.rowCount()
            self.ping_table.insertRow(row_position)
            self.ping_table.setItem(row_position, 0, QTableWidgetItem(ip))
            self.ping_table.setItem(row_position, 1, QTableWidgetItem(bytes_))
            self.ping_table.setItem(row_position, 2, QTableWidgetItem(time_))
            self.ping_table.setItem(row_position, 3, QTableWidgetItem(ttl))

    def visualize_packet_movement(self):
        """Визуализирует перемещение пакетов между узлами"""
        if not self.target_node:
            self.ping_output.append("Не указан целевой узел для ping.")
            return

        pygame.init()
        screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Визуализация пакета")

        # Построение графа
        self.G.clear()
        self.G.add_node(self.current_node, pos=(100, 200), label=self.current_node)
        self.G.add_node(self.target_node, pos=(500, 200), label=self.target_node)
        self.G.add_edge(self.current_node, self.target_node)

        # Координаты узлов
        pos = nx.get_node_attributes(self.G, 'pos')
        running = True
        packet_x = pos[self.current_node][0]
        target_x = pos[self.target_node][0]

        # Основной цикл анимации
        while running:
            screen.fill((46, 46, 46))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Отрисовка графа
            for edge in self.G.edges():
                pygame.draw.line(screen, (200, 200, 200), pos[edge[0]], pos[edge[1]], 3)
            for node, (x, y) in pos.items():
                pygame.draw.circle(screen, (0, 183, 255), (x, y), 35)
                font = pygame.font.SysFont(None, 24)
                text = font.render(node, True, (255, 255, 255))
                screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

            # Анимация пакета
            if packet_x < target_x:
                packet_x += 2  # Скорость перемещения пакета
            
            pygame.draw.circle(screen, (0, 255, 140), (packet_x, pos[self.current_node][1]), 10)

            pygame.display.flip()
            pygame.time.delay(20)

        pygame.quit()

    def stop_command(self):
        """Останавливает выполнение команды"""
        if self.command_thread is not None:
            self.command_thread.stop()
            self.command_thread.wait()
            self.command_thread = None
