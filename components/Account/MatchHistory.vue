<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { mapKDAToColor } from '~/helpers/kdaColors'
import { queueTypes } from '~/helpers/queueTypes'
import type { IAccount } from '~/models/account'
import type { IMatchData } from '~/models/matchData'
import { useMatchStore } from '~/stores/matchStore'

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
const matchStore = useMatchStore()

const selectedTab = ref('SOLOQ')
const loading = ref(false)
const matchHistoryPerRegion = ref<Record<string, IMatchData[]>>({
  SOLOQ: [] as IMatchData[],
  FLEXQ: [] as IMatchData[],
  NORMAL: [] as IMatchData[],
  ARAM: [] as IMatchData[],
})
const canLoadMore = ref(true)
const loadedFirstBatch = ref(false)

const matchAmount = 10

const tabs = computed(() => [
  { title: t('queueTypes.RANKED_SOLO_5x5'), value: 'SOLOQ' },
  { title: t('queueTypes.RANKED_FLEX_SR'), value: 'FLEXQ' },
  { title: t('queueTypes.NORMAL_DRAFT'), value: 'NORMAL' },
  { title: t('queueTypes.ARAM'), value: 'ARAM' },
])

watch(selectedTab, () => {
  getMatchHistory()
})

watch(account, () => {
  getMatchHistory()
}, { immediate: true })

async function loadMatches(count: number = matchAmount) {
  if (!account.value)
    return

  loading.value = true

  const requestQueueType = queueTypes[selectedTab.value]

  let lastLoadedMatchDate = new Date().getTime()

  const matches = matchHistoryPerRegion.value[selectedTab.value]
  if (matches.length)
    lastLoadedMatchDate = matches[matches.length - 1].info.gameStartTimestamp.seconds * 1000 || new Date().getTime()

  const optionalKeys = {
    count,
    queue: requestQueueType.id,
    type: requestQueueType.name,
    startTime: Math.floor(new Date('2021-06-16').getTime() / 1000),
    endTime: Math.floor(lastLoadedMatchDate / 1000),
  }

  const matchesData = await matchStore.getMatchHistoryBatch(account.value.puuid, account.value.region.toUpperCase(), optionalKeys)

  matchHistoryPerRegion.value[selectedTab.value].push(...matchesData)

  if (matchesData.length < count) {
    canLoadMore.value = false
  }

  loading.value = false
  loadedFirstBatch.value = true
}

function getMatchHistory() {
  if (!account.value || loading.value)
    return

  if (matchHistoryPerRegion.value[selectedTab.value].length === 0) {
    canLoadMore.value = true
  }

  loadMatches()
}

const processedGames = computed(() => {
  return matchHistoryPerRegion.value[selectedTab.value]
    .filter(match => match.info.participants.length && !match.info.participants[0].gameEndedInEarlySurrender)
    .sort((a, b) => b.info.gameStartTimestamp.seconds - a.info.gameStartTimestamp.seconds)
})

const mapLastGames = computed(() => {
  return processedGames.value
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

const lastGamesWins = computed(() => processedGames.value.reduce((acc, game) => acc + (game.info.participants.find(participant => account.value!.puuid.includes(participant.puuid))?.win
  ? 1
  : 0), 0))
const lastGamesLosses = computed(() => processedGames.value.reduce((acc, game) => acc + (!game.info.participants.find(participant => account.value!.puuid.includes(participant.puuid))?.win
  ? 1
  : 0), 0))
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
    v-if="mapLastGames.length && loadedFirstBatch"
    class="my-2"
  >
    <v-card-title>
      {{ $t('profile.matchHistory.lastGames', {"games": lastGamesWins + lastGamesLosses}) }}
    </v-card-title>

    <v-card-text>
      <v-row
        align="center"
      >
        <v-col
          cols="12"
          sm="3"
          align="center"
        >
          <div>
            <PieChart
              :wins="lastGamesWins"
              :losses="lastGamesLosses"
              :size="100"
            />
          </div>

          <p class="text-subtitle-2 mt-2 text-light-blue">
            {{ `${$t('profile.rank.wins')}: ${lastGamesWins}` }}
          </p>

          <p class="text-subtitle-2 text-red">
            {{ `${$t('profile.rank.losses')}: ${lastGamesLosses}` }}
          </p>

          <p class="text-subtitle-2 mt-1">
            {{ `${$t('profile.rank.winRate')}: ${(lastGamesWins / 10 * 100).toFixed(0)}%` }}
          </p>
        </v-col>

        <v-col
          cols="12"
          sm="9"
        >
          <div style="display: flex; overflow-x: auto; width: 100%">
            <div
              v-for="champion in mapLastGames"
              :key="champion.championId"
              align="center"
              style="min-width: 80px"
            >
              <v-avatar
                size="50"
              >
                <v-img
                  :src="storageStore.getChampionIcon(champion.championId) || ''"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>

              <p class="text-subtitle-2 mt-1">
                {{ champion.games }}
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

  <v-spacer class="my-4" />

  <AccountGameData
    v-for="match in processedGames"
    :key="match.metadata.matchId"
    class="mt-4"
    :account="account"
    :game="match"
  />

  <div v-if="loading && loadedFirstBatch">
    <v-skeleton-loader
      v-for="n in matchAmount"
      :key="n"
      class="my-4"
      type="image"
    />
  </div>

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
