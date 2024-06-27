import os
import threading
import http.server
import socketserver
import time

PORT = 8081

# Definir o diretório raiz para o servidor como o diretório onde o script está localizado
web_dir = os.path.join(os.path.dirname(__file__), '')
os.chdir(web_dir)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/slowpage.html':
            time.sleep(3)  # Simular resposta lenta
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
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
