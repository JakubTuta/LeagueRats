<script setup lang="ts">
import { fullUrl } from '~/helpers/url'
import type { IProActiveGame } from '~/models/proActiveGame'
import type { IProPlayer } from '~/models/proPlayer'

const proStore = useProPlayerStore()
const { activeGames, liveStreams } = storeToRefs(proStore)

const storageStore = useStorageStore()

const refreshTime = ref('00:00')

const playersPerSlide = 3

setInterval(getNextUpdateTime, 1000)

onMounted(() => {
  proStore.getActiveProGamesFromDatabase()
})

const filteredGames = computed(() => activeGames.value.filter((game, index, self) => index === self.findIndex(g => g.player.player === game.player.player)))

const shuffledGames = computed(() => {
  const copiedArray = filteredGames.value.map(game => game)

  for (let i = copiedArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copiedArray[i], copiedArray[j]] = [copiedArray[j], copiedArray[i]]
  }

  return copiedArray
})

const splitProGames = computed(() => {
  if (!filteredGames.value)
    return []

  const result = []
  let i = 0

  while (i < shuffledGames.value.length) {
    const end = Math.min(i + playersPerSlide, shuffledGames.value.length)
    result.push(shuffledGames.value.slice(i, end))
    i += playersPerSlide
  }

  return result
})

function getNextUpdateTime() {
  const now = new Date()
  const nextUpdate = new Date(now)

  const minutes = now.getMinutes()
  const nextMinutes = minutes % 10 === 0
    ? minutes + 10
    : Math.ceil(minutes / 10) * 10

  if (nextMinutes === 60) {
    nextUpdate.setHours(now.getHours() + 1)
    nextUpdate.setMinutes(0)
  }
  else {
    nextUpdate.setMinutes(nextMinutes)
  }

  nextUpdate.setSeconds(0)

  const diff = nextUpdate.getTime() - now.getTime()

  const minutesDiff = String(Math.floor(diff / 60000)).padStart(2, '0')
  const secondsDiff = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0')

  refreshTime.value = `${minutesDiff}:${secondsDiff}`
}

function goToPlayerAccount(game: IProActiveGame) {
  return `/account/${game.account.region}/${game.account.gameName}-${game.account.tagLine}`
}

function getTimeDiff(game: IProActiveGame) {
  const now = new Date()
  const gameDate = new Date(game.gameStartTime.toDate())

  const diff = now.getTime() - gameDate.getTime()

  const minutesDiff = String(Math.floor(diff / 60000)).padStart(2, '0')
  const secondsDiff = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0')

  return `${minutesDiff}:${secondsDiff}`
}

function getPlayerStream(player: IProPlayer) {
  const stream = liveStreams.value[player.player] || null

  return stream
    ? stream.twitch
    : null
}
</script>

<template>
  <v-card
    color="rgba(50, 50, 50, 0.9)"
    height="300px"
  >
    <v-card-text
      v-if="!filteredGames.length"
      style="height: 100%"
    >
      {{ $t('index.nextUpdate', {"time": refreshTime}) }}

      <span style="display: flex; align-items: center; justify-content: center; height: 90%">
        {{ $t('index.noActiveGames') }}
      </span>
    </v-card-text>

    <v-card-text v-else>
      {{ $t('index.nextUpdate', {"time": refreshTime}) }}
      <v-carousel
        class="mt-1"
        interval="10000"
        cycle
        hide-delimiters
        height="250"
        :show-arrows="filteredGames.length > playersPerSlide"
      >
        <v-carousel-item
          v-for="(games, index) in splitProGames"
          :key="index"
        >
          <v-row
            :class="filteredGames.length > playersPerSlide
              ? 'mx-15'
              : ''"
          >
            <v-col
              v-for="game in games"
              :key="game.participant.puuid"
              cols="4"
            >
              <v-card
                align="center"
                style="height: 250px"
                :ripple="false"
                :to="goToPlayerAccount(game)"
                color="rgba(50, 50, 50, 0.9)"
              >
                <v-card-text style="height: 100%; display: flex; flex-direction: column; justify-content: space-between">
                  <NuxtLink
                    v-if="getPlayerStream(game.player)"
                    external
                    :to="`${fullUrl.twitch}/${getPlayerStream(game.player)}`"
                    @click.stop
                  >
                    <v-avatar
                      style="position: absolute; top: 5px; left: 5px;"
                      size="50"
                      rounded="0"
                      variant="flat"
                    >
                      <v-badge
                        dot
                        color="red"
                      >
                        <v-icon
                          size="40"
                          icon="mdi-twitch"
                          color="secondary"
                        />

                        <v-tooltip
                          activator="parent"
                          location="bottom"
                        >
                          {{ $t('proPlayers.isLive', {"player": game.player.player}) }}
                        </v-tooltip>
                      </v-badge>
                    </v-avatar>
                  </NuxtLink>

                  <span style="position: absolute; top: 10px; right: 10px;">
                    {{ getTimeDiff(game) }}
                  </span>

                  <div>
                    <v-avatar
                      size="80"
                    >
                      <v-img
                        lazy-src="~/assets/default.png"
                        :src="storageStore.getPlayerImage(game.player.player)"
                      />
                    </v-avatar>

                    <p class="mt-1">
                      {{ `${game.player.team} ${game.player.player}` }}
                    </p>
                  </div>

                  <div>
                    <v-avatar
                      size="40"
                    >
                      <v-img
                        lazy-src="~/assets/default.png"
                        :src="storageStore.getChampionIcon(game.participant.championId)"
                      />
                    </v-avatar>
                  </div>

                  <div>
                    <p
                      class="text-subtitle-2 text-gray"
                      style="margin-top: auto"
                    >
                      {{ game.account.region }}
                    </p>

                    <p>
                      {{ game.participant.riotId.split('#')[0] || '' }}
                      <span class="text-gray">
                        {{ ` #${game.participant.riotId.split('#')[1] || ''}` }}
                      </span>
                    </p>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-carousel-item>
      </v-carousel>
    </v-card-text>
  </v-card>
</template>
