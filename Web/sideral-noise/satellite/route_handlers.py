from urllib.parse import quote
from response import Response
from os import urandom, environ

is_authenticated = lambda request: request.cookies.get('token') == environ['SATELLITE_TOKEN']

def index(request):
    body = ""
    if 'error' in request.query_string:
        error_message = request.query_string['error'][0]
        body += f"<b>Error: {error_message}<b>"
    if is_authenticated(request):
        body += "<h1>Welcome, Administrator</h1>"
        body += f"<p>Here is the flag: {environ.get('FLAG', '404CTF{fake_flag}')}</p>"
        return Response(200, body)
    else:
        body += "<h1>Forbidden</h1>"
        body += "<p>You are not authorized to view this page.</p>"
        return Response(403, body)
        
def noise(request):
    if not is_authenticated(request):
        return Response(403, "<h1>Forbidden</h1><p>You are not authorized to view this page.</p>")
    body = urandom(256).hex() # pure sideral noise !!
    response = Response(200, body, content_type='text/plain')
    return response

def not_found(request):
    body = "<h1>Not found</h1>"
    response = Response(301, body)
    response.set_header('Location', '/satellite?error=' + quote('The following resource was not found: ') + request.path)
    return response