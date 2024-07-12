<script setup lang="ts">
import { useLanguageStore } from '~/helpers/language'
import { useThemeStore } from '~/helpers/theme'

const currentLang = localStorage.getItem('current-lang')
const currentTheme = localStorage.getItem('current-theme')

const languageStore = useLanguageStore()
const themeStore = useThemeStore()

onMounted(() => {
  if (currentLang) {
    languageStore.setLanguage(currentLang)
  }
  else {
    languageStore.setLanguage('en')
  }

  if (currentTheme)
    themeStore.setTheme(currentTheme)
  else
    themeStore.setTheme('dark')
})
</script>

<template>
  <NuxtLayout>
    <v-app>
      <v-main>
        <NavBar />

        <NuxtPage />

        <Settings />
      </v-main>
    </v-app>
  </NuxtLayout>
</template>
