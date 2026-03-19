import pylink
import time

def rtt_connect(chip_name = "STM32F103C8"):
    jlink = pylink.JLink()
    jlink.open()

    jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
    jlink.connect(chip_name)

    jlink.rtt_start()

    print(f"Connected to {chip_name} via RTT.")

    try:
        while True:
            terminal_data = jlink.rtt_read(0, 1024)

            if terminal_data:
                print("".join(map(chr, terminal_data)))
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nClosing JLink connection.")
        jlink.rtt_stop()
        jlink.close()

if __name__ == "__main__":
    rtt_connect("STM32F103C8")