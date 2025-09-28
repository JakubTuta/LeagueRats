/* eslint-disable node/prefer-global/process */
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  app: {
    head: {
      title: 'League Rats',
      meta: [
        { name: 'description', content: 'Track and analyze professional League of Legends players, their stats, matches, and competitive achievements. Stay updated with pro players\' performance across different regions.' },
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
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        config?.plugins?.push(vuetify({ autoImport: true }))
      })
    },
  ],

  imports: {
    autoImport: true,
    dirs: [
      'stores/**',
      'constants/**',
      'components/**',
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
      server_url: process.env.SERVER_URL || 'http://localhost:8000',
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
    defaultLocale: 'en',
    vueI18n: './i18n.config.ts',
  },

  ssr: false,

  nitro: {
    preset: 'static',
  },

  typescript: {
    strict: true,
  },

  pinia: {
    storesDirs: ['./stores/**'],
  },

  compatibilityDate: '2024-07-18',
})
