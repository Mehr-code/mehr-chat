import socket
import threading
import datetime
from colorama import Fore, Style, init
import sys

init(autoreset=True)

# === SETTINGS ===
HOST = "0.0.0.0"
PORT = 5000
running = True

# === STORAGE ===
users = {}  # conn -> username
reverse_users = {}  # username -> conn
rooms = {"lobby": set()}  # room_name -> {conn, conn, ...}
user_room = {}  # conn -> room_name


# === UTILS ===
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def print_banner():
    print(Fore.CYAN + "=" * 55)
    print(
        Fore.MAGENTA
        + r"""
        ▗▖  ▗▖▗▄▄▄▖▗▖ ▗▖▗▄▄▖      ▗▄▄▖▗▖ ▗▖ ▗▄▖▗▄▄▄▖
        ▐▛▚▞▜▌▐▌   ▐▌ ▐▌▐▌ ▐▌    ▐▌   ▐▌ ▐▌▐▌ ▐▌ █  
        ▐▌  ▐▌▐▛▀▀▘▐▛▀▜▌▐▛▀▚▖    ▐▌   ▐▛▀▜▌▐▛▀▜▌ █  
        ▐▌  ▐▌▐▙▄▄▖▐▌ ▐▌▐▌ ▐▌    ▝▚▄▄▖▐▌ ▐▌▐▌ ▐▌ █       
   
               💬  M E H R   C H A T  💬
    """
    )
    print(Fore.CYAN + "=" * 55)
    print(
        Fore.YELLOW
        + f"🚀 Server started at {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    print(Fore.GREEN + f"🌐 Your local IP: {get_local_ip()}")
    print(Fore.CYAN + f"📡 Listening on port {PORT}")
    print(Fore.CYAN + "=" * 55 + "\n")


# === ROOM BROADCAST ===
def broadcast_to_room(room, message, sender=None):
    for conn in list(rooms[room]):
        if conn != sender:
            try:
                conn.send(message.encode())
            except:
                disconnect_client(conn)


def disconnect_client(conn):
    username = users.get(conn, None)

    if conn in users:
        del reverse_users[users[conn]]
        del users[conn]

    if conn in user_room:
        room = user_room[conn]
        if conn in rooms[room]:
            rooms[room].remove(conn)
        del user_room[conn]

    try:
        conn.close()
    except:
        pass

    if username:
        broadcast_to_room("lobby", f"🔴 {username} left the chat.")


# === PRIVATE MESSAGE ===
def handle_private_message(conn, msg):
    try:
        target, text = msg.split(" ", 1)
    except:
        conn.send("❌ Invalid private message format.\n".encode())
        return

    target_name = target[1:]
    if target_name not in reverse_users:
        conn.send("❌ User not found.\n".encode())
        return

    receiver = reverse_users[target_name]
    sender_name = users[conn]

    try:
        receiver.send(f"💌 [Private from {sender_name}] {text}".encode())
        conn.send(f"📨 [To {target_name}] {text}".encode())
    except:
        pass


# === COMMANDS ===
def handle_command(conn, cmd):
    parts = cmd.split()
    command = parts[0]

    username = users[conn]

    # /join room
    if command == "/join":
        if len(parts) < 2:
            conn.send("❌ Usage: /join room_name\n".encode())
            return

        new_room = parts[1]

        old_room = user_room[conn]
        rooms[old_room].remove(conn)

        if new_room == old_room:
            conn.send(f"⚠️ You are already in room: {new_room}\n".encode())
            return

        if new_room not in rooms:
            rooms[new_room] = set()

        rooms[new_room].add(conn)
        user_room[conn] = new_room

        conn.send(f"🔄 You joined room: {new_room}\n".encode())
        broadcast_to_room(new_room, f"🟢 {username} joined {new_room}", sender=conn)
        return

    # /leave → go to lobby
    if command == "/leave":
        old = user_room[conn]
        if old == "lobby":
            conn.send("❌ You are already in lobby.\n".encode())
            return

        rooms[old].remove(conn)
        rooms["lobby"].add(conn)
        user_room[conn] = "lobby"

        conn.send("↩️ You returned to lobby.\n".encode())
        return

    # /rooms → list rooms
    if command == "/rooms":
        room_list = "🏠 Rooms:\n"
        for r in rooms:
            room_list += f"- {r} ({len(rooms[r])} users)\n"
        conn.send(room_list.encode())
        return

    conn.send("❌ Unknown command.\n".encode())


# === HANDLE CLIENT ===
def handle_client(conn, addr):
    try:
        username = conn.recv(1024).decode().strip()
        users[conn] = username
        reverse_users[username] = conn

        rooms["lobby"].add(conn)
        user_room[conn] = "lobby"

        print(Fore.GREEN + f"[+] {username} ({addr[0]}) connected")
        broadcast_to_room("lobby", f"🟢 {username} joined the chat!", sender=conn)

        conn.send("🎉 Welcome to Mehr Chat!\n".encode())

        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break

            if msg.startswith("/"):
                handle_command(conn, msg)

            elif msg.startswith("@"):
                handle_private_message(conn, msg)

            else:
                room = user_room[conn]
                broadcast_to_room(room, f"{username}: {msg}", sender=conn)

    except:
        pass

    # Cleanup
    disconnect_client(conn)
    print(Fore.RED + f"[-] {addr} disconnected")


# === SHUTDOWN ===
def shutdown_server(server):
    global running
    running = False
    print(Fore.YELLOW + "\n⚠️  Shutting down server...")

    for conn in list(users.keys()):
        try:
            conn.send("💥 Server is shutting down.\n".encode())
        except:
            pass
        disconnect_client(conn)

    server.close()
    print(Fore.RED + "🛑 Server stopped.")
    sys.exit(0)


def command_listener(server):
    while True:
        cmd = input(Fore.YELLOW + "\n💻 Server command> ").strip().lower()
        if cmd in ["shutdown", "exit", "quit"]:
            shutdown_server(server)


# === START SERVER ===
def start_server():
    global running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print_banner()

    threading.Thread(target=command_listener, args=(server,), daemon=True).start()

    while running:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
        except OSError:
            break


# === MAIN ===
if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print(Fore.RED + "\n🧨 Keyboard interrupt detected. Exiting...")
        sys.exit(0)
