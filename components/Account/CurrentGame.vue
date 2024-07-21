<script setup lang="ts">
import type { IAccount } from '~/models/accountModel';
import type { ActiveGameModel } from '~/models/activeGame';

const props = defineProps<{
  currentGame: ActiveGameModel | null
  account: IAccount | null
}>()

const { currentGame, account } = toRefs(props)
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
</template>
