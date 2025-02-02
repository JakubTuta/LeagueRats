<script setup lang="ts">
import { useDisplay } from 'vuetify'
// @ts-expect-error correct path
import topIcon from '~/assets/roles/top.png'
// @ts-expect-error correct path
import jngIcon from '~/assets/roles/jng.png'
// @ts-expect-error correct path
import midIcon from '~/assets/roles/mid.png'
// @ts-expect-error correct path
import adcIcon from '~/assets/roles/adc.png'
// @ts-expect-error correct path
import supIcon from '~/assets/roles/sup.png'
import { teamFullName } from '~/helpers/regions'
import type { IProPlayer } from '~/models/proPlayer'

const route = useRoute()
const { mobile, height } = useDisplay()

const storageStore = useStorageStore()
const proPlayerStore = useProPlayerStore()

const loading = ref(false)
const teamName = ref('')
const players = ref<IProPlayer[]>([])

const mapRole: { [key: string]: number } = {
  TOP: 1,
  JNG: 2,
  MID: 3,
  ADC: 4,
  SUP: 5,
}

onMounted(() => {
  loading.value = true

  const team = (route.params.team as string).toUpperCase()

  teamName.value = team

  players.value = proPlayerStore.getProPlayersFromTeam(team)
    .sort((a, b) => mapRole[a.role] - mapRole[b.role])

  loading.value = false
})

function getPlayerRoleIcon(player: { role: string }) {
  switch (player.role) {
    case 'TOP':
      return topIcon
    case 'JNG':
      return jngIcon
    case 'MID':
      return midIcon
    case 'ADC':
      return adcIcon
    case 'SUP':
      return supIcon
    default:
      return ''
  }
}
</script>

<template>
  <v-container
    :class="mobile
      ? ''
      : 'fill-height'"
  >
    <v-row
      class="pa-3"
      align="center"
      justify="center"
    >
      <Loader v-if="loading" />

      <v-card v-else-if="!loading && !teamName">
        <v-card-title
          align="center"
          class="my-3"
        >
          {{ $t('proPlayers.notFoundTeam') }}
        </v-card-title>
      </v-card>

      <v-card v-else-if="!loading && teamName">
        <v-card-title align="center">
          <p class="my-4">
            <v-avatar
              size="130"
              class="pa-3"
            >
              <v-img
                :src="storageStore.getTeamLogo(teamName)"
                lazy-src="~/assets/default.png"
              />
            </v-avatar>
          </p>

          {{ teamFullName[teamName] }}
        </v-card-title>

        <v-card-text class="mt-2">
          <p
            v-if="!players.length"
            class="text-subtitle-1 ma-4"
          >
            {{ $t('proPlayers.noAccounts') }}
          </p>

          <v-list
            v-else
            lines="three"
            :style="`max-height: ${height - 400}px; overflow-y: auto;`"
          >
            <v-list-item
              v-for="player in players"
              :key="player.player"
              class="my-2"
              :to="`/player/${player.team}/${player.player}`"
            >
              <template #prepend>
                <v-avatar
                  rounded="0"
                  size="90"
                  class="mr-1"
                >
                  <v-img
                    :src="storageStore.getPlayerImage(player.player)"
                    lazy-src="~/assets/default.png"
                  />
                </v-avatar>

                <v-avatar
                  rounded="0"
                  size="45"
                >
                  <v-img :src="getPlayerRoleIcon(player)" />
                </v-avatar>
              </template>

              <v-row align="center">
                <v-col
                  cols="12"
                  sm="5"
                  md="4"
                  class="text-h6"
                >
                  {{ player.player }}
                </v-col>
              </v-row>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-row>
  </v-container>
</template>
