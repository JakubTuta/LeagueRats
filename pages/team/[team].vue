<script setup lang="ts">
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
import { teamFullName, teamPerRegion } from '~/helpers/regions'
import type { IProPlayer } from '~/models/proPlayer'

const route = useRoute()

const storageStore = useStorageStore()
const { teamImages } = storeToRefs(storageStore)

const proStore = useProPlayerStore()

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

function findRegionForTeam(team: string) {
  if (!team)
    return

  for (const [region, teams] of Object.entries(teamPerRegion)) {
    if (teams.includes(team))
      return region
  }
}

onMounted(async () => {
  loading.value = true

  const team = (route.params.team as string).toUpperCase()
  const proRegion = findRegionForTeam(team)

  if (!proRegion)
    return

  teamName.value = team

  players.value = (await proStore.returnProPlayersFromTeam(proRegion, team))
    .sort((a, b) => mapRole[a.role] - mapRole[b.role])

  if (proRegion)
    storageStore.getTeamImages(proRegion, team)

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
  <div
    style="display: flex;
    justify-content: center;
    align-items: center;
    height: 90%;"
  >
    <v-container>
      <v-card v-if="loading">
        <v-skeleton-loader
          type="card"
          width="90%"
          class="mx-auto my-8"
        />
      </v-card>

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
            <v-avatar size="150">
              <v-img
                :src="teamImages[teamName]?.team"
                lazy-src="~/assets/default.png"
              />
            </v-avatar>
          </p>

          {{ teamFullName[teamName] }}
        </v-card-title>

        <v-card-text class="mt-4">
          <span class="text-h5 ml-5">
            {{ $t('proPlayers.players') }}
          </span>

          <p
            v-if="!players.length"
            class="text-subtitle-1 ma-4"
          >
            {{ $t('proPlayers.noAccounts') }}
          </p>

          <v-list
            v-else
            lines="two"
          >
            <v-list-item
              v-for="player in players"
              :key="player.player"
              class="my-2"
              lines="three"
              :to="`/player/${player.team}/${player.player}`"
            >
              <template #prepend>
                <v-avatar
                  rounded="0"
                  size="70"
                  class="mr-1"
                >
                  <v-img
                    :src="teamImages[player.team]?.[player.player.toLowerCase()]"
                    lazy-src="~/assets/default.png"
                  />
                </v-avatar>

                <v-avatar
                  rounded="0"
                  size="35"
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
    </v-container>
  </div>
</template>
