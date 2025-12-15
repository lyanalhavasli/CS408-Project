# client.py

import socket

def run_client(server_ip="127.0.0.1", server_port=5000, username="Player1"):
    # Create TCP socket and connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print(f"[CLIENT] Connected to {server_ip}:{server_port}")

    # Send JOIN message
    join_msg = f"JOIN|{username}"
    sock.sendall(join_msg.encode("utf-8"))

    # Receive server response
    data = sock.recv(1024).decode("utf-8")
    if not data:
        print("[CLIENT] No response from server, connection closed.")
        sock.close()
        return

    data = data.strip()
    parts = data.split("|", 1)

    if parts[0] == "JOIN_ERROR":
        reason = parts[1] if len(parts) == 2 else "unknown"
        print(f"[CLIENT] Join error: {reason}")
        sock.close()
        return

    if parts[0] == "JOIN_OK":
        message = parts[1] if len(parts) == 2 else ""
        print(f"[CLIENT] {message}")
    else:
        print(f"[CLIENT] Unexpected response: {data}")
        sock.close()
        return

    # For now: manual send loop for testing (like a simple chat)
    try:
        while True:
            text = input("Enter message to send (or 'quit'): ")
            if text.lower() == "quit":
                break

            # Later we will send structured messages like ANSWER|...
            sock.sendall(text.encode("utf-8"))

    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("[CLIENT] Disconnected.")


if __name__ == "__main__":
    ip = input("Server IP [127.0.0.1]: ") or "127.0.0.1"
    port_str = input("Port [5000]: ") or "5000"
    username = input("Username: ")

    run_client(ip, int(port_str), username)
