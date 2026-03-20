import pylink
import struct
import threading
import time

# 协议常量
FRAME_HEAD1 = 0x5A
FRAME_HEAD2 = 0xA5
CMD_MONITOR = 0x01
CMD_MAPPING = 0x02
CMD_REQ_MAP = 0x03
CMD_SET_VAL = 0x04


class RMDebugger:
    def __init__(self, chip="STM32F103C8"):
        self.jlink = pylink.JLink()
        self.jlink.open()
        self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.jlink.connect(chip)
        self.jlink.rtt_start()

        self.param_map = {}  # ID -> {name, is_monitor}
        self.monitor_ids = []  # 缓存需要监控的 ID 顺序
        self.running = True

    def send_packet(self, cmd, payload=None):
        """ 封装并发送协议包 """
        if payload is None: payload = []
        full_pkg = [FRAME_HEAD1, FRAME_HEAD2, cmd, len(payload)] + list(payload)
        # 计算校验和 (CMD + Len + Payload)
        check_sum = sum(full_pkg[2:]) & 0xFF
        full_pkg.append(check_sum)
        self.jlink.rtt_write(0, full_pkg)

    def receive_thread(self):
        """ 异步接收线程：处理 MCU 发来的所有数据 """
        buffer = bytearray()
        while self.running:
            data = self.jlink.rtt_read(0, 1024)
            if data:
                buffer.extend(data)

                # 状态机解析缓冲区
                while len(buffer) >= 5:
                    if buffer[0] == FRAME_HEAD1 and buffer[1] == FRAME_HEAD2:
                        cmd = buffer[2]
                        length = buffer[3]
                        if len(buffer) < 5 + length: break  # 数据还没收全

                        payload = buffer[4: 4 + length]
                        checksum = buffer[4 + length]

                        # 验证校验和
                        if (sum(buffer[2: 4 + length]) & 0xFF) == checksum:
                            self.handle_payload(cmd, payload)

                        del buffer[: 5 + length]  # 弹出已处理的包
                    else:
                        del buffer[0]  # 找错帧头了，删掉第一个字节继续找
            time.sleep(0.01)

    def handle_payload(self, cmd, payload):
        if cmd == CMD_MONITOR:
            # 高速数据解析 (假设全部为 float)
            num_floats = len(payload) // 4
            values = struct.unpack(f"<{num_floats}f", payload)
            # 简易打印（在实际应用中，这里应喂给绘图器）
            # print(f"\r[MONITOR] {dict(zip(self.monitor_ids, values))}", end="")
            pass

        elif cmd == CMD_MAPPING:
            # 解析映射条目: [ID(1B)][Type(1B)][Name(String)]
            p_id = payload[0]
            p_type = payload[1]
            p_name = payload[2:].decode('utf-8').strip('\x00')
            self.param_map[p_id] = {"name": p_name, "is_monitor": True}  # 简化逻辑
            print(f"\n[MAP] 已同步: ID {p_id} -> {p_name}")
            # 更新监控顺序（按 ID 升序）
            self.monitor_ids = sorted(self.param_map.keys())

    def run_cli(self):
        """ 终端交互逻辑 """
        print("--- RoboMaster 终端调参器 ---")
        print("输入 'sync' 同步参数表, 'set [ID] [Val]' 修改参数, 'exit' 退出")

        threading.Thread(target=self.receive_thread, daemon=True).start()

        while self.running:
            user_input = input("\n> ").strip().split()
            if not user_input: continue

            cmd = user_input[0].lower()
            if cmd == "sync":
                print("正在请求参数映射表...")
                self.send_packet(CMD_REQ_MAP)
            elif cmd == "set" and len(user_input) == 3:
                p_id = int(user_input[1])
                p_val = float(user_input[2])
                # 打包 [ID(1B)][Value(4B float)]
                payload = struct.pack("<Bf", p_id, p_val)
                self.send_packet(CMD_SET_VAL, payload)
                print(f"已下发修改指令: ID {p_id} = {p_val}")
            elif cmd == "exit":
                self.running = False
                self.jlink.rtt_stop()
                self.jlink.close()


if __name__ == "__main__":
    dbg = RMDebugger()
    dbg.run_cli()
