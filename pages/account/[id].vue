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

const tabs = computed(() => [
  { text: t('profile.rank.title'), value: 0 },
  { text: t('profile.currentGame.title'), value: 1 },
  { text: t('profile.champions.title'), value: 2 },
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

watch(account, async (newAccount) => {
  if (newAccount) {
    tabLoading.value = true
    leagueEntry.value = await restStore.getLeagueEntryBySummonerId(newAccount.id)
    tabLoading.value = false
  }
})

watch(selectedTab, (newTab) => {
  if (newTab === 1) {
    findCurrentGame()
  }
  else if (newTab === 2) {
    findChampions()
  }
}, { immediate: true })

async function findCurrentGame() {
  if (!account.value || currentGame.value)
    return

  const response = await restStore.getCurrentGameByPuuid(account.value.puuid)

  if (response)
    currentGame.value = response
  else
    gameNotFound.value = true
}

async function findChampions() {
  if (!account.value || championMasteries.value.length)
    return

  championMasteries.value = await restStore.getChampionMasteryByPuuid(account.value.puuid)
}
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

        <AccountCurrentGame
          v-if="selectedTab === 1"
          :current-game="currentGame"
          :account="account"
          :loading="tabLoading"
        />

        <AccountChampions
          v-if="selectedTab === 2"
          :champions="championMasteries"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>
