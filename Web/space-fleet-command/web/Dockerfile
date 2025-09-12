FROM node:22

WORKDIR /home/app/

# Install Chrome
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/package.json src/package-lock.json /home/app/
RUN npm ci --omit=dev
COPY src/ /home/app/
RUN chmod -R a+r /home/app/

EXPOSE 3000

CMD ["node", "app.js"]
