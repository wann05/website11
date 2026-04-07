import sqlite3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKOUT_DB = os.path.join(BASE_DIR, "checkout.sqlite")
MEMBERS_DB = os.path.join(BASE_DIR, "members.sqlite")


def init_db():
    # Init Members DB
    conn_mem = sqlite3.connect(MEMBERS_DB)
    curr_mem = conn_mem.cursor()
    curr_mem.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn_mem.commit()
    conn_mem.close()

    # Init Checkout DB
    conn_chk = sqlite3.connect(CHECKOUT_DB)
    curr_chk = conn_chk.cursor()
    curr_chk.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quantity INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            email_address TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            payment_option TEXT NOT NULL,
            order_notes TEXT,
            ordered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn_chk.commit()
    conn_chk.close()


class RequestHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/members":
            try:
                conn = sqlite3.connect(MEMBERS_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM members ORDER BY applied_at DESC")
                rows = cursor.fetchall()
                members = [dict(row) for row in rows]
                conn.close()
                self.send_json(200, {"success": True, "data": members})
            except Exception as e:
                self.send_json(500, {"success": False, "error": str(e)})

        elif parsed_path.path == "/api/orders":
            try:
                conn = sqlite3.connect(CHECKOUT_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM orders ORDER BY ordered_at DESC")
                rows = cursor.fetchall()
                orders = [dict(row) for row in rows]
                conn.close()
                self.send_json(200, {"success": True, "data": orders})
            except Exception as e:
                self.send_json(500, {"success": False, "error": str(e)})

        else:
            self.send_json(404, {"success": False, "message": "Not found"})

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/join":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))

                conn = sqlite3.connect(MEMBERS_DB)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO members (first_name, last_name, email)
                    VALUES (?, ?, ?)
                """,
                    (
                        data.get("first_name"),
                        data.get("last_name"),
                        data.get("email")
                    ),
                )
                conn.commit()
                conn.close()

                self.send_json(200, {"success": True, "message": "Registration successful"})
            except Exception as e:
                self.send_json(500, {"success": False, "error": str(e)})

        elif parsed_path.path == "/api/checkout":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))

                conn = sqlite3.connect(CHECKOUT_DB)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO orders (quantity, full_name, email_address, phone_number, shipping_address, payment_option, order_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data.get("quantity"),
                        data.get("full_name"),
                        data.get("email_address"),
                        data.get("phone_number"),
                        data.get("shipping_address"),
                        data.get("payment_option"),
                        data.get("order_notes"),
                    ),
                )
                conn.commit()
                conn.close()

                self.send_json(200, {"success": True, "message": "Order placed successfully"})
            except Exception as e:
                self.send_json(500, {"success": False, "error": str(e)})

        else:
            self.send_json(404, {"success": False, "message": "Not found"})


def run(port=5000):
    init_db()
    server = HTTPServer(("", port), RequestHandler)
    print(f"Server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
