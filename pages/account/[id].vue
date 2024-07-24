<script setup lang="ts">
import type { IAccount } from '~/models/accountModel';
import type { ActiveGameModel } from '~/models/activeGame';
import { useAccountStore } from '~/stores/accountStore';

const route = useRoute()

const accountStore = useAccountStore()
const restStore = useRestStore()

const loading = ref(false)
const account = ref<IAccount | null>(null)
const currentGame = ref<ActiveGameModel | null>(null)
const currentGameLoading = ref(false)
const isShowCurrentGamePanel = ref(false)
const gameNotFound = ref(false)

async function getAccountDetails(gameName: string, tagLine: string) {
  const databaseAccountDetails = await accountStore.getAccountDetails(gameName, tagLine)

  if (databaseAccountDetails) {
    return databaseAccountDetails
  }

  const apiAccountDetails = await restStore.getAccountDetailsByRiotId(gameName, tagLine)

  if (apiAccountDetails) {
    accountStore.saveAccount(apiAccountDetails)

    return apiAccountDetails
  }

  return null
}

onMounted(async () => {
  const userDetails = String(route.params.id)
  const gameName = userDetails.split('-')[0]
  const tagLine = userDetails.split('-')[1]

  loading.value = true
  account.value = await getAccountDetails(gameName, tagLine)
  loading.value = false
})

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
      </v-card-text>
    </v-card>
  </v-container>
</template>
