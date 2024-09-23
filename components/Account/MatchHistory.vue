<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { queueTypes } from '~/helpers/queueTypes'
import type { IAccount } from '~/models/account'
import type { IMatchData } from '~/models/matchData'

const props = defineProps<{
  account: IAccount | null
}>()

const { account } = toRefs(props)

const { t } = useI18n()
const { mobile } = useDisplay()

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

async function loadMatches(count: number = 10) {
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

  <v-card v-if="!matchHistoryPerRegion[selectedTab].length && loading">
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
