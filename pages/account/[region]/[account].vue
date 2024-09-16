<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { selectRegions } from '~/helpers/regions'
import type { IAccount } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'
import type { IChampionMastery } from '~/models/championMastery'
import type { ILeagueEntry } from '~/models/leagueEntry'
import { useAccountStore } from '~/stores/accountStore'

const route = useRoute()
const router = useRouter()
const { mobile } = useDisplay()
const { t } = useI18n()

const accountStore = useAccountStore()
const restStore = useRestStore()

const loading = ref(false)
const tabLoading = ref(false)
const selectedTab = ref(0)
const region = ref('')
const account = ref<IAccount | null>(null)
const leagueEntry = ref<ILeagueEntry[]>([])
const matchHistory = ref<any[]>([])
const currentGame = ref<IActiveGame | null>(null)
const championMasteries = ref<IChampionMastery[]>([])

const tabs = computed(() => [
  { text: t('profile.rank.title'), value: 0 },
  { text: t('profile.matchHistory.title'), value: 1 },
  { text: t('profile.currentGame.title'), value: 2 },
  { text: t('profile.champions.title'), value: 3 },
])

const tabNumberToName: Record<number, string> = {
  0: 'rank',
  1: 'matchHistory',
  2: 'currentGame',
  3: 'champions',
}

const tabNameToNumber: Record<string, number> = {
  rank: 0,
  matchHistory: 1,
  currentGame: 2,
  champions: 3,
}

onMounted(async () => {
  let gameName = ''
  let tagLine = ''

  try {
    const paramsData = route.params as { region: string, account: string }
    region.value = paramsData.region.toUpperCase()
    const accountData = paramsData.account

    if (!accountData.includes('-'))
      throw new Error('Invalid account data')

    gameName = accountData.split('-')[0]
    tagLine = accountData.split('-')[1]
  }
  catch (error) {
    console.error(error)

    router.replace('/404')
  }

  if (!selectRegions.includes(region.value)) {
    router.push(`/search-account/${gameName}-${tagLine}`)
  }

  loading.value = true

  const response = await accountStore.getAccount(gameName, tagLine, region.value, true)

  if (!response) {
    router.push(`/search-account/${gameName}-${tagLine}`)

    return
  }

  account.value = response

  loading.value = false
})

onUnmounted(() => {
  loading.value = false
  tabLoading.value = false
  account.value = null
  leagueEntry.value = []
  matchHistory.value = []
  currentGame.value = null
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
      // replaceUrl(0)
      findLeagueEntry()
      break
    // case 1:
    //   replaceUrl(1)
    //   break
    case 2:
      // replaceUrl(2)
      findCurrentGame()
      break
    case 3:
      // replaceUrl(3)
      findChampions()
      break
  }
}

function replaceUrl(index: number) {
  const fullPath = router.currentRoute.value.fullPath.split('/')

  const accountIndex = fullPath.findIndex(value => value === 'account')
  const subPageIndex = accountIndex + 3

  if (accountIndex === -1 || fullPath.length > subPageIndex)
    return

  if (!fullPath[subPageIndex]) {
    fullPath[subPageIndex] = tabNumberToName[index]
  }
  else {
    fullPath.push(tabNumberToName[index])
  }

  router.replace(fullPath.join('/'))
}

async function findLeagueEntry() {
  if (!account.value || leagueEntry.value.length)
    return

  tabLoading.value = true
  leagueEntry.value = await restStore.getLeagueEntryBySummonerId(account.value.id, region.value)
  tabLoading.value = false
}

async function findCurrentGame() {
  if (!account.value || currentGame.value)
    return

  tabLoading.value = true
  const response = await restStore.getCurrentGameByPuuid(account.value.puuid, region.value)
  currentGame.value = response
  tabLoading.value = false
}

async function findChampions() {
  if (!account.value || championMasteries.value.length)
    return

  tabLoading.value = true
  championMasteries.value = await restStore.getChampionMasteryByPuuid(account.value.puuid, region.value)
  tabLoading.value = false
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
          :loading="tabLoading"
        />

        <AccountMatchHistory
          v-if="selectedTab === 1"
          :account="account"
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
          :loading="tabLoading"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>
