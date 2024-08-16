import '@mdi/font/css/materialdesignicons.css'

import { createVuetify } from 'vuetify'
import 'vuetify/styles'

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    theme: {
      defaultTheme: 'dark',
      themes: {
        light: {
          dark: false,
          colors: {
            'primary': '#A87676',
            'secondary': '#76A8A8',
            'league-blue': '#23a7fa',
            'league-red': '#fc2626',
            'league-blue-transparent': 'rgba(35, 167, 250, 0.7)',
            'league-red-transparent': 'rgba(252, 38, 38, 0.7)',
          },
        },
        dark: {
          dark: true,
          colors: {
            'primary': '#A87676',
            'secondary': '#87CACA',
            'league-blue': '#23a7fa',
            'league-red': '#fc2626',
            'league-blue-transparent': 'rgba(35, 167, 250, 0.7)',
            'league-red-transparent': 'rgba(252, 38, 38, 0.7)',
          },
        },
      },
    },
    defaults: {
      VTextField: {
        variant: 'outlined',
      },
      VAutocomplete: {
        variant: 'outlined',
      },
      VBtn: {
        variant: 'outlined',
      },
      VContainer: {
        style: 'max-width: 1500px',
      },
    },
    display: {
      mobileBreakpoint: 'sm',
    },
  })
  app.vueApp.use(vuetify)
})
