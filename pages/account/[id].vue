<script setup lang="ts">
import type { IAccount } from '~/models/account'
import { mapAccount } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'
import type { ILeagueEntry } from '~/models/leagueEntry'
import { useAccountStore } from '~/stores/accountStore'

const route = useRoute()

const accountStore = useAccountStore()
const restStore = useRestStore()

const loading = ref(false)
const account = ref<IAccount | null>(null)
const currentGame = ref<IActiveGame | null>(null)
const currentGameLoading = ref(false)
const isShowCurrentGamePanel = ref(false)
const gameNotFound = ref(false)
const accountNotFound = ref(false)
const leagueEntry = ref<ILeagueEntry | null>(null)

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
  clearValues()
})

watch(account, async (newAccount) => {
  if (newAccount) {
    leagueEntry.value = await restStore.getLeagueEntryBySummonerId(newAccount.id)
  }
})

function clearValues() {
  account.value = null
  currentGame.value = null
  currentGameLoading.value = false
  isShowCurrentGamePanel.value = false
  gameNotFound.value = false
  accountNotFound.value = false
}

async function handleCurrentGameButton() {
  if (isShowCurrentGamePanel.value) {
    isShowCurrentGamePanel.value = false

    return
  }

  if (!account.value)
    return

  currentGameLoading.value = true

  if (currentGame.value) {
    isShowCurrentGamePanel.value = true
    currentGameLoading.value = false
  }

  const response = await restStore.getCurrentGameByPuuid(account.value.puuid)

  if (response && (response.gameMode === 'CLASSIC' || response.gameMode === 'ARAM')) {
    currentGame.value = response

    gameNotFound.value = false
    isShowCurrentGamePanel.value = true
  }
  else {
    gameNotFound.value = true
  }

  currentGameLoading.value = false
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
        class="my-4"
      >
        {{ account?.gameName || '' }}

        <span class="test-subtitle-1 ml-1 text-gray">
          #{{ account?.tagLine || '' }}
        </span>
      </v-card-title>

      <v-card-text>
        <v-row class="ma-2">
          <v-btn
            v-if="!gameNotFound"
            color="primary"
            :loading="currentGameLoading"
            @click="handleCurrentGameButton"
          >
            {{ $t('profile.currentGame.title') }}

            <v-icon
              icon="mdi-menu-down"
              size="x-large"
              class="ml-2"
            />
          </v-btn>

          <v-btn
            v-else
            v-tooltip="$t('profile.currentGame.gameNotFound')"
            color="disabled"
            :loading="currentGameLoading"
            @click="handleCurrentGameButton"
          >
            {{ $t('profile.currentGame.title') }}

            <v-icon
              icon="mdi-refresh"
              size="x-large"
              class="ml-2"
            />
          </v-btn>

          <AccountCurrentGame
            v-if="isShowCurrentGamePanel"
            :current-game="currentGame"
            :account="account"
          />
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>
