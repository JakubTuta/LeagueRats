import en from './locales/en.json'
import pl from './locales/pl.json'

export default defineI18nConfig(() => ({
  useCookie: true,
  legacy: false,
  locale: 'en',
  locales: ['pl', 'en'],
  defaultLocale: 'en',
  fallbackLocale: 'pl',
  messages: {
    pl,
    en,
  },
}))
