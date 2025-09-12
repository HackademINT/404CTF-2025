from urllib.parse import unquote, parse_qs

class Request:
    def __init__(self, raw_data):
        self.method = None
        self.path = None
        self.query_string = None
        self.headers = {}
        self.cookies = {}
        self.parse(raw_data)

    def parse(self, raw_data):
        try:
            lines = raw_data.split('\r\n')
            request_line = lines[0].split()
            self.method, request_target = request_line[0], unquote(request_line[1])
            self.path = request_target.split('?')[0]
            self.query_string = parse_qs(request_target.split('?')[1]) if '?' in request_target else {}

            for header_line in lines[1:]:
                if ': ' in header_line:
                    key, value = header_line.split(': ', 1)
                    self.headers[key.lower()] = value

            if 'cookie' in self.headers:
                self.cookies = (dict(i.split('=', 1) for i in self.headers['cookie'].split('; ')))

        except Exception as e:
            print("Failed to parse request:", e)
