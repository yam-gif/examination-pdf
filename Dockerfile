FROM python:3.10-slim

WORKDIR /app

# TeXLive と必要パッケージをインストール
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       texlive-latex-base \
       texlive-latex-recommended \
       texlive-latex-extra \
       texlive-fonts-recommended \
       texlive-lang-japanese \
       dvipdfmx \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Python 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Flask 実行設定
ENV PORT=5000
EXPOSE 5000
CMD ["python", "app.py"]
