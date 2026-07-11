import vue from '@vitejs/plugin-vue';
import {resolve} from 'path';
import {defineConfig, loadEnv, ConfigEnv} from 'vite';
import monacoEditorPlugin from 'vite-plugin-monaco-editor';

const pathResolve = (dir: string) => {
  return resolve(__dirname, '.', dir);
};

const alias: Record<string, string> = {
  '/@': pathResolve('./src/'),
};

const viteConfig = defineConfig((mode: ConfigEnv) => {
  const env = loadEnv(mode.mode, process.cwd());
  return {
    plugins: [vue(), monacoEditorPlugin()],
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        '@vueuse/core',
        'pinia',
        'axios',
        'splitpanes',
        'screenfull',
        'echarts',
        'monaco-editor',
        'element-plus/es',
        'element-plus/es/components/form/style/index',
        'element-plus/es/components/radio-group/style/index',
        'element-plus/es/components/radio/style/index',
        'element-plus/es/components/checkbox/style/index',
        'element-plus/es/components/checkbox-group/style/index',
        'element-plus/es/components/switch/style/index',
        'element-plus/es/components/time-picker/style/index',
        'element-plus/es/components/date-picker/style/index',
        'element-plus/es/components/col/style/index',
        'element-plus/es/components/form-item/style/index',
        'element-plus/es/components/alert/style/index',
        'element-plus/es/components/breadcrumb/style/index',
        'element-plus/es/components/select/style/index',
        'element-plus/es/components/input/style/index',
        'element-plus/es/components/breadcrumb-item/style/index',
        'element-plus/es/components/tag/style/index',
        'element-plus/es/components/pagination/style/index',
        'element-plus/es/components/table/style/index',
        'element-plus/es/components/table-column/style/index',
        'element-plus/es/components/card/style/index',
        'element-plus/es/components/row/style/index',
        'element-plus/es/components/button/style/index',
        'element-plus/es/components/menu/style/index',
        'element-plus/es/components/sub-menu/style/index',
        'element-plus/es/components/menu-item/style/index',
        'element-plus/es/components/option/style/index',
        '@element-plus/icons-vue',
      ],
    },
    root: process.cwd(),
    resolve: {alias},
    base: mode.command === 'serve' ? './' : env.VITE_PUBLIC_PATH,
    server: {
      host: '0.0.0.0',
      port: env.VITE_PORT as unknown as number,
      open: JSON.parse(env.VITE_OPEN),
      hmr: true,
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8100',
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      chunkSizeWarningLimit: 1500,
      rolldownOptions: {
        output: {
          entryFileNames: 'assets/[name].[hash].js',
          chunkFileNames: 'assets/[name].[hash].js',
          assetFileNames: 'assets/[name].[hash].[ext]',
          codeSplitting: {
            groups: [
              {
                name: 'vue',
                test: /node_modules\/(vue|vue-router|pinia)/,
              },
              {
                name: 'echarts',
                test: /node_modules\/echarts/,
              },
            ],
          },
        },
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          silenceDeprecations: ['import'],
        },
        css: {charset: false},
      },
      postcss: {
        plugins: [
          {
            postcssPlugin: 'internal:charset-removal',
            AtRule: {
              charset: (atRule) => {
                if (atRule.name === 'charset') {
                  atRule.remove();
                }
              },
            },
          },
        ],
      },
    },
    define: {
      __VERSION__: JSON.stringify(process.env.npm_package_version),
    },
  };
});

export default viteConfig;
