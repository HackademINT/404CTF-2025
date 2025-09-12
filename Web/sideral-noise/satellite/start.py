from server import HTTPServer, Route
from route_handlers import index, noise, not_found
from os import environ

if __name__ == "__main__":
    server = HTTPServer('0.0.0.0', environ.get('PORT', 8000), not_found)
    server.routes.append(Route(r'^/satellite/?$', index))
    server.routes.append(Route(r'^/satellite/noise/[A-Za-z0-9_-]{21}$', noise))
    server.start()