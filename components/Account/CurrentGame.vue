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
</template>
