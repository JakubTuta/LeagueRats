<script setup lang="ts">
import type { IProPlayer } from '~/models/proPlayer';

const props = defineProps<{
  player: IProPlayer | null
}>()

const { player } = toRefs(props)

const isShow = defineModel<boolean>('isShow', { default: false })

function close() {
  isShow.value = false
}
</script>

<template>
  <v-dialog
    v-model="isShow"
    max-width="800px"
  >
    <v-card v-if="player">
      <v-card-title>
        {{ `${player.team} ${player.player}` }}
      </v-card-title>

      <v-divider />

      <v-card-text>
        Soon...
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-btn
          color="error"
          @click="close"
        >
          {{ $t('universal.form.close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
