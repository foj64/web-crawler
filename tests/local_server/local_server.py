import os
import threading
import http.server
import socketserver

PORT = 8081

# Definir o diretório raiz para o servidor como o diretório onde o script está localizado
web_dir = os.path.join(os.path.dirname(__file__), '')
os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

def run_server():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = False
    server_thread.start()

if __name__ == "__main__":
    run_server()
