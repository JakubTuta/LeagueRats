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

async function getAccountDetails(gameName: string, tagLine: string) {
  loading.value = true

  const databaseAccountDetails = await accountStore.getAccountDetails(gameName, tagLine)

  if (databaseAccountDetails) {
    return databaseAccountDetails
  }

  const apiAccountDetails = await restStore.getAccountDetailsByRiotId(gameName, tagLine)

  if (apiAccountDetails) {
    accountStore.saveAccount(apiAccountDetails)

    return apiAccountDetails
  }

  loading.value = false

  return null
}

onMounted(async () => {
  const userDetails = String(route.params.id)
  const gameName = userDetails.split('-')[0]
  const tagLine = userDetails.split('-')[1]

  account.value = await getAccountDetails(gameName, tagLine)
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

  if (response && response.gameMode === 'CLASSIC') {
    currentGame.value = response

    isShowCurrentGamePanel.value = true
  }

  currentGameLoading.value = false
}
</script>

<template>
  <v-container>
    <v-card>
      <v-card-text>
        <v-btn
          :loading="currentGameLoading"
          :color="currentGame
            ? 'primary'
            : ''"
          @click="handleCurrentGameButton"
        >
          {{ $t('profile.currentGame.title') }}

          <v-icon
            icon="mdi-menu-down"
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
