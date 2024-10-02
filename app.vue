<script setup lang="ts">
import { useDisplay } from 'vuetify'

const languageStore = useLanguageStore()
const themeStore = useThemeStore()

const { height, width } = useDisplay()

onMounted(() => {
  languageStore.setDefaultLanguage()
  themeStore.setDefaultTheme()
})
</script>

<template>
  <NuxtLayout>
    <v-app>
      <v-main
        class="bg-image"
        :style="`width: ${width}px; height: ${height}px`"
      >
        <NavBar />

        <NuxtPage />

        <Cookies />
      </v-main>
    </v-app>
  </NuxtLayout>
</template>

<style scoped>
.bg-image {
  background-image: url('~/assets/background.jpg');
  background-size: cover;
  background-position: top;
  background-repeat: no-repeat;
}
</style>
