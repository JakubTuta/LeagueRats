<script setup lang="ts">
import { champions, searchChampion } from '~/const/champions';

const search = ref('')
</script>

<template>
  <v-container>
    <v-autocomplete
      v-model="search"
      prepend-inner-icon="mdi-magnify"
      clearable
      :items="champions"
      :custom-filter="searchChampion"
      @click:append="search = ''"
    />
  </v-container>
</template>
