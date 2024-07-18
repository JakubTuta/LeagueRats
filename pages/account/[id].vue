<script setup lang="ts">
import type { IAccount } from '~/models/accountModel';
import { useAccountStore } from '~/stores/accountStore';

const route = useRoute()

const accountStore = useAccountStore()
const restStore = useRestStore()

const userDetails = String(route.params.id)
const gameName = userDetails.split('-')[0]
const tagLine = userDetails.split('-')[1]

const account = ref<IAccount | null>(null)
const currentGame = ref<any>(null)

onMounted(async () => {
  account.value = await accountStore.getAccountDetails(gameName, tagLine)
})

watch(account, async (newAccount) => {
  if (newAccount) {
    currentGame.value = await restStore.getCurrentGameByPuuid(newAccount.puuid)
  }
}, { immediate: true })
</script>

<template>
  <v-container>
    <v-card>
      <v-card-text>
        <v-btn
          :disabled="!currentGame"
          :color="currentGame
            ? 'primary'
            : ''"
        >
          {{ $t('profile.liveGame') }}

          <v-icon
            icon="mdi-menu-down"
            size="x-large"
            class="ml-2"
          />
        </v-btn>

        {{ currentGame }}
      </v-card-text>
    </v-card>
  </v-container>
</template>
