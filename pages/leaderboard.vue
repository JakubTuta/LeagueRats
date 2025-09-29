<script setup lang="ts">
import { importantSelectRegions } from '~/helpers/regions'
import type { ILeaderboard } from '~/models/leaderboard'

const soloqStore = useSoloqStore()
const { leaderboardPerRegion } = storeToRefs(soloqStore)

const proStore = useProPlayerStore()
const { proAccountNames } = storeToRefs(proStore)

const appStore = useAppStore()
const { loading: appLoading } = storeToRefs(appStore)

const { t } = useI18n()

const loading = ref(false)
const search = ref('')
const region = ref('EUW')
const league = ref('CHALLENGER')
const isOnlyPros = ref(false)

const playersPerPage = 25
const maxPlayers = 300

const accounts = computed(() => {
  if (!leaderboardPerRegion.value[region.value]) {
    return []
  }

  const tmp = leaderboardPerRegion.value[region.value].map((account) => {
    return {
      ...account,
      player: getProPlayer(account),
    }
  })

  return tmp
})

const filteredAccounts = computed(() => {
  if (!isOnlyPros.value) {
    return accounts.value
  }

  return accounts.value.filter(account => account.player)
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
    title: 'LP',
    key: 'leaguePoints',
    value: 'leaguePoints',
    align: 'center' as const,
  },
  {
    title: t('bootcamp.totalGames'),
    key: 'totalGames',
    value: 'totalGames',
    align: 'center' as const,
    sortRaw: (a: any, b: any) => {
      return (a.wins + a.losses) - (b.wins + b.losses)
    },
  },
  {
    title: t('bootcamp.wins'),
    key: 'wins',
    value: 'wins',
    align: 'center' as const,
  },
  {
    title: t('bootcamp.losses'),
    key: 'losses',
    value: 'losses',
    align: 'center' as const,
  },
  {
    title: t('bootcamp.winRate'),
    key: 'winRate',
    value: 'winRate',
    align: 'center' as const,
    sortRaw: (a: any, b: any) => {
      return a.wins / (a.wins + a.losses) - b.wins / (b.wins + b.losses)
    },
  },
])

watch(region, async () => {
  loading.value = true
  await soloqStore.getLeaderboardForRegion(region.value, playersPerPage, 1)
  loading.value = false

  const pages = Math.floor(maxPlayers / playersPerPage)
  for (let i = 2; i <= pages; i++) {
    soloqStore.getLeaderboardForRegion(region.value, playersPerPage, i)
  }
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
    <Loader v-if="loading || appLoading" />

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
            :label="$t('leaderboard.rank')"
          />
        </v-col>

        <v-col
          cols="12"
          sm="4"
        >
          <v-select
            v-model="region"
            :items="importantSelectRegions"
            :label="$t('leaderboard.region')"
          />
        </v-col>

        <v-col
          cols="12"
          sm="4"
        >
          <v-checkbox
            v-model="isOnlyPros"
            :label="$t('leaderboard.onlyPros')"
          />
        </v-col>
      </v-row>

      <v-card-text v-if="filteredAccounts.length">
        <v-data-table
          :items="filteredAccounts"
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
              :to="`/account/${region}/${item.gameName}-${item.tagLine}`"
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
              v-if="item.player"
              style="cursor: pointer; text-decoration: none; color: inherit;"
              :to="`/player/${item.player.team}/${item.player.player}`"
            >
              {{ `${item.player.team} ${item.player.player}` }}
            </NuxtLink>
          </template>

          <template #item.totalGames="{item}">
            {{ item.wins + item.losses }}
          </template>

          <template #item.winRate="{item}">
            {{ (item.wins / (item.wins + item.losses) * 100).toFixed(2) }}%
          </template>
        </v-data-table>
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
