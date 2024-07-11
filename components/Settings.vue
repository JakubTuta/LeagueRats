<script setup lang="ts">
const isShowSettings = ref(false)

function showSettings() {
  isShowSettings.value = !isShowSettings.value
}

function closeSettings() {
  isShowSettings.value = false
}
</script>

<template>
  <v-btn
    style="position: absolute; left: 10px; bottom: 10px"
    icon
    variant="outlined"
    @click="showSettings"
  >
    <v-icon icon="mdi-cog-outline" />
  </v-btn>

  <SettingsDialog
    :is-show="isShowSettings"
    @close="closeSettings"
  />
</template>
