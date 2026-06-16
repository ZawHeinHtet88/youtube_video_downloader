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

RUN mkdir -p /opt/bgutil && \
    git clone --single-branch --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil/repo && \
    cd /opt/bgutil/repo/server && \
    npm ci && \
    npx tsc && \
    cp -r /opt/bgutil/repo/server /opt/bgutil/server && \
    mkdir -p /root/.yt-dlp/plugins && \
    cp -r /opt/bgutil/repo/plugin/yt_dlp_plugins /root/.yt-dlp/plugins/

RUN echo "node version:" && node --version && \
    echo "yt-dlp plugins:" && ls -la /root/.yt-dlp/plugins/yt_dlp_plugins/extractor/ && \
    python -c "import yt_dlp; print('yt-dlp:', yt_dlp.version.__version__)" && \
    python -c "import yt_dlp_plugins.extractor.getpot_bgutil_script; print('plugin OK')"

COPY . .

RUN mkdir -p /app/downloads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
