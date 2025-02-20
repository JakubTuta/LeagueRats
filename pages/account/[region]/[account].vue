<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { selectRegions } from '~/helpers/regions'
import type { IAccount } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'
import type { IChampionMastery } from '~/models/championMastery'
import type { ILeagueEntry } from '~/models/leagueEntry'
import { useLeagueStore } from '~/stores/leagueStore'
import { useMatchStore } from '~/stores/matchStore'

const route = useRoute()
const router = useRouter()
const { mobile } = useDisplay()
const { t } = useI18n()

const accountStore = useAccountStore()
const leagueStore = useLeagueStore()
const matchStore = useMatchStore()
const championStore = useChampionStore()
const storageStore = useStorageStore()

const proStore = useProPlayerStore()
const { proAccountNames } = storeToRefs(proStore)

const appStore = useAppStore()
const { loading: appLoading } = storeToRefs(appStore)

const loading = ref(false)
const rankLoading = ref(false)
const gamesLoading = ref(false)
const liveGameLoading = ref(false)
const championsLoading = ref(false)
const selectedTab = ref(0)
const region = ref('')
const account = ref<IAccount | null>(null)
const leagueEntry = ref<ILeagueEntry[]>([])
const matchHistory = ref<any[]>([])
const currentGame = ref<IActiveGame | null>(null)
const championMasteries = ref<IChampionMastery[]>([])

const proPlayer = ref<{ team: string, player: string } | null>(null)
const isShowTeamDialog = ref(false)
const selectedTeam = ref('')

const tabs = computed(() => [
  { text: t('profile.rank.title'), value: 0 },
  { text: t('profile.matchHistory.title'), value: 1 },
  { text: t('profile.currentGame.title'), value: 2 },
  { text: t('profile.champions.title'), value: 3 },
])

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
    router.push('/404')
  }

  if (!selectRegions.includes(region.value)) {
    router.push(`/search-account/${gameName}-${tagLine}`)
  }

  loading.value = true

  const response = await accountStore.getAccount({ username: gameName, tag: tagLine, region: region.value })

  if (!response) {
    router.push(`/search-account/${gameName}-${tagLine}`)

    return
  }

  account.value = response

  loadTabs()

  loading.value = false
})

onUnmounted(() => {
  loading.value = false
  rankLoading.value = false
  gamesLoading.value = false
  liveGameLoading.value = false
  championsLoading.value = false
  account.value = null
  leagueEntry.value = []
  matchHistory.value = []
  currentGame.value = null
  championMasteries.value = []
})

watch(account, () => {
  handleTabData()
  checkIfAccountIsPro()
}, { immediate: true })

watch(selectedTab, () => {
  handleTabData()
}, { immediate: true })

watch(isShowTeamDialog, (value) => {
  if (!value)
    selectedTeam.value = ''
})

function loadTabs() {
  findLeagueEntry()
  findCurrentGame()
  findChampions()
}

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

function checkIfAccountIsPro() {
  if (!account.value?.puuid || !proAccountNames.value)
    return

  proPlayer.value = proAccountNames.value[account.value.puuid] || null
}

async function findLeagueEntry() {
  if (!account.value || leagueEntry.value.length)
    return

  rankLoading.value = true
  leagueEntry.value = await leagueStore.getLeagueEntry(account.value.puuid)
  rankLoading.value = false
}

async function findCurrentGame() {
  if (!account.value || currentGame.value)
    return

  liveGameLoading.value = true
  currentGame.value = await matchStore.getActiveMatch(account.value.puuid)
  liveGameLoading.value = false
}

async function findChampions() {
  if (!account.value || championMasteries.value.length)
    return

  championsLoading.value = true
  championMasteries.value = await championStore.getChampionMastery(account.value.puuid)
  championsLoading.value = false
}
</script>

<template>
  <v-container>
    <Loader v-if="loading || appLoading" />

    <v-card
      v-else
      rounded="shaped"
    >
      <v-card-title
        align="center"
        class="text-h5 my-4"
      >
        <p
          v-if="proPlayer"
          class="mb-1"
        >
          <v-avatar size="100">
            <v-img
              :src="storageStore.getPlayerImage(proPlayer.player)"
              lazy-src="~/assets/default.png"
            />
          </v-avatar>
        </p>

        <p
          v-if="proPlayer"
          class="text-subtitle-1 mb-2"
        >
          <NuxtLink
            class="text-blue"
            style="cursor: pointer; text-decoration: none; color: inherit;"
            :to="`/team/${proPlayer.team}`"
          >
            {{ `[${proPlayer.team}]` }}
          </NuxtLink>

          {{ proPlayer.player }}
        </p>

        {{ account?.gameName || '' }}

        <span class="text-gray font-italic">
          #{{ account?.tagLine || '' }}
        </span>
      </v-card-title>

      <v-tabs
        v-if="!loading"
        v-model="selectedTab"
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
          {{ tab.text }}
        </v-tab>
      </v-tabs>

      <v-card-text v-if="!loading">
        <AccountRank
          v-if="selectedTab === 0"
          :league-entries="leagueEntry"
          :loading="rankLoading"
        />

        <AccountMatchHistory
          v-if="selectedTab === 1"
          :account="account"
        />

        <AccountCurrentGame
          v-if="selectedTab === 2"
          :current-game="currentGame"
          :account="account"
          :loading="liveGameLoading"
        />

        <AccountChampions
          v-if="selectedTab === 3"
          :account="account"
          :champions="championMasteries"
          :loading="championsLoading"
        />
      </v-card-text>
    </v-card>
  </v-container>

  <AccountProTeam
    v-model:is-show="isShowTeamDialog"
    :team="selectedTeam"
  />
</template>
