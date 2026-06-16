FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade yt-dlp && \
    pip install --no-cache-dir bgutil-ytdlp-pot-provider

RUN git clone --single-branch --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil/repo && \
    cd /opt/bgutil/repo/server && \
    npm install && \
    npx tsc && \
    mkdir -p /opt/bgutil/server && \
    cp -r build node_modules src package.json /opt/bgutil/server/ && \
    rm -rf /opt/bgutil/repo

COPY . .
RUN chmod +x entrypoint.sh && mkdir -p /app/downloads

EXPOSE 8000

CMD ["./entrypoint.sh"]
