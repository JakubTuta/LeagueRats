import { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  app: {
    head: {
      title: 'League Rats',
      meta: [
        { name: 'description', content: 'Strona z profesjonalnymi rozgrywkami gry League of Legends' },
      ],
    },
  },

  build: {
    transpile: ['vuetify'],
  },

  modules: [
    '@vueuse/nuxt',
    '@unocss/nuxt',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    '@nuxtjs/i18n',
  ],

  imports: {
    autoImport: true,
    dirs: [
      'stores/**',
      'constants/**',
      'utils/**',
    ],
  },

  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },

  runtimeConfig: {
    public: {
      NODE_ENV: process.env.NODE_ENV,
      APP_VERSION: process.env.npm_package_version,
      apiKey: process.env.API_KEY,
      authDomain: process.env.AUTH_DOMAIN,
      projectId: process.env.PROJECT_ID,
      storageBucket: process.env.STORAGE_BUCKET,
      messagingSenderId: process.env.MESSAGING_SENDER_ID,
      appId: process.env.APP_ID,
    },
  },

  i18n: {
    strategy: 'no_prefix',
    defaultLocale: 'pl',
    vueI18n: './i18n.config.ts',
  },

  ssr: false,

  nitro: {
    static: true,
    esbuild: {
      options: {
        target: 'esnext',
      },
    },
    prerender: {
      crawlLinks: true,
      routes: ['/'],
    },
  },

  typescript: {
    strict: true,
  },
})
