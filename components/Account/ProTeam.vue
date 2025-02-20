<script setup lang="ts">
import type { IProPlayer } from '~/models/proPlayer';

const props = defineProps<{
  team: string
}>()

const { team } = toRefs(props)

const isShow = defineModel<boolean>('isShow', { default: false })

const proStore = useProPlayerStore()
const storageStore = useStorageStore()

const players = ref<IProPlayer[]>([])

const mapLane: Record<'TOP' | 'JNG' | 'MID' | 'ADC' | 'SUP', number> = {
  TOP: 1,
  JNG: 2,
  MID: 3,
  ADC: 4,
  SUP: 5,
}

watch(team, (newTeam) => {
  if (newTeam)
    findTeamMembers()
})

function close() {
  isShow.value = false
}

function findTeamMembers() {
  if (!team.value)
    return

  players.value = proStore.getProPlayersFromTeam(team.value)
  players.value = players.value.sort((a, b) => mapLane[a.role] - mapLane[b.role])
}
</script>

<template>
  <v-dialog
    :model-value="isShow"
    max-width="800px"
    @update:model-value="close"
  >
    <v-card>
      <v-card-title>
        {{ team }}
      </v-card-title>

      <v-card-text>
        <v-list>
          <v-list-item
            v-for="player in players"
            :key="player.player"
            lines="two"
          >
            <v-list-item-title class="ml-2">
              {{ player.player }}
            </v-list-item-title>

            <template #prepend>
              <v-avatar size="100">
                <v-img
                  :src="storageStore.getPlayerImage(player.player)"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>

      <v-card-actions>
        <v-btn
          text
          color="error"
          @click="close"
        >
          {{ $t('universal.form.close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
