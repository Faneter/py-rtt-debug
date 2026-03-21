import sys
import socket
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import pyqtgraph as pg


class UDPReceiver(QThread):
    """独立线程接收 UDP 数据，防止界面卡死"""
    data_signal = pyqtSignal(dict)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 9999))
        while True:
            try:
                data, _ = sock.recvfrom(4096)
                self.data_signal.emit(json.loads(data.decode()))
            except:
                pass


class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTT Real-time Waveform")
        self.resize(800, 500)

        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.curves = {}
        self.data_history = {}

        self.receiver = UDPReceiver()
        self.receiver.data_signal.connect(self.update_plot)
        self.receiver.start()

    def update_plot(self, data_dict):
        for tid, val in data_dict.items():
            if tid not in self.curves:
                self.curves[tid] = self.plot_widget.plot(pen=pg.mkPen(len(self.curves)), name=f"ID:{tid}")
                self.data_history[tid] = []

            self.data_history[tid].append(val)
            if len(self.data_history[tid]) > 1000:
                self.data_history[tid].pop(0)

            self.curves[tid].setData(self.data_history[tid])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PlotWindow()
    win.show()
    sys.exit(app.exec_())
