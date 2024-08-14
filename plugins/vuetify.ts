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
          },
        },
        dark: {
          dark: true,
          colors: {
            'primary': '#A87676',
            'secondary': '#87CACA',
            'league-blue': '#23a7fa',
            'league-red': '#fc2626',
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
