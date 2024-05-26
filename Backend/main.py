import socket
import os
import json
import logging

# Настройка логгера
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def handle_request(request, root_directory):
    lines = request.split('\r\n')
    if len(lines) > 0:
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) == 3:
            method, path, version = parts
            logger.debug(f"Method: {method}, Path: {path}, Version: {version}")
            if method == 'GET':
                if path == '/':
                    path = '/index.html'
                logger.debug(f"Requested Path: {path}")
                return serve_file(path, root_directory)
    return generate_response(404, "Not Found")

def serve_file(path, root_directory):
    full_path = os.path.join(root_directory, path.lstrip('/'))
    logger.debug(f"Full Path: {full_path}")
    if os.path.isfile(full_path):
        with open(full_path, 'rb') as f:
            body = f.read()
        return generate_response(200, 'OK', body, content_type='text/html')
    logger.debug("File not found")
    return generate_response(404, "Not Found")

def generate_response(status_code, status_text, body=b'', content_type='text/plain'):
    response_line = f"HTTP/1.1 {status_code} {status_text}\r\n"
    headers = f"Content-Type: {content_type}\r\n"
    headers += f"Content-Length: {len(body)}\r\n"
    headers += "\r\n"
    response = response_line + headers
    return response.encode() + body

def start_server(config):
    sock = socket.socket()
    port = config.get('port', 8080)
    try:
        sock.bind(('', port))
    except OSError:
        logger.error(f"Could not bind to port {port}. Trying port 8080.")
        port = 8080
        sock.bind(('', port))
    sock.listen(5)
    logger.info(f"Serving HTTP on port {port} ...")

    while True:
        conn, addr = sock.accept()
        logger.debug(f"Connected by {addr}")
        data = conn.recv(8192)
        if data:
            response = handle_request(data.decode(), config['root_directory'])
            conn.sendall(response)
        conn.close()

if __name__ == "__main__":
    config = load_config('config.json')
    start_server(config)
