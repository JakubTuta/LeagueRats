<script setup lang="ts">
import { useDisplay } from 'vuetify'
// @ts-expect-error correct path
import imgLck from '~/assets/regions/lck.png'
// @ts-expect-error correct path
import imgLcs from '~/assets/regions/lcs.png'
// @ts-expect-error correct path
import imgLec from '~/assets/regions/lec.png'
// @ts-expect-error correct path
import imgLpl from '~/assets/regions/lpl.png'
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

const { mdAndUp, sm } = useDisplay()

const proStore = useProPlayerStore()
const { players } = storeToRefs(proStore)

const storageStore = useStorageStore()
const { teamLogos } = storeToRefs(storageStore)

const loading = ref(false)
const selectedRegion = ref('lec')
const filterRoles = ref(['TOP', 'JNG', 'MID', 'ADC', 'SUP'])
const filterTeams = ref<string[]>([])
const savedTeams = ref<string[]>([])

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
  return players.value.filter(player => filterTeams.value.includes(player.team))
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

watch(selectedRegion, (region) => {
  loading.value = true
  const upperCaseRegion = region.toUpperCase()

  proStore.resetPlayers()

  filterTeams.value = teamPerRegion[upperCaseRegion].sort((a, b) => a.localeCompare(b))
  const newTeams = filterTeams.value.slice(0, 2)
  savedTeams.value = newTeams

  newTeams.forEach((team) => {
    proStore.getProPlayersFromTeam(upperCaseRegion, team)
    storageStore.getTeamLogo(upperCaseRegion, team)
  })

  loading.value = false
}, { immediate: true })

watch(filterRoles, () => {
  filterRoles.value = filterRoles.value.sort((a, b) => mapRole[a] - mapRole[b])
})

async function loadPlayers({ done }: { done: (status: string) => void }) {
  const notSavedTeams = filterTeams.value.filter(team => !savedTeams.value.includes(team))

  if (!notSavedTeams.length) {
    done('empty')

    return
  }

  const newTeam = notSavedTeams[0]

  proStore.getProPlayersFromTeam(selectedRegion.value.toUpperCase(), newTeam)
  storageStore.getTeamLogo(selectedRegion.value.toUpperCase(), newTeam)

  savedTeams.value.push(newTeam)

  await new Promise(resolve => setTimeout(resolve, 150))

  done('ok')
}

function teamCustomFilter(_value: string, query: string, item: { title: string, props: { subtitle: string } }) {
  return item.title.toLowerCase().includes(query.toLowerCase()) || item.props.subtitle.toLowerCase().includes(query.toLowerCase())
}

const scrollHeight = computed(() => {
  const height = window.innerHeight

  if (height < 1000)
    return '50vh'
  else if (height < 1250)
    return '55vh'
  else if (height < 1500)
    return '60vh'
  else if (height < 1750)
    return '65vh'
  else if (height < 2000)
    return '70vh'
  else
    return '75vh'
})

const imageWidth = computed(() => {
  if (mdAndUp.value)
    return 75
  else if (sm.value)
    return 50
  else
    return 25
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
  <v-container>
    <v-card>
      <v-card-title class="my-2">
        <v-row>
          <v-col
            v-for="region in regions"
            :key="region.value"
            align="center"
            cols="12"
            sm="3"
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
                :max-width="imageWidth"
                aspect-ratio="1"
                cover
                class="mb-5"
              />

              {{ region.title }}
            </v-card>
          </v-col>
        </v-row>
      </v-card-title>

      <v-spacer class="my-2" />

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
              chips
              clearable
              single-line
              multiple
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
          :height="scrollHeight"
          empty-text=""
          :margin="100"
          :items="filteredPlayers"
          @load="loadPlayers"
        >
          <template
            v-for="player in filteredPlayers"
            :key="player.player"
          >
            <v-list-item
              class="my-2"
            >
              <template
                #prepend
              >
                <v-avatar
                  rounded="0"
                  size="70"
                >
                  <v-img
                    src="~/assets/default.png"
                  />
                </v-avatar>

                <span>
                  <p>
                    <v-avatar
                      rounded="0"
                      size="35"
                    >
                      <v-img :src="teamLogos[player.team]" />
                    </v-avatar>
                  </p>

                  <p>
                    <v-avatar
                      rounded="0"
                      size="35"
                    >
                      <v-img :src="getPlayerRoleIcon(player)" />
                    </v-avatar>
                  </p>
                </span>
              </template>

              <v-list-item-title class="text-h6 ml-1">
                {{ player.player }}
              </v-list-item-title>

              <v-list-item-subtitle class="text-subtitle-2 ml-1">
                {{ teamFullName[player.team] }}
              </v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-infinite-scroll>
      </v-card-text>
    </v-card>
  </v-container>
</template>
