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
            'primary': 'rgba(168, 118, 118, 1)',
            'primary-transparent': 'rgba(168, 118, 118, 0.25)',
            'secondary': 'rgba(118, 168, 168, 1)',
            'league-blue': 'rgba(35, 167, 250, 1)',
            'league-red': 'rgba(252, 38, 38, 1)',
            'league-blue-transparent': 'rgba(35, 167, 250, 0.3)',
            'league-red-transparent': 'rgba(252, 38, 38, 0.3)',
          },
        },
        dark: {
          dark: true,
          colors: {
            'primary': 'rgba(168, 118, 118, 1)',
            'primary-transparent': 'rgba(168, 118, 118, 0.25)',
            'secondary': 'rgba(118, 168, 168, 1)',
            'league-blue': 'rgba(35, 167, 250, 1)',
            'league-red': 'rgba(252, 38, 38, 1)',
            'league-blue-transparent': 'rgba(35, 167, 250, 0.3)',
            'league-red-transparent': 'rgba(252, 38, 38, 0.3)',
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
        style: 'max-width: 1300px',
      },
    },
    display: {
      mobileBreakpoint: 'sm',
    },
  })
  app.vueApp.use(vuetify)
})
