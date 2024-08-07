<script setup lang="ts">
import type { IAccount } from '~/models/account';
import type { IActiveGame } from '~/models/activeGame';

const props = defineProps<{
  currentGame: IActiveGame | null
  account: IAccount | null
  loading: boolean
}>()

const { currentGame, account, loading } = toRefs(props)

function formatTime(time: number) {
  const minutes = Math.floor(time / 60)
  const seconds = time % 60

  return `${minutes}:${seconds < 10
? `0${seconds}`
: seconds}`
}

setInterval(() => {
  if (currentGame.value)
    currentGame.value.gameLength += 1
}, 1000)
</script>

<template>
  <v-row
    v-if="account && !currentGame && !loading"
    class="text-h5 my-4"
    justify="center"
  >
    {{ $t('profile.currentGame.noGame', {"username": account.gameName}) }}
  </v-row>

  <v-card
    v-else-if="currentGame && account"
    elevation="24"
    class="my-2"
  >
    <v-card-title
      style="display: flex; justify-content: space-between"
      class="mx-4"
    >
      {{ $t('profile.currentGame.usersGame', {"username": `${account.gameName} #${account.tagLine}`}) }}

      <v-spacer />

      {{ formatTime(currentGame.gameLength) }}
    </v-card-title>

    <v-card-text>
      <AccountGameTable
        :game="currentGame"
        :account="account"
      />
    </v-card-text>
  </v-card>
</template>
