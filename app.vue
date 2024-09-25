<script setup lang="ts">
const languageStore = useLanguageStore()
const themeStore = useThemeStore()

onMounted(() => {
  languageStore.setDefaultLanguage()
  themeStore.setDefaultTheme()
})
</script>

<template>
  <NuxtLayout>
    <v-app>
      <v-main class="bg-image">
        <NavBar />

        <NuxtPage />

        <Cookies />
      </v-main>
    </v-app>
  </NuxtLayout>
</template>

<style scoped>
.bg-image {
  background-image: url('~/assets/backgrounds/lec_bg2.jpg');
  background-position: top;
  background-repeat: no-repeat;
}
</style>
