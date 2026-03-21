import pylink
import struct
import threading
import time

# 协议常量
FRAME_HEAD1, FRAME_HEAD2 = 0x5A, 0xA5
CMD_MONITOR, CMD_MAPPING, CMD_REQ_MAP, CMD_SET_VAL = 0x01, 0x02, 0x03, 0x04

# 类型映射表：字符 -> (struct格式, 字节数)
TYPE_INFO = {
    ord('f'): ('f', 4), ord('i'): ('i', 4), ord('I'): ('I', 4),
    ord('h'): ('h', 2), ord('H'): ('H', 2), ord('b'): ('b', 1), ord('B'): ('B', 1)
}


class RMDebuggerCLI:
    def __init__(self, chip="STM32F103C8"):
        self.jlink = pylink.JLink()
        self.jlink.open()
        self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.jlink.connect(chip)
        self.jlink.rtt_start()

        self.param_map = {}  # id -> {name, type, is_monitor, init_val}
        self.monitor_fmt = ""  # 动态生成的波形解析格式，如 "<fH"
        self.monitor_names = []  # 对应波形数据的变量名顺序
        self.monitor_ids = []
        self.running = True

    def send_packet(self, cmd, payload=None):
        payload = list(payload) if payload else []
        full_pkg = [FRAME_HEAD1, FRAME_HEAD2, cmd, len(payload)] + payload
        full_pkg.append(sum(full_pkg[2:]) & 0xFF)
        self.jlink.rtt_write(0, full_pkg)

    def receive_loop(self):
        buffer = bytearray()
        while self.running:
            data = self.jlink.rtt_read(0, 1024)
            if data:
                buffer.extend(data)
                while len(buffer) >= 5:
                    if buffer[0] == FRAME_HEAD1 and buffer[1] == FRAME_HEAD2:
                        cmd = buffer[2]
                        length = struct.unpack("<H", buffer[3:5])[0]

                        total_pkg_len = 2 + 1 + 2 + length + 1

                        if len(buffer) < total_pkg_len: break
                        payload = buffer[5: 5 + length]
                        if (sum(buffer[2: 5 + length]) & 0xFF) == buffer[5 + length]:
                            self.handle_payload(cmd, payload)
                        del buffer[: total_pkg_len]
                    else:
                        del buffer[0]
            time.sleep(0.01)

    def handle_payload(self, cmd, payload):
        if cmd == CMD_MAPPING:
            self.parse_mapping_package(payload)
        elif cmd == CMD_MONITOR:
            if self.monitor_fmt:
                data = struct.unpack(self.monitor_fmt, payload)
                for i, val in enumerate(data):
                    target_id = self.monitor_ids[i]
                    self.param_map[target_id]['val'] = val

    def parse_mapping_package(self, payload):
        """ 解析重构后的变长映射大包 """
        ptr = 0
        new_map = {}
        while ptr < len(payload):
            p_id = payload[ptr]
            ptr += 1
            p_type = payload[ptr]
            ptr += 1
            p_monitor = bool(payload[ptr])
            ptr += 1

            # 根据类型解出初始 Value
            fmt, size = TYPE_INFO.get(p_type, ('f', 4))
            val = struct.unpack(f"<{fmt}", payload[ptr: ptr + size])[0]
            ptr += size

            # 提取以 \0 结尾的 Name
            end = payload.find(b'\x00', ptr)
            name = payload[ptr:end].decode('utf-8')
            ptr = end + 1

            new_map[p_id] = {'name': name, 'type': chr(p_type), 'is_monitor': p_monitor, 'val': val}

        self.param_map = new_map
        self.rebuild_monitor_config()
        print("\n[SYSTEM] 映射表同步完成:")
        for i, info in self.param_map.items():
            print(f" ID {i}: {info['name']} ({info['type']}) | Monitor: {info['is_monitor']} | Value: {info['val']}")

    def rebuild_monitor_config(self):
        """ 重新构建波形解析格式 """
        # 1. 筛选出所有 is_monitor 为 True 的参数 ID，并进行升序排序
        self.monitor_ids = sorted([
            p_id for p_id, info in self.param_map.items() if info['is_monitor']
        ])

        # 2. 根据排序后的 ID 顺序，构建 struct 解析字符串
        # 比如 ID 0 是 float, ID 2 是 uint16 -> 格式为 "<fH"
        fmt_parts = []
        self.monitor_names = []

        for p_id in self.monitor_ids:
            info = self.param_map[p_id]
            fmt_parts.append(TYPE_INFO[ord(info['type'])][0])
            self.monitor_names.append(info['name'])

        self.monitor_fmt = "<" + "".join(fmt_parts)
        print(f"[DEBUG] 监控序列已更新: {self.monitor_names} (格式: {self.monitor_fmt})")

    def run(self):
        try:
            threading.Thread(target=self.receive_loop, daemon=True).start()
            print("--- RM 通用调试终端 --- (输入 'sync', 'ls', 'set [id] [val]', 'exit')")
            while self.running:
                cmd_in = input("\n>> ").strip().split()
                if not cmd_in: continue
                op = cmd_in[0].lower()
                if op == "sync":
                    self.send_packet(CMD_REQ_MAP)
                elif op == "ls":
                    for i, v in self.param_map.items(): print(f"[{i}] {v['name']}: {v['val']}")
                elif op == "set" and len(cmd_in) == 3:
                    p_id, val = int(cmd_in[1]), float(cmd_in[2])
                    fmt = TYPE_INFO[ord(self.param_map[p_id]['type'])][0]
                    # 根据该 ID 的实际类型进行打包发送
                    payload = struct.pack(f"<B{fmt}", p_id, val if 'f' in fmt else int(val))
                    self.send_packet(CMD_SET_VAL, payload)
                elif op == "exit":
                    self.running = False
                    self.jlink.rtt_stop()
                    self.jlink.close()
        except KeyboardInterrupt:
            self.running = False
            self.jlink.rtt_stop()
            self.jlink.close()


if __name__ == "__main__":
    RMDebuggerCLI().run()
