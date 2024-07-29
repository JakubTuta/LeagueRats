export const useLanguageStore = defineStore('language', () => {
  const { locale, setLocale } = useI18n()

  const setLanguage = (lang: string) => {
    locale.value = lang
    localStorage.setItem('current-lang', lang)
    setLocale(lang)
  }

  return {
    setLanguage,
  }
})
