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
            primary: '#A87676',
            secondary: '#76A8A8',
          },
        },
        dark: {
          dark: true,
          colors: {
            primary: '#A87676',
            secondary: '#87CACA',
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
  })
  app.vueApp.use(vuetify)
})
