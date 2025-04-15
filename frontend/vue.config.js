module.exports = {
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://backend:8000',  // Docker Compose内のサービス名を使用
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  }
}
