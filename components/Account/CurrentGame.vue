<script setup lang="ts">
import { useDisplay } from 'vuetify'
import type { IAccount } from '~/models/account'

const props = defineProps<{
  region: string
  gameName: string
  tagLine: string
  account: IAccount | null
}>()

const { region, gameName, tagLine, account } = toRefs(props)

const matchStore = useMatchStore()
const { mdAndDown } = useDisplay()

const currentGame = computed(() => matchStore.getActiveGameData(region.value, gameName.value, tagLine.value))
const loading = computed(() => matchStore.isActiveGameLoading(region.value, gameName.value, tagLine.value))

const intervalId = ref<number | null>(null)

function formatTime(time: number) {
  const minutes = Math.floor(time / 60)
  const seconds = time % 60

  return `${minutes}:${seconds < 10
    ? `0${seconds}`
    : seconds}`
}

watch(currentGame, (game) => {
  if (intervalId.value !== null) {
    clearInterval(intervalId.value)
    intervalId.value = null
  }

  if (game) {
    intervalId.value = setInterval(() => {
      if (currentGame.value) {
        currentGame.value.gameLength += 1
      }
    }, 1000) as unknown as number
  }
}, { immediate: true })

onUnmounted(() => {
  if (intervalId.value !== null) {
    clearInterval(intervalId.value)
  }
})
</script>

<template>
  <Loader v-if="loading" />

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
