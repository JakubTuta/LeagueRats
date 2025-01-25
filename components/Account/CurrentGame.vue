<script setup lang="ts">
import { useDisplay } from 'vuetify'
import type { IAccount } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'

const props = defineProps<{
  currentGame: IActiveGame | null
  account: IAccount | null
  loading: boolean
}>()

const { currentGame, account, loading } = toRefs(props)

const { mdAndDown } = useDisplay()

function formatTime(time: number) {
  const minutes = Math.floor(time / 60)
  const seconds = time % 60

  return `${minutes}:${seconds < 10
? `0${seconds}`
: seconds}`
}

const interval = setInterval(() => {
  if (currentGame.value)
    currentGame.value.gameLength += 1
}, 1000)

onUnmounted(() => {
  clearInterval(interval)
})
</script>

<template>
  <v-card v-if="loading">
    <v-skeleton-loader
      type="card"
      width="80%"
      class="mx-auto my-8"
    />
  </v-card>

  <v-row
    v-else-if="account && !currentGame && !loading"
    class="text-h5 my-4"
    justify="center"
  >
    {{ $t('profile.currentGame.noGame', {"username": account.gameName}) }}
  </v-row>

  <v-card
    v-else-if="currentGame && account"
    elevation="0"
    class="my-2"
  >
    <v-card-title
      class="mx-4"
      :style="mdAndDown
        ? 'display: flex; flex-direction: column; align-items: start'
        : 'display: flex; justify-content: space-between; align-items: center'"
    >
      <div
        style="display: flex; justify-content: center; align-items: center"
        class="my-3"
      >
        <v-img
          v-if="currentGame.gameMode === 'CLASSIC'"
          class="mr-2"
          src="~/assets/classic_icon.png"
          lazy-src="~/assets/default.png"
          width="30"
          height="30"
        />

        <v-img
          v-else
          class="mr-2"
          src="~/assets/aram_icon.png"
          lazy-src="~/assets/default.png"
          width="30"
          height="30"
        />

        {{ $t(`game.${currentGame.gameMode.toLowerCase()}`) }}
        {{ $t(`queueTypes.${currentGame.gameQueueConfigId}`) }}
      </div>

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
