<script setup lang="ts">
// @ts-expect-error działa
import icon from '../public/favicon.ico'

const router = useRouter()

const appIcon = ref(icon)

function goHome() {
  router.push({ name: '/' })
}
</script>

<template>
  <v-app-bar>
    <v-img
      :src="appIcon"
      max-height="40"
      max-width="40"
      class="ml-4"
      rounded="circle"
      @click="goHome"
    />

    <!-- eslint-disable-next-line vue/no-bare-strings-in-template -->
    <v-app-bar-title>
      LeagueRats
    </v-app-bar-title>
  </v-app-bar>
</template>
