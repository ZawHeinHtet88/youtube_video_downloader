FROM brainicism/bgutil-ytdlp-pot-provider:latest AS potserver

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

COPY --from=potserver /app /opt/bgutil/server

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade yt-dlp && \
    pip install --no-cache-dir bgutil-ytdlp-pot-provider

COPY . .
RUN chmod +x entrypoint.sh && mkdir -p /app/downloads

EXPOSE 8000

CMD ["./entrypoint.sh"]
