<script setup lang="ts">
import { useDisplay } from 'vuetify'
import type { IAccount } from '~/models/account'
import { mapAccount } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'
import type { IChampionMastery } from '~/models/championMastery'
import type { ILeagueEntry } from '~/models/leagueEntry'
import { useAccountStore } from '~/stores/accountStore'

const route = useRoute()
const { mobile } = useDisplay()
const { t } = useI18n()

const accountStore = useAccountStore()
const restStore = useRestStore()

const loading = ref(false)
const account = ref<IAccount | null>(null)
const currentGame = ref<IActiveGame | null>(null)
const tabLoading = ref(false)
const gameNotFound = ref(false)
const accountNotFound = ref(false)
const leagueEntry = ref<ILeagueEntry[]>([])
const selectedTab = ref(0)
const championMasteries = ref<IChampionMastery[]>([])
const matchHistory = ref<any[]>([])
const matchHistoryNotFound = ref(false)

const tabs = computed(() => [
  { text: t('profile.rank.title'), value: 0 },
  { text: t('profile.matchHistory.title'), value: 1 },
  { text: t('profile.currentGame.title'), value: 2 },
  { text: t('profile.champions.title'), value: 3 },
])

onMounted(async () => {
  const userDetails = String(route.params.id)
  const gameName = userDetails.split('-')[0]
  const tagLine = userDetails.split('-')[1]

  loading.value = true
  const tmpAccount = await accountStore.findAccount(gameName, tagLine)

  if (tmpAccount) {
    account.value = tmpAccount
    loading.value = false

    return
  }

  const accountDetails = await restStore.getAccountDetailsByRiotId(gameName, tagLine)

  if (!accountDetails) {
    accountNotFound.value = true
    loading.value = false

    return
  }

  const summonerDetails = await restStore.getSummonerDetailsByPuuid(accountDetails.puuid)

  if (!summonerDetails) {
    accountNotFound.value = true
    loading.value = false

    return
  }

  account.value = mapAccount(accountDetails, summonerDetails)
  accountStore.saveAccount(account.value)

  loading.value = false
})

onUnmounted(() => {
  account.value = null
  currentGame.value = null
  tabLoading.value = false
  gameNotFound.value = false
  accountNotFound.value = false
  leagueEntry.value = []
  selectedTab.value = 0
  championMasteries.value = []
})

watch(account, () => {
  handleTabData()
}, { immediate: true })

watch(selectedTab, () => {
  handleTabData()
}, { immediate: true })

function handleTabData() {
  switch (selectedTab.value) {
    case 0:
      findLeagueEntry()
      break
    case 1:
      findMatchHistory()
      break
    case 2:
      findCurrentGame()
      break
    case 3:
      findChampions()
      break
  }
}

async function findLeagueEntry() {
  if (!account.value || leagueEntry.value.length)
    return

  tabLoading.value = true
  leagueEntry.value = await restStore.getLeagueEntryBySummonerId(account.value.id)
  tabLoading.value = false
}

async function findMatchHistory() {
  if (!account.value)
    return

  const optionalKeys = {
    count: 5,
  }

  tabLoading.value = true
  matchHistory.value = await restStore.getMatchHistoryByPuuid(account.value.puuid, optionalKeys)
  tabLoading.value = false

  if (!matchHistory.value.length)
    matchHistoryNotFound.value = true
}

async function findCurrentGame() {
  if (!account.value || currentGame.value)
    return

  tabLoading.value = true
  const response = await restStore.getCurrentGameByPuuid(account.value.puuid)
  tabLoading.value = false

  if (response)
    currentGame.value = response
  else
    gameNotFound.value = true
}

async function findChampions() {
  if (!account.value || championMasteries.value.length)
    return

  tabLoading.value = true
  championMasteries.value = await restStore.getChampionMasteryByPuuid(account.value.puuid)
  tabLoading.value = false
}

// async function endTabLoading() {
//   await sleep(500)
//   tabLoading.value = false
// }
</script>

<template>
  <v-container>
    <v-card v-if="loading">
      <v-skeleton-loader
        type="card"
        width="90%"
        class="mx-auto my-16"
      />
    </v-card>

    <v-card v-else>
      <v-card-title
        align="center"
        class="text-h5 my-4"
      >
        {{ account?.gameName || '' }}

        <span class="ml-1 text-gray font-italic">
          #{{ account?.tagLine || '' }}
        </span>
      </v-card-title>

      <v-tabs
        v-model="selectedTab"
        color="primary"
        align-tabs="center"
        grow
        :show-arrows="mobile"
        :items="tabs"
      />

      <v-card-text>
        <v-card v-if="tabLoading">
          <v-skeleton-loader
            type="card"
            width="90%"
            class="mx-auto my-8"
          />
        </v-card>

        <AccountRank
          v-if="selectedTab === 0"
          :league-entries="leagueEntry"
        />

        <AccountMatchHistory
          v-if="selectedTab === 1"
          :match-ids="matchHistory"
        />

        <AccountCurrentGame
          v-if="selectedTab === 2"
          :current-game="currentGame"
          :account="account"
          :loading="tabLoading"
        />

        <AccountChampions
          v-if="selectedTab === 3"
          :champions="championMasteries"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>
