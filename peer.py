from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import socket, threading, json, time, os

from crypto_utils import *

# ===================== CONFIG =====================
USERNAME = input("Username: ")
P2P_PORT = int(input("P2P listen port (e.g. 6000): "))
WEB_PORT = int(input("Web port (e.g. 5000): "))

DISCOVERY_PORT = 9999
DISCOVERY_INTERVAL = 30
RATE_LIMIT_SECONDS = 1
HISTORY_DIR = "history"

os.makedirs(HISTORY_DIR, exist_ok=True)

# ===================== APP =====================
app = Flask(__name__)
socketio = SocketIO(app)

# ===================== CRYPTO =====================
private_key, public_key = generate_keypair()

connections = {}      # peer -> socket
shared_keys = {}      # peer -> aes key
known_fingerprints = set()
last_message_time = {}

# ===================== UTIL =====================
def rate_limited(peer):
    now = time.time()
    if peer not in last_message_time or now - last_message_time[peer] > RATE_LIMIT_SECONDS:
        last_message_time[peer] = now
        return False
    return True

def save_history(peer, payload):
    path = os.path.join(HISTORY_DIR, f"{peer}.dat")
    with open(path, "ab") as f:
        f.write(encrypt(shared_keys[peer], payload) + b"\n")

# ===================== P2P =====================
def handle_peer(conn, peer):
    key = shared_keys[peer]
    while True:
        try:
            encrypted = conn.recv(4096)
            if not encrypted:
                break

            data = decrypt(key, encrypted)

            if data.get("private") and data["private"] != USERNAME:
                continue

            if data["type"] == "msg":
                socketio.emit("message", f"[{data['sender']}]: {data['msg']}")

            elif data["type"] == "file":
                with open(f"recv_{data['name']}", "ab") as f:
                    f.write(bytes.fromhex(data["chunk"]))

            save_history(peer, data)

        except Exception as e:
            print("Receive error:", e)
            continue

    connections.pop(peer, None)
    socketio.emit("system", f"{peer} disconnected")

def p2p_listener():
    s = socket.socket()
    s.bind(("0.0.0.0", P2P_PORT))
    s.listen()

    while True:
        conn, addr = s.accept()

        data = json.loads(conn.recv(4096).decode())
        peer = data["username"]

        peer_pub_bytes = data["pubkey"].encode()
        peer_pub = deserialize_public_key(peer_pub_bytes)

        fp = fingerprint(peer_pub_bytes)
        if fp not in known_fingerprints:
            known_fingerprints.add(fp)
            socketio.emit("system", f"Fingerprint {peer}: {fp}")

        conn.send(json.dumps({
            "pubkey": serialize_public_key(public_key).decode()
        }).encode())

        shared_keys[peer] = derive_shared_key(private_key, peer_pub)
        connections[peer] = conn

        socketio.emit("system", f"{peer} joined the group")

        threading.Thread(
            target=handle_peer,
            args=(conn, peer),
            daemon=True
        ).start()

threading.Thread(target=p2p_listener, daemon=True).start()

# ===================== DISCOVERY =====================
def discovery_broadcast():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        s.sendto(
            json.dumps({
                "user": USERNAME,
                "port": P2P_PORT
            }).encode(),
            ("255.255.255.255", DISCOVERY_PORT)
        )
        time.sleep(DISCOVERY_INTERVAL)

def discovery_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", DISCOVERY_PORT))
    seen = set()
    while True:
        data, addr = s.recvfrom(1024)
        info = json.loads(data.decode())
        if info["user"] != USERNAME and info["user"] not in seen:
            seen.add(info["user"])
            socketio.emit(
                "system",
                f"Discovered {info['user']} @ {addr[0]}:{info['port']}"
            )

threading.Thread(target=discovery_broadcast, daemon=True).start()
threading.Thread(target=discovery_listener, daemon=True).start()

# ===================== FLASK =====================
@app.route("/")
def index():
    return render_template("chat.html")

@socketio.on("connect_peer")
def connect_peer(data):
    peer = data["peer"]
    ip = data["ip"]
    port = int(data["port"])

    s = socket.socket()
    s.connect((ip, port))

    s.send(json.dumps({
        "username": USERNAME,
        "pubkey": serialize_public_key(public_key).decode()
    }).encode())

    response = json.loads(s.recv(4096).decode())
    peer_pub = deserialize_public_key(response["pubkey"].encode())

    shared_keys[peer] = derive_shared_key(private_key, peer_pub)
    connections[peer] = s

    emit("system", f"Connected to {peer}")

    threading.Thread(
        target=handle_peer,
        args=(s, peer),
        daemon=True
    ).start()

@socketio.on("send_message")
def send_message(data):
    text = data["message"]
    private = data.get("private")

    for peer, conn in connections.items():
        if rate_limited(peer):
            continue

        payload = {
            "type": "msg",
            "sender": USERNAME,
            "msg": text,
            "private": private,
            "ts": time.time()
        }

        encrypted = encrypt(shared_keys[peer], payload)
        conn.send(encrypted)
        save_history(peer, payload)

    emit("message", f"[You]: {text}")

@socketio.on("send_file")
def send_file(data):
    peer = data["peer"]
    path = data["path"]

    with open(path, "rb") as f:
        while chunk := f.read(1024):
            payload = {
                "type": "file",
                "name": os.path.basename(path),
                "chunk": chunk.hex()
            }
            encrypted = encrypt(shared_keys[peer], payload)
            connections[peer].send(encrypted)

socketio.run(app, port=WEB_PORT)
