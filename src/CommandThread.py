import subprocess
from PyQt5.QtCore import QThread, pyqtSignal


class CommandThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command
        self._is_running = True

    def run(self):
        """Выполняет команду и передает вывод через сигнал"""
        try:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, text=True, encoding='cp866')
            for line in process.stdout:
                if not self._is_running:
                    process.terminate()
                    break
                self.output_signal.emit(line)
            process.stdout.close()
            process.wait()
        except Exception as e:
            self.output_signal.emit(f"Ошибка: {e}")
        finally:
            self.finished_signal.emit()

    def stop(self):
        """Останавливает выполнение потока"""
        self._is_running = False