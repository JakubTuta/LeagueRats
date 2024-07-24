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
            'league-blue': '#4cb4f5',
            'league-red': '#f73b3b',
          },
        },
        dark: {
          dark: true,
          colors: {
            'primary': '#A87676',
            'secondary': '#87CACA',
            'league-blue': '#4cb4f5',
            'league-red': '#f73b3b',
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
    },
    display: {
      mobileBreakpoint: 'sm',
    },
  })
  app.vueApp.use(vuetify)
})
