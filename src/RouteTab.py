import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from src.CommandThread import CommandThread  # Предполагается, что CommandThread уже реализован аналогично примеру
import pygame
import sys
import networkx as nx

class RouteTab(QWidget):
    """Виджет для отображения и управления таблицей маршрутов"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_thread = None
        self.G = nx.DiGraph()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.command_text = ""
        self.route_output = QTextEdit()
        self.route_output.setReadOnly(True)

        self.route_table = QTableWidget(0, 5)
        self.route_table.setHorizontalHeaderLabels(["Сеть назначения", "Маска", "Шлюз", "Интерфейс", "Метрика"])
        self.route_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.view_button = QPushButton("Показать маршруты")
        self.view_button.clicked.connect(self.view_routes)

        self.add_button = QPushButton("Добавить маршрут")
        self.add_button.clicked.connect(self.add_route)

        self.modify_button = QPushButton("Изменить маршрут")
        self.modify_button.clicked.connect(self.modify_route)

        self.delete_button = QPushButton("Удалить маршрут")
        self.delete_button.clicked.connect(self.delete_route)

        # Поля для ввода параметров
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Сеть назначения (например, 192.168.1.0)")
        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("Маска (например, 255.255.255.0)")
        self.gateway_input = QLineEdit()
        self.gateway_input.setPlaceholderText("Шлюз (например, 192.168.1.1)")
        self.metric_input = QLineEdit()
        self.metric_input.setPlaceholderText("Метрика (например, 1)")

        layout.addWidget(QLabel("Текущие маршруты:"))
        layout.addWidget(self.route_output)
        layout.addWidget(self.route_table)
        layout.addWidget(self.view_button)
        layout.addWidget(QLabel("Добавить/Изменить маршрут:"))
        layout.addWidget(self.destination_input)
        layout.addWidget(self.mask_input)
        layout.addWidget(self.gateway_input)
        layout.addWidget(self.metric_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.modify_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def view_routes(self):
        """Отображает текущие маршруты"""
        self.route_output.clear()
        command = ["route", "print"]
        self.start_command_thread(command)

    def add_route(self):
        """Добавляет маршрут"""
        command = [
            "route", "add", self.destination_input.text(),
            "MASK", self.mask_input.text(), self.gateway_input.text(),
            "METRIC", self.metric_input.text(), 
            #"IF", self.interface_input.text()
        ]
        self.start_command_thread(command)

    def modify_route(self):
        """Изменяет существующий маршрут"""
        command = [
            "route", "change", self.destination_input.text(),
            "mask", self.mask_input.text(), self.gateway_input.text(),
            "metric", self.metric_input.text()
        ]
        self.start_command_thread(command)

    def delete_route(self):
        """Удаляет маршрут"""
        command = ["route", "delete", self.destination_input.text()]
        self.start_command_thread(command)

    def start_command_thread(self, command):
        self.command_text = ""
        self.route_output.setText(self.command_text)

        """Запускает команду в отдельном потоке"""
        if self.command_thread is not None and self.command_thread.isRunning():
            self.stop_command()

        self.command_thread = CommandThread(command)
        self.command_thread.output_signal.connect(self.handle_output)
        self.command_thread.finished_signal.connect(lambda: self.finished_signal())
        self.command_thread.start()

    def handle_output(self, output):
        """Обрабатывает вывод команды"""
        self.command_text += output

    def parse_route_output(self, output):
        """Парсит и заполняет таблицу маршрутов"""
        self.route_table.setRowCount(0)
        self.G.clear()  

        for line in output.splitlines():
            match = re.match(r'\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\S+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)', line)
            if match:
                destination, mask, gateway, interface, metric = match.groups()
                row_position = self.route_table.rowCount()
                self.route_table.insertRow(row_position)
                self.route_table.setItem(row_position, 0, QTableWidgetItem(destination))
                self.route_table.setItem(row_position, 1, QTableWidgetItem(mask))
                self.route_table.setItem(row_position, 2, QTableWidgetItem(gateway))
                self.route_table.setItem(row_position, 3, QTableWidgetItem(interface))
                self.route_table.setItem(row_position, 4, QTableWidgetItem(metric))

                self.G.add_node(destination)
                self.G.add_node(gateway)
                self.G.add_edge(gateway, destination, label=f"Metric: {metric}")

        self.display_graph()

    def display_graph(self):
        """Создает окно PyGame для визуализации графа"""
        pygame.init()
        sx, sy = 800, 600
        ox = sx / 2
        oy = sy / 2
        k = 0.8
        screen = pygame.display.set_mode((sx, sy))
        pygame.display.set_caption("Network Routes Graph")

        pos = nx.spring_layout(self.G, seed=42)  # Позиции узлов
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((46, 46, 46))

            # Отображение ребер
            for edge in self.G.edges(data=True):
                src, dest, label = edge
                pygame.draw.line(screen, (200, 200, 200), 
                                 (int(pos[src][0] * (sx/2)*k + sx/2), int(pos[src][1] * (sy/2)*k + (sy/2))),
                                 (int(pos[dest][0] * (sx/2)*k + sx/2), int(pos[dest][1] * (sy/2)*k + (sy/2))), 2)

            # Отображение узлов и меток
            for node, (x, y) in pos.items():
                pygame.draw.circle(screen, (0, 183, 255), (int(x * (sx/2)*k + (sx/2)), int(y * (sy/2)*k + (sy/2))), 20)
                font = pygame.font.Font(None, 24)
                text = font.render(node, True, (255, 255, 255))
                screen.blit(text, (int(x * (sx/2)*k + (sx/2)), int(y * (sy/2)*k + (sy/2))))

            pygame.display.flip()

        pygame.quit()

    def finished_signal(self):
        self.command_text += "Команда завершена."
        self.route_output.append(self.command_text)

        # Обновляем таблицу маршрутов после просмотра командой route print
        if "route print" in ' '.join(self.command_thread.command):
            self.parse_route_output(self.command_text)

        self.command_text = ""
        self.command_thread = None

    def stop_command(self):
        """Останавливает выполнение команды"""
        if self.command_thread is not None:
            self.command_thread.stop()
            self.command_thread.wait()
            self.command_thread = None
