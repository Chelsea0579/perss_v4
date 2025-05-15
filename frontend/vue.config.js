const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 配置Vue Feature Flags，解决警告
  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      Object.assign(definitions[0], {
        __VUE_OPTIONS_API__: 'true',
        __VUE_PROD_DEVTOOLS__: 'false',
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      })
      return definitions
    })
  },
  
  // 开发服务器配置
  devServer: {
    port: 8091, // 前端端口
    
    // 代理配置
    proxy: {
      // 将所有 /api 请求代理到后端
      '/api': {
        target: 'http://localhost:8000', // 后端地址
        changeOrigin: true, // 更改源地址
        ws: true, // 代理 websockets
        pathRewrite: {
          '^/api': '/api' // 保持API路径不变
        },
        // 调试日志
        onProxyReq(proxyReq, req, res) {
          console.log(`[API代理] ${req.method} ${req.url} -> ${proxyReq.path}`);
        },
        onError(err, req, res) {
          console.error('[API代理] 错误:', err);
          
          // 如果代理失败，返回自定义错误信息
          if (res.writeHead && !res.headersSent) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
              success: false, 
              message: '无法连接到后端服务，请确保后端服务已启动',
              error: err.message
            }));
          }
        }
      }
    }
  },

  // 生产环境配置
  publicPath: '/',
  outputDir: 'dist',
  assetsDir: 'static',
  productionSourceMap: false,

  // 禁用 ESLint 保存时检查（可选）
  lintOnSave: false,

  // Vuetify配置
  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    }
  },

  // 调整内部webpack配置
  configureWebpack: {
    // 设置应用名称，会显示在浏览器标签页
    name: 'PERSS - 英语阅读支持系统',
    
    // 性能提示设置
    performance: {
      hints: false // 禁用性能提示
    }
  }
});