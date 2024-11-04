<script setup lang="ts">
import { importantSelectRegions } from '~/helpers/regions';
import type { ILeaderboard } from '~/models/leaderboard';

const soloqStore = useSoloqStore()
const { leaderboardPerRegion } = storeToRefs(soloqStore)

const proStore = useProPlayerStore()
const { proAccountNames } = storeToRefs(proStore)

const { t } = useI18n()

const loading = ref(false)
const search = ref('')
const region = ref('EUW')
const league = ref('CHALLENGER')

const playersPerPage = 25

onMounted(() => {
  if (!proAccountNames.value) {
    proStore.getProAccountNames()
  }
})

const headers = computed(() => [
  {
    title: '#',
    value: 'rank',
    key: 'rank',
  },
  {
    title: t('bootcamp.account'),
    key: 'account',
    value: 'account',
    sortable: false,
  },
  {
    title: t('bootcamp.player'),
    key: 'player',
    value: 'player',
    sortable: false,
  },
  {
    title: t('bootcamp.totalGames'),
    key: 'totalGames',
    value: 'totalGames',
    align: 'center',
    sortRaw: (a: any, b: any) => {
      return (a.wins + a.losses) - (b.wins + b.losses)
    },
  },
  {
    title: t('bootcamp.wins'),
    key: 'wins',
    value: 'wins',
    align: 'center',
  },
  {
    title: t('bootcamp.losses'),
    key: 'losses',
    value: 'losses',
    align: 'center',
  },
  {
    title: t('bootcamp.winRate'),
    key: 'winRate',
    value: 'winRate',
    align: 'center',
    sortRaw: (a: any, b: any) => {
      return a.wins / (a.wins + a.losses) - b.wins / (b.wins + b.losses)
    },
  },
])

watch(region, async () => {
  loading.value = true
  await soloqStore.getFirstLeaderboardForRegion(region.value, league.value, playersPerPage)
  loading.value = false

  soloqStore.getOtherLeaderboardForRegion(region.value, league.value)
}, { immediate: true })

function customFilter(_value: string, query: string, item: any) {
  const gameName = item.raw.gameName.toLowerCase()

  return gameName.includes(query.toLowerCase())
}

function getProPlayer(item: ILeaderboard) {
  if (!proAccountNames.value) {
    return null
  }

  return proAccountNames.value[item.puuid] || null
}
</script>

<template>
  <v-container>
    <v-card v-if="loading">
      <v-skeleton-loader
        type="card"
        width="80%"
        class="mx-auto my-8"
      />
    </v-card>

    <v-card v-else>
      <v-card-title class="text-h5">
        {{ $t('leaderboard.title') }}
      </v-card-title>

      <v-row
        justify="space-between"
        class="mx-2 mt-1"
      >
        <v-col
          cols="12"
          sm="4"
        >
          <v-text-field
            v-model="search"
            :label="$t('universal.search')"
            append-inner-icon="mdi-magnify"
          />
        </v-col>

        <v-col
          cols="12"
          sm="4"
        >
          <v-select
            v-model="league"
            :items="['CHALLENGER']"
            label="Region"
          />
        </v-col>

        <v-col
          cols="12"
          sm="4"
        >
          <v-select
            v-model="region"
            :items="importantSelectRegions"
            label="Region"
          />
        </v-col>
      </v-row>

      <v-card-text v-if="leaderboardPerRegion[region].length">
        <v-data-table
          :items="leaderboardPerRegion[region]"
          :headers="headers"
          :items-per-page="playersPerPage"
          :custom-filter="customFilter"
          :search="search"
          :sort-by="[
            {
              'key': 'rank',
              'order': 'asc',
            },
          ]"
        >
          <template #item.account="{item}">
            <NuxtLink
              style="cursor: pointer; text-decoration: none; color: inherit;"
              :to="`/account/EUW/${item.gameName}-${item.tagLine}`"
            >
              <span class="text-subtitle-1">
                {{ item.gameName }}
              </span>

              <span class="text-caption ml-2">
                {{ `#${item.tagLine}` }}
              </span>
            </NuxtLink>
          </template>

          <template
            #item.player="{item}"
          >
            <NuxtLink
              v-if="getProPlayer(item)"
              style="cursor: pointer; text-decoration: none; color: inherit;"
              :to="`/player/${getProPlayer(item)!.team}/${getProPlayer(item)!.player}`"
            >
              {{ `${getProPlayer(item)!.team} ${getProPlayer(item)!.player}` }}
            </NuxtLink>
          </template>

          <template #item.totalGames="{item}">
            {{ item.wins + item.losses }}
          </template>

          <template #item.winRate="{item}">
            {{ (item.wins / (item.wins + item.losses) * 100).toFixed(2) }}%
          </template>
        </v-data-table>
        <!--
          <v-list>
          <v-list-item
          v-for="player in leaderboardPerRegion[region]"
          :key="player.puuid"
          lines="two"
          :to="`/account/${region}/${player.gameName}-${player.tagLine}`"
          >
          <template #prepend>
          {{ player.rank }}
          </template>

          {{ player.gameName }}
          </v-list-item>
          </v-list>
        -->
      </v-card-text>

      <v-card-text
        v-else
        class="text-h5"
      >
        {{ $t('leaderboard.noPlayers') }}
      </v-card-text>
    </v-card>
  </v-container>
</template>
