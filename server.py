from http.server import BaseHTTPRequestHandler, HTTPServer
from algorithms import Grafo
import json

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == '/grafo.png':
            try:
                with open('grafo.png', 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/processar':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Parse input data
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'Invalid JSON format'}).encode('utf-8'))
                    return
                
                # Validate required fields
                required_fields = ['materias', 'cursadas', 'semestreAtual']
                if not all(field in data for field in required_fields):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode('utf-8'))
                    return
                
                # Process data
                try:
                    grafo = Grafo(data['materias'])
                    recomendacoes = grafo.bfs_recomendacao(data['cursadas'], data['semestreAtual'])
                    cadeias = grafo.encontrar_cadeias()
                    
                    resposta = {
                        'recomendacoes': recomendacoes,
                        'cadeias': cadeias
                    }
                    
                    self._set_headers()
                    self.wfile.write(json.dumps(resposta).encode('utf-8'))
                except Exception as e:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({'error': f'Processing error: {str(e)}'}).encode('utf-8'))
                
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': f'Server error: {str(e)}'}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))
        

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()