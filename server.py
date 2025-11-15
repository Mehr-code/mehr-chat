import socket
import threading
import datetime
from colorama import Fore, Style, init
import sys

init(autoreset=True)

# === SETTINGS ===
HOST = "0.0.0.0"
PORT = 5000
clients = {}
running = True


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


def broadcast(message, sender_conn=None):
    for conn in list(clients.keys()):
        if conn != sender_conn:
            try:
                conn.send(message.encode())
            except:
                conn.close()
                del clients[conn]


def handle_client(conn, addr):
    try:
        username = conn.recv(1024).decode().strip()
        clients[conn] = username
        print(Fore.GREEN + f"[+] {username} ({addr[0]}) connected ✅")
        broadcast(f"🟢 {username} joined the chat!", conn)
        conn.send("🎉 Welcome to Mehr Chat!".encode())

        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            formatted = f"{Fore.CYAN}[{username}] {Fore.WHITE}{msg}"
            print(formatted)
            broadcast(f"{username}: {msg}", conn)

    except:
        pass

    print(Fore.RED + f"[-] {clients.get(conn, addr)} disconnected ❌")
    broadcast(f"🔴 {clients.get(conn, addr)} left the chat.")
    if conn in clients:
        del clients[conn]
    print(Fore.CYAN + f"👥 Active clients: {len(clients)}")
    conn.close()


def shutdown_server(server):
    global running
    running = False
    print(Fore.YELLOW + "\n⚠️  Shutting down server...")
    broadcast("💥 Server is shutting down. See you soon!")
    for conn in list(clients.keys()):
        conn.close()
    clients.clear()
    server.close()
    print(Fore.RED + "🛑 Server stopped.")
    sys.exit(0)


def command_listener(server):
    while True:
        cmd = input(Fore.YELLOW + "\n💻 Server command> ").strip().lower()
        if cmd in ["shutdown", "exit", "quit"]:
            shutdown_server(server)


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
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(Fore.CYAN + f"👥 Active clients: {len(clients) + 1}")
        except OSError:
            break


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print(Fore.RED + "\n🧨 Keyboard interrupt detected. Exiting...")
        sys.exit(0)
