<script setup lang="ts">
import type { IAccount } from '~/models/account';
import type { IActiveGame } from '~/models/activeGame';

const props = defineProps<{
  currentGame: IActiveGame | null
  account: IAccount | null
  loading: boolean
}>()

const { currentGame, account, loading } = toRefs(props)
</script>

<template>
  <v-card
    v-if="currentGame && account"
    elevation="24"
    class="my-2"
  >
    <v-card-title>
      {{ $t('profile.currentGame.usersGame', {"username": `${account.gameName} #${account.tagLine}`}) }}
    </v-card-title>

    <v-card-text>
      <AccountGameTable
        :game="currentGame"
        :account="account"
      />
    </v-card-text>
  </v-card>

  <v-card v-else-if="account && !currentGame && !loading">
    <v-card-title>
      {{ $t('profile.currentGame.noGame', {"username": account.gameName}) }}
    </v-card-title>
  </v-card>
</template>
