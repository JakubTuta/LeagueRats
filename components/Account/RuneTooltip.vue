<script setup lang="ts">
import type { IRuneData } from '~/models/runeInfo'

const props = defineProps<{
  rune: IRuneData | null
}>()

const { rune } = toRefs(props)
</script>

<template>
  <v-card
    elevation="0"
    max-width="300px"
    style="background-color: rgba(0, 0, 0, 0);"
  >
    <v-card-title text-align-center>
      {{ rune?.name || '' }}
    </v-card-title>

    <v-card-text>
      {{ rune?.shortDesc || '' }}
    </v-card-text>
  </v-card>
</template>
