import serial, threading, queue, time

events = queue.Queue()

def _reader(port, baud):
    while True:
        try:
            with serial.Serial(port, baud, timeout=1) as ser:
                while True:
                    line = ser.readline().decode(errors="ignore").strip()
                    if line:
                        events.put(line)
        except serial.SerialException as e:
            print("[joystick] error:", e)
            time.sleep(2)

def start(port, baud=115200):
    threading.Thread(target=_reader, args=(port, baud), daemon=True).start()

def get_events():
    """Return all commands received since the last call."""
    out = []
    while not events.empty():
        out.append(events.get_nowait())
    return out