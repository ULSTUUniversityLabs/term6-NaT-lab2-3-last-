import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QWidget,
                             QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QTableWidgetItem, QTableWidget,
                             QDialog, QFormLayout)
from src.CommandThread import CommandThread


class InputDialog(QDialog):
    """Диалоговое окно для ввода IP и MAC адреса"""

    def __init__(self, title, is_add=True):
        super().__init__()
        self.setWindowTitle(title)
        self.is_add = is_add
        self.ip_input = QLineEdit()
        self.mac_input = QLineEdit() if is_add else None

        layout = QFormLayout()
        layout.addRow("IP-адрес:", self.ip_input)
        if is_add:
            layout.addRow("MAC-адрес:", self.mac_input)

        self.submit_button = QPushButton("Добавить" if is_add else "Удалить")
        self.submit_button.clicked.connect(self.submit)

        layout.addRow(self.submit_button)
        self.setLayout(layout)

    def submit(self):
        """Обработка ввода и закрытие диалога"""
        self.accept()

    def get_data(self):
        """Возвращает введенные данные"""
        return self.ip_input.text(), (self.mac_input.text() if self.is_add else None)


class ArpTab(QWidget):
    """Даёт просматривать и изменять ARP-таблицу, в которой хранятся пары МАС-адрес - IP-адрес
    для тех узлов, с которыми в недавнем происходил обмен данными"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_thread = None

    def setup_ui(self):
        layout = QVBoxLayout()

        self.arp_params = QLineEdit()
        self.arp_params.setPlaceholderText("Введите параметры для arp (например, -a)")
        self.arp_button = QPushButton("ARP")
        self.arp_button.clicked.connect(self.perform_arp)

        self.arp_table = QTableWidget()
        self.arp_table.setColumnCount(3)
        self.arp_table.setHorizontalHeaderLabels(["Адрес в Интернете", "Физический адрес", "Тип"])
        self.arp_table.setEditTriggers(QTableWidget.DoubleClicked)

        self.arp_output = QTextEdit()
        self.arp_output.setReadOnly(True)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.show_add_dialog)
        self.remove_button = QPushButton("Удалить")
        self.remove_button.clicked.connect(self.show_remove_dialog)

        self.visualize_button = QPushButton("Визуализировать структуру сети")
        self.visualize_button.clicked.connect(self.visualize_network)

        layout.addWidget(QLabel("Параметры ARP:"))
        layout.addWidget(self.arp_params)
        layout.addWidget(self.arp_button)
        layout.addWidget(self.arp_table)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.visualize_button)
        layout.addWidget(QLabel("Полный вывод ARP:"))
        layout.addWidget(self.arp_output)

        self.setLayout(layout)

    def perform_arp(self):
        self.arp_table.clearContents()
        self.arp_table.setRowCount(0)
        self.arp_output.clear()
        params = self.arp_params.text().strip() or "-a"
        command = ["arp"] + params.split()
        self.start_command_thread(command)

    def start_command_thread(self, command):
        """Запускает команду в отдельном потоке"""
        if self.command_thread is not None and self.command_thread.isRunning():
            self.stop_command()

        self.command_thread = CommandThread(command)
        self.command_thread.output_signal.connect(self.handle_output)
        self.command_thread.finished_signal.connect(lambda: self.arp_output.append("Команда завершена."))
        self.command_thread.start()

    def handle_output(self, output):
        """Обрабатывает вывод"""
        self.arp_output.append(output)

        lines = output.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("Интерфейс:"):
                parts = line.split()
                internet_address = ""
                physical_address = ""
                entry_type = ""

                if len(parts) > 0 and self.is_ip_address(parts[0]):
                    internet_address = parts[0]

                if len(parts) > 1 and self.is_mac_address(parts[1]):
                    physical_address = parts[1]

                if len(parts) > 2:
                    entry_type = parts[2]

                if len(parts) > 1 and not self.is_mac_address(parts[1]):
                    entry_type = parts[1]

                if internet_address or physical_address:
                    self.add_table_row(internet_address, physical_address, entry_type)

    def is_ip_address(self, address):
        """Проверяет, является ли адрес IP-адресом (только числа)"""
        return all(part.isdigit() for part in address.split('.')) if '.' in address else False

    def is_mac_address(self, address):
        """Проверяет, является ли адрес MAC-адресом (состоящий из чисел и букв)"""
        return all(c in "0123456789abcdefABCDEF:-" for c in address)

    def add_table_row(self, internet_address, physical_address, entry_type):
        """Добавляет строку в таблицу"""
        row_position = self.arp_table.rowCount()
        self.arp_table.insertRow(row_position)
        self.arp_table.setItem(row_position, 0, QTableWidgetItem(internet_address or ""))
        self.arp_table.setItem(row_position, 1, QTableWidgetItem(physical_address or ""))
        self.arp_table.setItem(row_position, 2, QTableWidgetItem(entry_type or ""))

    def show_add_dialog(self):
        """Показывает диалоговое окно для добавления новой записи"""
        dialog = InputDialog("Добавить запись", is_add=True)
        if dialog.exec_() == QDialog.Accepted:
            ip, mac = dialog.get_data()
            if ip and mac:
                command = f"arp -S {ip} {mac}"
                self.start_command_thread(command.split())
                self.add_table_row(ip, mac, "Динамический")

    def show_remove_dialog(self):
        """Показывает диалоговое окно для удаления записи"""
        dialog = InputDialog("Удалить запись", is_add=False)
        if dialog.exec_() == QDialog.Accepted:
            ip, _ = dialog.get_data()
            if ip:
                command = f"arp -d {ip}"
                self.start_command_thread(command.split())
                self.remove_row_by_ip(ip)

    def remove_row_by_ip(self, ip):
        """Удаляет строку по IP-адресу"""
        for row in range(self.arp_table.rowCount()):
            if self.arp_table.item(row, 0).text() == ip:
                self.arp_table.removeRow(row)
                break

    def visualize_network(self):
        """Визуализирует структуру сети на основе данных ARP"""
        G = nx.Graph()

        for row in range(self.arp_table.rowCount()):
            internet_address = self.arp_table.item(row, 0).text()
            physical_address = self.arp_table.item(row, 1).text()
            if internet_address and physical_address:
                G.add_node(internet_address)
                G.add_node(physical_address)
                G.add_edge(internet_address, physical_address)

        pos = nx.spring_layout(G, k=0.5, iterations=50)
        plt.figure(figsize=(10, 6))
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold',
                edge_color='gray')
        plt.title("Структура сети")
        plt.show()

    def stop_command(self):
        """Останавливает выполнение команды"""
        if self.command_thread is not None:
            self.command_thread.stop()
            self.command_thread.wait()
            self.command_thread = None
