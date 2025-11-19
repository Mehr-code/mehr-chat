import socket
import threading
from colorama import Fore, Style, init
import datetime
import sys

init(autoreset=True)


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
    print(Fore.YELLOW + f"🕓 Started at {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(Fore.CYAN + "=" * 55 + "\n")


def print_help():
    print(
        Fore.LIGHTGREEN_EX
        + """
📘 Available Commands:
--------------------------------------
/rooms          → list all rooms
/join roomName  → join or auto-create a room
/leave          → return to lobby
@username msg   → send a private message
exit            → exit the chat
--------------------------------------
    """
    )


def receive_messages(client):
    while True:
        try:
            msg = client.recv(2048).decode()
            if msg:
                print(Fore.LIGHTCYAN_EX + f"\n💬 {msg}" + Style.RESET_ALL)
                print(Fore.WHITE + "> ", end="")
        except:
            print(Fore.RED + "\n❌ Connection lost!")
            break


def start_client():
    print_banner()
    HOST = input(Fore.YELLOW + "🌐 Enter server IP: " + Fore.WHITE).strip()
    username = input(Fore.YELLOW + "👤 Enter your username: " + Fore.WHITE).strip()

    if not username:
        print(Fore.RED + "❌ Username cannot be empty.")
        return

    PORT = 5000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        client.send(username.encode())
        print(Fore.GREEN + f"\n✅ Connected as {username}!")
        print_help()
    except:
        print(Fore.RED + "❌ Could not connect to the server.")
        return

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    print(Fore.CYAN + "\nType your messages below ⬇️\n")

    while True:
        msg = input(Fore.WHITE + f"{username}> ").strip()

        if msg.lower() == "exit":
            print(Fore.YELLOW + "👋 Leaving Mehr Chat...")
            break

        if not msg:
            continue

        try:
            client.send(msg.encode())
        except:
            print(Fore.RED + "⚠️ Failed to send message.")
            break

    client.close()
    sys.exit(0)


if __name__ == "__main__":
    start_client()
