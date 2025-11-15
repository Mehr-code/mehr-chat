import socket
import threading
from colorama import Fore, Style, init
import datetime

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
    print(
        Fore.YELLOW + f"🕓 Connected at {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    print(Fore.CYAN + "=" * 55 + "\n")


def receive_messages(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg:
                print(Fore.LIGHTCYAN_EX + f"\n💬 {msg}" + Style.RESET_ALL)
        except:
            print(Fore.RED + "\n❌ Connection lost!")
            break


def start_client():
    print_banner()
    HOST = input(Fore.YELLOW + "Enter server IP: " + Fore.WHITE)
    username = input(Fore.YELLOW + "Enter your username: " + Fore.WHITE)
    PORT = 5000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        client.send(username.encode())  # Send name first
        print(Fore.GREEN + f"✅ Connected as {username}!")
    except:
        print(Fore.RED + "❌ Could not connect to the server.")
        return

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    print(Fore.CYAN + "\nType your messages below. Type 'exit' to quit.\n")

    while True:
        msg = input(Fore.WHITE + f"{username}> ")
        if msg.lower() == "exit":
            print(Fore.YELLOW + "👋 Leaving Mehr Chat...")
            break
        if msg.strip() != "":
            try:
                client.send(msg.encode())
            except:
                print(Fore.RED + "⚠️  Failed to send message.")
                break

    client.close()


if __name__ == "__main__":
    start_client()
