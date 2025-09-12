class Response:
    def __init__(self, status_code=200, body='', content_type='text/html'):
        self.status_code = status_code
        self.body = body
        self.headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(body))
        }

    def set_header(self, key, value):
        self.headers[key] = value

    def build(self):
        reason_phrases = {
            200: 'OK',
            301: 'Moved Permanently',
            404: 'Not Found',
            403: 'Forbidden',
            405: 'Method Not Allowed',
            500: 'Internal Server Error'
        }

        status_line = f"HTTP/1.1 {self.status_code} {reason_phrases.get(self.status_code, '')}"
        headers = '\r\n'.join(f"{k}: {v}" for k, v in self.headers.items())
        return f"{status_line}\r\n{headers}\r\n\r\n{self.body}"