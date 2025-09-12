const url = require('url');

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

function isAdmin(req, token) {
    return req.cookies && req.cookies.token === token;
}

module.exports = {
    extractPath,
    isAdmin,
};