export const useLanguageStore = defineStore('language', () => {
  const defaultLang = 'en'

  const { locale, setLocale } = useI18n()

  const currentLang = useCookie('current-lang', {
    default: () => 'en',
    maxAge: 60 * 60 * 24 * 365,
  })
  const isAcceptedCookies = useCookie('is-accepted-cookies', {
    default: () => false,
    maxAge: 60 * 60 * 24 * 365,
  })

  const setLanguage = (lang: string) => {
    if (isAcceptedCookies.value) {
      currentLang.value = lang
    }

    locale.value = lang
    setLocale(lang)
  }

  const setDefaultLanguage = () => {
    if (!isAcceptedCookies.value) {
      setLanguage(defaultLang)
    }
    else {
      setLanguage(currentLang.value)
    }
  }

  return {
    currentLang,
    setLanguage,
    setDefaultLanguage,
  }
})
