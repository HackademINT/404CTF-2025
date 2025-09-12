const express = require('express');
const path = require('path');
const crypto = require('crypto');
const cookieParser = require('cookie-parser');
const { visit } = require("./bot.js");
const { isAdmin, extractPath } = require('./utils.js');
var spaceships = require('./spaceships.json');

const TOKEN = crypto.randomBytes(32).toString('hex');
const PORT = process.env.PORT || 3000;
const CHALLENGE_HOST = process.env.CHALLENGE_HOST || `localhost:${PORT}` // in production CHALLENGE_HOST=spacefleetcommand.404ctf.fr

for (let i = 0; i < spaceships.length; i++) {
    if (spaceships[i].classified) {
        spaceships[i].name = process.env.FLAG || "404CTF{fake_flag}";
    }
}

const app = express();

app.use(cookieParser());
app.use(express.urlencoded());
app.use(express.static(path.join(__dirname, 'public'), { maxAge: 3600000 })); 
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'none';"); // javascript belongs in the backend !
    next();
});

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));


app.get('/', (req, res) => {
    const query = req.query.q;
    const filteredShips = spaceships.filter(ship =>
        (!query || ship.name.toLowerCase().startsWith(query.toLowerCase())) && (!ship.classified || isAdmin(req, TOKEN))
    );
    res.status(filteredShips.length ? 200 : 404).render('pages/index', { spaceships: filteredShips, query: query });
});

app.get('/spaceship/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id, 10);
        const spaceship = spaceships.find(s => s.id === id);
        if (!spaceship || (spaceship.classified && !isAdmin(req, TOKEN))) {
            return res.status(404).send('Spaceship not found');
        }
        res.render('pages/spaceship', { spaceship: spaceship });
    }
    catch (error) {
        return res.status(400).send('Error retrieving spaceship');
    }
});

app.get('/report', (req, res) => {
    res.render('pages/report', { message: '' });
});

app.post('/report', (req, res) => {
    const url = req.body.url;
    if (!url) {
        return res.status(400).send('Missing URL');
    }
    const path = extractPath(url);
    if (!path) {
        return res.render('pages/report', { message: `The URL <i>${url}</i> is not valid.` });
    }
    visit(path, TOKEN, CHALLENGE_HOST)
        .then(() => {
            res.render('pages/report', { message: `The page was visited by our admin. We'll get back to you soon.` });
        })
        .catch((error) => {
            console.error('Error visiting URL:', error);
            res.render('pages/report', { message: `An error occurred while visiting the URL <i>${url}</i>.` });
        });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Admin token: ${TOKEN}`);
});

process.on('SIGINT', async function () {
    console.log('Shutting down server...');
    process.exit();
});