import { useTheme } from 'vuetify'

export const useThemeStore = defineStore('theme', () => {
  const defaultTheme = 'dark'

  const theme = useTheme()

  const currentTheme = useCookie('current-theme', {
    default: () => ('dark'),
    maxAge: 60 * 60 * 24 * 365,
  })
  const isAcceptedCookies = useCookie('is-accepted-cookies', {
    default: () => false,
    maxAge: 60 * 60 * 24 * 365,
  })

  const isDark = computed(() => theme.global.name.value === 'dark')

  const setTheme = (newTheme: string) => {
    if (isAcceptedCookies.value) {
      currentTheme.value = newTheme
    }

    theme.global.name.value = newTheme
  }

  const setDefaultTheme = () => {
    if (!isAcceptedCookies.value) {
      setTheme(defaultTheme)
    }
    else {
      setTheme(currentTheme.value)
    }
  }

  return {
    currentTheme,
    isDark,
    setTheme,
    setDefaultTheme,
  }
})
