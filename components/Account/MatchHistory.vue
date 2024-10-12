<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { mapKDAToColor } from '~/helpers/kdaColors'
import { queueTypes } from '~/helpers/queueTypes'
import type { IAccount } from '~/models/account'
import type { IMatchData } from '~/models/matchData'

interface IChampionHistory {
  championId: number
  games: number
  wins: number
  loses: number
  kills: number
  deaths: number
  assists: number
}

const props = defineProps<{
  account: IAccount | null
}>()

const { account } = toRefs(props)

const { t } = useI18n()
const { mobile } = useDisplay()

const storageStore = useStorageStore()
const { championIcons } = storeToRefs(storageStore)

const restStore = useRestStore()

const selectedTab = ref('SOLOQ')
const loading = ref(false)
const matchHistoryPerRegion = ref<Record<string, IMatchData[]>>({})
const canLoadMore = ref(true)

const tabs = computed(() => [
  { title: t('queueTypes.RANKED_SOLO_5x5'), value: 'SOLOQ' },
  { title: t('queueTypes.RANKED_FLEX_SR'), value: 'FLEXQ' },
  { title: t('queueTypes.NORMAL_DRAFT'), value: 'NORMAL' },
  { title: t('queueTypes.ARAM'), value: 'ARAM' },
])

watch(selectedTab, () => {
  getMatchHistory()
}, { immediate: true })

watch(account, () => {
  getMatchHistory()
}, { immediate: true })

async function getMatchIds(count: number) {
  if (!account.value)
    return []

  const requestQueueType = queueTypes[selectedTab.value]

  let lastLoadedMatchDate = new Date().getTime()

  if (matchHistoryPerRegion.value[selectedTab.value]?.length)
    lastLoadedMatchDate = matchHistoryPerRegion.value[selectedTab.value]?.[matchHistoryPerRegion.value[selectedTab.value]?.length - 1].info.gameStartTimestamp.seconds * 1000 || new Date().getTime()

  const optionalKeys = {
    count,
    queue: requestQueueType.id,
    type: requestQueueType.name,
    startTime: Math.floor(new Date(new Date().getFullYear(), 0, 1).getTime() / 1000),
    endTime: Math.floor(lastLoadedMatchDate / 1000),
  }

  const matchIds = await restStore.getAccountMatchHistory(account.value, optionalKeys)

  return matchIds
}

async function getMatchData(matchId: string) {
  const matchData = await restStore.getMatchData(matchId)

  return matchData
}

async function loadMatches(count: number = 20) {
  const matchIds = await getMatchIds(count)

  if (matchIds.length < count) {
    loading.value = false
    canLoadMore.value = false

    return []
  }

  const promises = matchIds.map(async matchId => await getMatchData(matchId))
  const matchData = await Promise.all(promises)

  return matchData
}

async function getMatchHistory() {
  if (!account.value || loading.value)
    return

  loading.value = true

  const matches = await loadMatches()

  if (!matchHistoryPerRegion.value[selectedTab.value])
    matchHistoryPerRegion.value[selectedTab.value] = []

  const sortedMatches = (matches.filter(item => item !== null
    && item.info.participants.length
    && !item.info.participants[0]?.gameEndedInEarlySurrender) as IMatchData[])
    .sort((a, b) => b.info.gameStartTimestamp.seconds - a.info.gameStartTimestamp.seconds)

  matchHistoryPerRegion.value[selectedTab.value].push(...sortedMatches)

  loading.value = false
}

// eslint-disable-next-line vue/no-side-effects-in-computed-properties
const last20Games = computed(() => matchHistoryPerRegion.value[selectedTab.value]
  ?.sort((a, b) => b.info.gameStartTimestamp.seconds - a.info.gameStartTimestamp.seconds)
  .slice(0, 20) || [])

