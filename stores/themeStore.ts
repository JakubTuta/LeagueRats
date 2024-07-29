import { useTheme } from 'vuetify'

export const useThemeStore = defineStore('theme', () => {
  const theme = useTheme()

  const toggleTheme = () => {
    theme.global.name.value = theme.global.current.value.dark
      ? 'light'
      : 'dark'
    localStorage.setItem('current-theme', theme.global.name.value)
  }

  const setTheme = (newTheme: string) => {
    theme.global.name.value = newTheme
    localStorage.setItem('current-theme', newTheme)
  }

  const isDark = computed(() => theme.global.name.value === 'dark')

  return {
    toggleTheme,
    setTheme,
    isDark,
  }
})
