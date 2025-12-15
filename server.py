# server.py

import socket
import threading
from questions import load_questions

HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5000        # you can change this

class QuizServerCore:
    """
    Pure core server: handles TCP connections and player registration.

    - First message from each client must be: "JOIN|<name>"
    - Responds with:
        "JOIN_OK|Welcome, <name>"
      or
        "JOIN_ERROR|reason"
    """

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port

        self.server_sock = None
        # player_name -> socket
        self.players = {}
        # For later: scores, etc.
        self.scores = {}

        self.lock = threading.Lock()
        self.running = False

        # Quiz data (loaded from file)
        self.questions = []
        self.num_questions_to_ask = 0

    # ---------- setup / teardown ----------

    def load_question_file(self, path):
        self.questions = load_questions(path)
        print(f"[SERVER] Loaded {len(self.questions)} questions from {path}")

    def start(self):
        """Start listening for incoming TCP connections (non-blocking)."""
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()
        self.running = True

        print(f"[SERVER] Listening on {self.host}:{self.port}")

        # Accept loop in a background thread
        threading.Thread(target=self.accept_loop, daemon=True).start()

    def stop(self):
        """Stop the server and close all client sockets."""
        self.running = False

        if self.server_sock:
            try:
                self.server_sock.close()
            except OSError:
                pass

        with self.lock:
            for sock in self.players.values():
                try:
                    sock.close()
                except OSError:
                    pass
            self.players.clear()
            self.scores.clear()

        print("[SERVER] Stopped.")

    # ---------- connection handling ----------

    def accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
            except OSError:
                break  # socket closed

            print(f"[SERVER] New connection from {addr}")
            threading.Thread(
                target=self.handle_client,
                args=(client_sock, addr),
                daemon=True
            ).start()

    def handle_client(self, client_sock, addr):
        """
        Handle a single client.

        First message must be JOIN|name.
        After that, for now we just print any messages they send (for testing).
        Later we will expand this to handle ANSWER|... messages.
        """
        name = None

        try:
            # Receive the first message
            data = client_sock.recv(1024).decode("utf-8")
            if not data:
                client_sock.close()
                return

            data = data.strip()
            parts = data.split("|", 1)

            if len(parts) != 2 or parts[0] != "JOIN":
                print(f"[SERVER] Invalid join message from {addr}: {data}")
                client_sock.sendall(
                    "JOIN_ERROR|invalid_join_format".encode("utf-8")
                )
                client_sock.close()
                return

            name = parts[1].strip()

            if not name:
                client_sock.sendall("JOIN_ERROR|empty_name".encode("utf-8"))
                client_sock.close()
                return

            # Check for duplicate name
            with self.lock:
                if name in self.players:
                    client_sock.sendall(
                        "JOIN_ERROR|name_taken".encode("utf-8")
                    )
                    client_sock.close()
                    print(f"[SERVER] Rejected duplicate name '{name}' from {addr}")
                    return

                # Accept the player
                self.players[name] = client_sock
                self.scores[name] = 0
                print(f"[SERVER] Player '{name}' joined from {addr}")

            client_sock.sendall(
                f"JOIN_OK|Welcome, {name}".encode("utf-8")
            )

            # For now: just loop and print any further messages.
            # We will replace this with full quiz handling later.
            while True:
                data = client_sock.recv(1024).decode("utf-8")
                if not data:
                    break
                msg = data.strip()
                print(f"[SERVER] From {name}: {msg}")
                # Later: handle ANSWER|... and other commands here.

        except ConnectionResetError:
            # Client closed abruptly; ignore.
            pass
        finally:
            # Cleanup on disconnect
            if name:
                with self.lock:
                    if name in self.players and self.players[name] is client_sock:
                        del self.players[name]
                        if name in self.scores:
                            del self.scores[name]
                print(f"[SERVER] Player '{name}' disconnected")
            try:
                client_sock.close()
            except OSError:
                pass


if __name__ == "__main__":
    # Simple manual test (no GUI yet)
    server = QuizServerCore()
    server.load_question_file("quiz_qa.txt")
    server.num_questions_to_ask = min(5, len(server.questions))  # just for later

    server.start()
    print("Press Enter to stop the server...")
    input()
    server.stop()