const mapLast20Games = computed(() => {
  return last20Games.value
    .reduce((acc, game) => {
      const participant = game.info.participants.find(participant => account.value!.puuid.includes(participant.puuid))!

      storageStore.getChampionIcon(participant.championId)

      let champion = acc.find(champ => champ.championId === participant.championId)

      if (!champion) {
        champion = {
          championId: participant.championId,
          games: 0,
          wins: 0,
          loses: 0,
          kills: 0,
          deaths: 0,
          assists: 0,
        }
        acc.push(champion)
      }

      champion.games++
      champion.kills += participant.kills
      champion.deaths += participant.deaths
      champion.assists += participant.assists

      if (participant.win) {
        champion.wins++
      }
      else {
        champion.loses++
      }

      return acc
    }, [] as IChampionHistory[])
    .sort((a, b) => b.games - a.games)
})

function getKDA(champion: IChampionHistory) {
  const kda = (champion.kills + champion.assists) / champion.deaths

  return kda.toFixed(2)
}

function getWinRatio(champion: IChampionHistory) {
  const winRatio = champion.wins / champion.games

  return (winRatio * 100).toFixed(0)
}

const last20GamesWins = computed(() => last20Games.value.filter(game => game.info.participants.find(participant => account.value!.puuid.includes(participant.puuid))?.win).length)
const last20GamesLosses = computed(() => last20Games.value.filter(game => !game.info.participants.find(participant => account.value!.puuid.includes(participant.puuid))?.win).length)
</script>

<template>
  <v-tabs
    v-model="selectedTab"
    class="mt-4"
    density="compact"
    color="primary"
    align-tabs="center"
    grow
    :show-arrows="mobile"
  >
    <v-tab
      v-for="tab in tabs"
      :key="tab.value"
      :value="tab.value"
    >
      {{ tab.title }}
    </v-tab>
  </v-tabs>

  <v-card
    v-if="!loading && mapLast20Games.length"
    class="my-2"
  >
    <v-card-title>
      {{ $t('profile.matchHistory.lastGames') }}
    </v-card-title>

    <v-card-text>
      <v-row align="center">
        <v-col
          cols="12"
          sm="3"
          align="center"
        >
          <div>
            <PieChart
              :wins="last20GamesWins"
              :losses="last20GamesLosses"
            />
          </div>

          <p class="text-subtitle-2 mt-2 text-light-blue">
            {{ `${$t('profile.rank.wins')}: ${last20GamesWins}` }}
          </p>

          <p class="text-subtitle-2 text-red">
            {{ `${$t('profile.rank.losses')}: ${last20GamesLosses}` }}
          </p>

          <p class="text-subtitle-2 mt-1">
            {{ `${$t('profile.rank.winRate')}: ${(last20GamesWins / 20 * 100).toFixed(0)}%` }}
          </p>
        </v-col>

        <v-col
          cols="12"
          sm="9"
        >
          <div style="display: flex; overflow-x: auto; width: 100%">
            <div
              v-for="champion in mapLast20Games"
              :key="champion.championId"
              align="center"
              style="min-width: 100px"
            >
              <v-avatar
                size="50"
              >
                <v-img
                  :src="championIcons[champion.championId]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>

              <p class="text-subtitle-2">
                {{ `${$t('proPlayers.games')}: ${champion.games}` }}
              </p>

              <p class="text-subtitle-2">
                {{ getWinRatio(champion) }}%
              </p>

              <p :class="`text-subtitle-2 text-${mapKDAToColor(Number(getKDA(champion)))}`">
                {{ getKDA(champion) }}
              </p>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>

  <v-card v-if="!matchHistoryPerRegion[selectedTab]?.length && loading">
    <v-skeleton-loader
      type="card"
      width="90%"
      class="mx-auto my-8"
    />
  </v-card>

  <v-spacer class="my-4" />

  <AccountGameData
    v-for="match in matchHistoryPerRegion[selectedTab]"
    :key="match.metadata.matchId"
    class="mt-4"
    :account="account"
    :game="match"
  />

  <v-row
    v-if="canLoadMore"
    justify="center"
    class="mb-3 mt-6"
  >
    <v-btn
      color="primary"
      :loading="loading"
      stacked
      append-icon="mdi-chevron-down"
      size="small"
      @click="getMatchHistory"
    >
      {{ $t('profile.matchHistory.loadMore') }}
    </v-btn>
  </v-row>
</template>
