import pl from './locales/pl.json'
import en from './locales/en.json'

export default defineI18nConfig(() => ({
  useCookie: true,
  legacy: false,
  locale: 'pl',
  locales: ['pl', 'en'],
  defaultLocale: 'pl',
  fallbackLocale: 'en',
  messages: {
    pl,
    en,
  },
}))
