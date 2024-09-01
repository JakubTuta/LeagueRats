<script setup lang="ts">
// @ts-expect-error correct path
import imgLck from '~/assets/regions/lck.png'
// @ts-expect-error correct path
import imgLcs from '~/assets/regions/lcs.png'
// @ts-expect-error correct path
import imgLec from '~/assets/regions/lec.png'
// @ts-expect-error correct path
import imgLpl from '~/assets/regions/lpl.png'
import { teamFullName, teamPerRegion } from '~/helpers/regions'
import type { IProAccount } from '~/models/pro_account'

const proStore = useProPlayerStore()
const { players } = storeToRefs(proStore)

const loading = ref(false)
const selectedRegion = ref('lec')
const loadedPlayers = ref<IProAccount[]>([])
const filterRoles = ref(['TOP', 'JNG', 'MID', 'ADC', 'SUP'])
const filterTeams = ref<string[]>([])

const mapRole: { [key: string]: number } = {
  TOP: 1,
  JNG: 2,
  MID: 3,
  ADC: 4,
  SUP: 5,
}

const regions = [
  {
    title: 'LEC',
    value: 'lec',
    image: imgLec,
  },
  {
    title: 'LCS',
    value: 'lcs',
    image: imgLcs,
  },
  {
    title: 'LCK',
    value: 'lck',
    image: imgLck,
  },
  {
    title: 'LPL',
    value: 'lpl',
    image: imgLpl,
  },
]

const filteredPlayers = computed(() => {
  return loadedPlayers.value.filter(player => filterTeams.value.includes(player.team))
    .filter(player => filterRoles.value.includes(player.role))
    .sort((a, b) => mapRole[a.role] - mapRole[b.role])
    .sort((a, b) => a.team.localeCompare(b.team))
})

const mapTeamItems = computed(() => {
  return teamPerRegion[selectedRegion.value.toUpperCase()]
    .map(team => ({
      title: team,
      props: { subtitle: teamFullName[team] },
    }))
})

watch(selectedRegion, async (region) => {
  loading.value = true

  filterTeams.value = teamPerRegion[region.toUpperCase()]

  await proStore.getProPlayersForRegion(region)

  loadedPlayers.value = players.value.splice(0, 10)

  loading.value = false
}, { immediate: true })

watch(filterRoles, () => {
  filterRoles.value = filterRoles.value.sort((a, b) => mapRole[a] - mapRole[b])
})

function loadPlayers({ done }: { done: (status: string) => void }) {
  const newPlayers = players.value.slice(loadedPlayers.value.length, loadedPlayers.value.length + 10)

  if (!newPlayers.length) {
    done('empty')

    return
  }

  loadedPlayers.value.push(...newPlayers)

  done('ok')
}

function teamCustomFilter(_value: string, query: string, item: { title: string, props: { subtitle: string } }) {
  return item.title.toLowerCase().includes(query.toLowerCase()) || item.props.subtitle.toLowerCase().includes(query.toLowerCase())
}
</script>

<template>
  <v-container>
    <v-card>
      <v-card-title class="my-2">
        <v-row>
          <v-col
            v-for="region in regions"
            :key="region.value"
            align="center"
            cols="12"
            sm="6"
            md="3"
          >
            <!-- primary-transparent -->
            <v-card
              elevation="0"
              style="cursor: pointer;"
              :color="region.value === selectedRegion
                ? 'rgba(142, 147, 108, 0.25)'
                : ''"
              @click.stop="() => selectedRegion = region.value"
            >
              <v-img
                :src="region.image"
                max-width="100"
                max-height="100"
                aspect-ratio="1"
                cover
                class="mb-5"
              />

              {{ region.title }}
            </v-card>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text
        v-if="loading"
        align="center"
      >
        <v-skeleton-loader
          type="card"
          class="ma-4"
        />

        {{ `${$t('proPlayers.loadingPlayers')}...` }}
      </v-card-text>

      <v-card-text v-else>
        <v-row>
          <v-col
            cols="12"
            sm="6"
          >
            <v-select
              v-model="filterRoles"
              multiple
              chips
              clearable
              single-line
              :label="$t('proPlayers.roles')"
              :items="[
                'TOP',
                'JNG',
                'MID',
                'ADC',
                'SUP',
              ]"
              @click:clear="() => filterRoles = []"
            >
              <template #prepend-item>
                <v-list-item
                  class="mb-1"
                  :title="$t('universal.selectAll')"
                  @click="() => filterRoles = [
                    'TOP',
                    'JNG',
                    'MID',
                    'ADC',
                    'SUP',
                  ]"
                />
              </template>
            </v-select>
          </v-col>

          <v-col
            cols="12"
            sm="6"
          >
            <v-autocomplete
              v-model="filterTeams"
              style="cursor: pointer;"
              multiple
              chips
              single-line
              clearable
              :label="$t('proPlayers.teams')"
              :items="mapTeamItems"
              :custom-filter="teamCustomFilter"
              @click:clear="() => filterTeams = []"
            >
              <template #prepend-item>
                <v-list-item
                  class="mb-1"
                  :title="$t('universal.selectAll')"
                  @click="() => filterTeams = teamPerRegion[selectedRegion.toUpperCase()]"
                />
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>

        <v-infinite-scroll
          height="70vh"
          empty-text=""
          :items="filteredPlayers"
          @load="loadPlayers"
        >
          <template
            v-for="player in filteredPlayers"
            :key="player.player"
          >
            <v-list-item class="my-2">
              {{ player.player }}
            </v-list-item>
          </template>
        </v-infinite-scroll>
      </v-card-text>
    </v-card>
  </v-container>
</template>
