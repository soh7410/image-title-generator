FROM node:16-alpine

WORKDIR /app

# 依存関係をインストール
COPY package*.json ./
RUN npm install

# アプリケーションをコピー
COPY . .

# ポートを公開
EXPOSE 8080

# コマンドを実行
CMD ["npm", "run", "serve"]
