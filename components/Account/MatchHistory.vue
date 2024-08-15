<script setup lang="ts">
import { useDisplay } from 'vuetify';
import { queueTypes } from '~/helpers/queueTypes';
import type { IAccount } from '~/models/account';
import type { IMatchData } from '~/models/matchData';

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

async function getMatchHistory() {
  if (!account.value || loading.value || matchHistoryPerRegion.value[selectedTab.value])
    return

  loading.value = true

  const requestQueueType = queueTypes[selectedTab.value]

  const optionalKeys = {
    count: 2,
    queue: requestQueueType.id,
    type: requestQueueType.name,
  }

  const matchIds = await restStore.getAccountMatchHistory(account.value, optionalKeys)

  if (!matchIds.length) {
    loading.value = false

    return
  }

  const promises = matchIds.map(async (matchId) => {
    const matchData = await restStore.getMatchData(matchId)

    return matchData
  })

  const matchData = await Promise.all(promises)

  matchHistoryPerRegion.value[selectedTab.value] = matchData.filter(item => item !== null)

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

  <v-card v-if="loading">
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
    class="mb-4"
    :account="account"
    :game="match"
  />
</template>
