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
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许多个窗口监听同一个UDP端口
        sock.bind(("127.0.0.1", 9999))
        while True:
            try:
                data, _ = sock.recvfrom(4096)
                self.data_signal.emit(json.loads(data.decode()))
            except:
                pass


class PlotWindow(QMainWindow):
    def __init__(self, target_ids):
        super().__init__()
        self.target_ids = target_ids
        self.setWindowTitle(f"RTT Real-time Waveform - IDs: {target_ids}")
        self.resize(800, 600)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addLegend(offset=(30, 30))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.setCentralWidget(self.plot_widget)

        self.curves = {}
        self.data_history = {tid: [] for tid in self.target_ids}

        self.receiver = UDPReceiver()
        self.receiver.data_signal.connect(self.update_plot)
        self.receiver.start()

    def update_plot(self, data_dict):
        for i, tid in enumerate(self.target_ids):
            if tid in data_dict:
                item = data_dict[tid]
                val = item['val']
                name = item['name']

                if tid not in self.curves:
                    pen = pg.mkPen(color=pg.intColor(i, hues=len(self.target_ids)), width=2)
                    lable_name = f"{name} (ID:{tid})"
                    self.curves[tid] = self.plot_widget.plot(pen=pen, name=lable_name)

                self.data_history[tid].append(val)
                if len(self.data_history[tid]) > 1000:
                    self.data_history[tid].pop(0)
                self.curves[tid].setData(self.data_history[tid])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    target_ids = sys.argv[1:]
    if not target_ids:
        print("\n[ERROR] 未指定观测ID")
        sys.exit(1)
    win = PlotWindow(target_ids)
    win.show()
    sys.exit(app.exec_())
