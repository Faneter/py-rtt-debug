import os.path
import subprocess
import sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Log, Input, Static
from textual.containers import Horizontal, Vertical, Container
from textual import work
from textual.binding import Binding

from collector import Collector


def get_resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和Pyinstaller打包环境"""
    if getattr(sys, "frozen", False):
        # Pyinstaller 打包后的临时目录路径
        base_path = sys._MEIPASS
    else:
        # 正常开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class RTTTerminalApp(App):
    """RTT 调试终端主界面"""

    CSS_PATH = get_resource_path("style.tcss")
    BINDINGS = [
        Binding("f1", "sync", "Sync (REQ_MAP)", show=True),
        Binding("f2", "clear_logs", "Clear Logs", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="body"):
            # 左侧：参数列表
            with Vertical(id="param_pane"):
                yield Static("Param List", classes="pane-title")
                yield DataTable(id="param_list")

            # 中间：Dashboard + 调试日志 + 输入
            with Vertical(id="center_pane"):
                yield Static("Dashboard (Live Monitors)", id="dashboard_view")
                yield Log(id="dbg_log", auto_scroll=True)
                yield Input(
                    placeholder="Enter command (e.g. set 1 45.2)", id="cmd_input"
                )

            # 右侧：MCU 日志
            with Vertical(id="log_pane"):
                yield Static("MCU Log View", classes="pane-title")
                yield Log(id="mcu_log", auto_scroll=True)

        yield Footer()

    def on_mount(self) -> None:
        """初始化界面和后台任务"""
        # 初始化表格
        table = self.query_one("#param_list", DataTable)
        table.add_column("ID", key="id")
        table.add_column("Name", key="name")
        table.add_column("Value", key="val")
        table.cursor_type = "row"

        # 1. 实例化 Collector
        self.collector = Collector()

        # 2. 启动后台 RTT 接收 Worker
        self.run_rtt_receiver()

        # 3. 设置定时器：每 50ms 从队列检查一次新数据并更新 UI
        self.set_interval(0.05, self.update_ui_from_queue)

    def debug_log(self, log: str):
        self.query_one("#dbg_log").write_line(log)

    @work(exclusive=True, thread=True)
    def run_rtt_receiver(self):
        """在独立线程中运行 RTT 接收循环"""
        self.collector.receive_loop()

    def update_ui_from_queue(self):
        """非阻塞地处理采集器发来的消息"""
        while True:
            msg = self.collector.poll()
            if not msg:
                break

            msg_type = msg["type"]
            content = msg["content"]

            if msg_type == "mapping":
                self.refresh_param_table(content)

            elif msg_type == "data":
                self.update_param_values(content)

            elif msg_type == "dbg_log":
                self.debug_log(content)

            elif msg_type == "mcu_log":
                # 这里目前暂不处理具体内容，直接打印
                self.query_one("#mcu_log").write_line(content)

    def refresh_param_table(self, mapping):
        """收到新的映射表时清空重绘表格"""
        table = self.query_one("#param_list", DataTable)
        table.clear()
        for p_id, info in mapping.items():
            # ID, 名称, 当前值
            table.add_row(str(p_id), info["name"], str(info["val"]), key=str(p_id))

    def update_param_values(self, data):
        """更新已存在的表格行数据"""
        table = self.query_one("#param_list", DataTable)
        for p_id, info in data.items():
            try:
                # 动态更新 ID 对应行的 "Value" 列
                table.update_cell(
                    row_key=str(p_id), column_key="val", value=str(info["val"])
                )
            except:
                pass

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入框指令"""
        cmd_text = event.value.strip().split()
        if not cmd_text:
            return

        op = cmd_text[0].lower()
        if op == "set" and len(cmd_text) == 3:
            p_id, val = int(cmd_text[1]), float(cmd_text[2])
            self.collector.send_set_cmd(p_id, val)
        elif op == "sync":
            self.collector.send_packet(0x03)  # CMD_REQ_MAP
        elif op == "plot":
            if len(cmd_text) < 2:
                self.debug_log("\n[WARN] 输入格式错误")
            else:
                target_ids = cmd_text[1:]
                try:
                    target_ids = [
                        tid
                        for tid in target_ids
                        if int(tid) in self.collector.monitor_ids
                    ]
                    self.debug_log(f"\n[INFO] 正在唤起 ID {target_ids} 的波形窗口")
                    if getattr(sys, "frozen", False):
                        exe_path = os.path.join(
                            os.path.dirname(sys.executable), "display.exe"
                        )
                        subprocess.Popen([exe_path] + target_ids)
                    else:
                        subprocess.Popen([sys.executable, "display.py"] + target_ids)
                except Exception as e:
                    self.debug_log(f"\n[ERROR] 无法启动显示进程: {e}")

        # 清空输入框
        event.input.value = ""

    def action_sync(self):
        """F1 快捷键逻辑"""
        self.collector.send_packet(0x03)
        self.debug_log("[INFO] 正在请求映射表...")

    def action_clear_logs(self):
        """F2 快捷键逻辑"""
        self.query_one("#mcu_log").clear()
        self.query_one("#dbg_log").clear()

    async def action_quit(self) -> None:
        """Ctrl + Q 退出逻辑"""
        self.debug_log("[INFO] 关闭资源中...")
        if hasattr(self, "collector"):
            self.collector.close()
        self.exit()

    def on_unmount(self) -> None:
        """当应用被卸载时，确保资源被清理"""
        if hasattr(self, "collector"):
            self.collector.close()


if __name__ == "__main__":
    app = RTTTerminalApp()
    app.run()
