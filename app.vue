<script setup lang="ts">
import 'twitch-stream-embed'
import { useDisplay } from 'vuetify'

// const languageStore = useLanguageStore()
// const themeStore = useThemeStore()

const appStore = useAppStore()

const { height, width } = useDisplay()

onMounted(() => {
  appStore.getInitialData()
  // languageStore.setDefaultLanguage()
  // themeStore.setDefaultTheme()
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

        <!-- <Cookies /> -->
      </v-main>
    </v-app>
  </NuxtLayout>
</template>

<style>
.bg-image {
  background-image: url('~/assets/background.jpg');
  background-size: cover;
  background-position: top;
  background-repeat: no-repeat;
}

.card-dark {
  background-color: rgba(50, 50, 50, 0.9);
}

.card-light {
  background-color: rgba(180, 180, 180, 0.9);
}

.fading-background-win {
  background: linear-gradient(to right, rgba(35, 167, 250, 0.75), rgba(35, 167, 250, 0.25));
}

.fading-background-lose {
  background: linear-gradient(to right, rgba(252, 38, 38, 0.75), rgba(252, 38, 38, 0.25));
}
</style>
