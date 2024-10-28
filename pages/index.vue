<script setup lang="ts">
import { useDisplay } from 'vuetify'
// @ts-expect-error correct path
import logo from '~/assets/logo.png'
import { selectRegions, teamPerRegion } from '~/helpers/regions'
import { lengthRule } from '~/helpers/rules'
import { fullUrl } from '~/helpers/url'
import type { IProActiveGame } from '~/models/proActiveGame'
import type { IProPlayer } from '~/models/proPlayer'

const { t } = useI18n()
const router = useRouter()
const { mobile } = useDisplay()

const proStore = useProPlayerStore()
const { activeGames, liveStreams, proAccountNames } = storeToRefs(proStore)

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const storageStore = useStorageStore()
const { championIcons, teamImages } = storeToRefs(storageStore)

const championStore = useChampionStore()
const { champions } = storeToRefs(championStore)

useSummonerSpellsStore()

const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const region = ref('EUW')
const refreshTime = ref('00:00')
const search = ref('')

const playersPerSlide = 3

const errorMessage = t('rules.requiredField')

onMounted(() => {
  if (mobile.value)
    return

  proStore.getActiveProGamesFromDatabase()

  proStore.getLiveStreams()
  proStore.getNotLiveStreams()

  if (!Object.keys(champions.value).length)
    championStore.getChampions()

  if (!proAccountNames.value)
    proStore.getProAccountNames()

  storageStore.getAllChampionIcons()
})

onUnmounted(() => {
  clearValues()
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

const regions = computed(() => {
  return selectRegions.map((region) => {
    return {
      title: t(`regions.${region.toLowerCase()}`),
      value: region,
    }
  })
})

const sortedChampions = computed(() => {
  return Object.entries(champions.value).sort((a, b) => {
    return a[1].value.localeCompare(b[1].value, 'en', { sensitivity: 'base' })
  }).map(item => ({ id: item[0], title: item[1].title, value: item[1].value }))
})

const searchItems = computed(() => {
  const championItems = sortedChampions.value.map((champion) => {
    return {
      title: champion.title,
      value: champion.value,
      isChampion: true,
      id: champion.id,
    }
  })

  if (!proAccountNames.value)
    return championItems

  const uniqueProPlayers = Object.values(proAccountNames.value).filter((player, index, self) => index === self.findIndex(p => p.player === player.player))

  const proPlayerItems = uniqueProPlayers.map((player) => {
    return {
      title: `${player.team} ${player.player}`,
      value: `${player.team.toLowerCase()} ${player.player.toLowerCase()}`,
      isChampion: false,
      team: player.team,
      player: player.player,
      region: player.region,
    }
  })

  return [...championItems, ...proPlayerItems]
})

const filteredSearchItems = computed(() => {
  if (!search.value)
    return []

  const filteredItems = searchItems.value
    .filter(item => item.value.toLowerCase().includes(search.value.toLowerCase())
    || item.title.toLowerCase().includes(search.value.toLowerCase()))

  filteredItems.forEach((item) => {
    if (!item.isChampion)
    // @ts-expect-error correct fields
      storageStore.getTeamImages(item.region, item.team)
  })

  return filteredItems
})

watch(gameName, (newGameName, oldGameName) => {
  if (newGameName && !oldGameName)
    clearError()
})

watch(tagLine, (newTagLine, oldTagLine) => {
  if (newTagLine && !oldTagLine)
    clearError()
})

watch(filteredGames, async (value) => {
  if (!value.length)
    return

  getIcons()

  await new Promise(resolve => setTimeout(resolve, 100))
})

setInterval(getNextUpdateTime, 1000)

function findRegionForTeam(team: string) {
  for (const [key, value] of Object.entries(teamPerRegion)) {
    if (value.includes(team)) {
      return key
    }
  }

  return null
}

function getIcons() {
  const uniqueTeams = [...new Set(filteredGames.value.map(game => game.player.team))]
  uniqueTeams.forEach((team) => {
    const teamRegion = findRegionForTeam(team)

    if (!teamRegion)
      return

    storageStore.getTeamImages(teamRegion, team)
  })

  const uniqueChampionIds = [...new Set(filteredGames.value.map(game => game.participant.championId))]
  uniqueChampionIds.forEach(championId => storageStore.getChampionIcon(championId))
}

function regionItemsProps(item: any) {
  return {
    title: item.value,
    value: item.value,
    subtitle: item.title,
    lines: 'two',
  }
}

function showError() {
  if (!gameName.value) {
    gameNameError.value = errorMessage
  }

  else if (!tagLine.value) {
    tagLineError.value = errorMessage
  }
}

function clearError() {
  gameNameError.value = ''
  tagLineError.value = ''
}

function clearValues() {
  gameName.value = ''
  tagLine.value = ''
  gameNameError.value = ''
  tagLineError.value = ''
  loading.value = false
  region.value = 'EUW'
  refreshTime.value = '00:00'
}

function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  router.push(`/account/${region.value}/${gameName.value}-${tagLine.value}`)
}

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
  <v-container
    style="max-width: 1000px; height: 100%"
    class="d-flex justify-space-between flex-column"
  >
    <v-spacer />

    <v-row
      justify="center"
      align="center"
      :class="mobile
        ? 'mb-1'
        : ''"
    >
      <v-col
        cols="6"
        sm="5"
        md="4"
      >
        <v-img
          :src="logo"
          draggable="false"
          rounded="pill"
        />
      </v-col>
    </v-row>

    <v-spacer />

    <v-card
      color="rgba(50, 50, 50, 0.9)"
      min-height="150px"
    >
      <v-card-text
        class="d-flex align-center mx-10 justify-center"
        style="height: 100%"
      >
        <v-row
          dense
          class="mt-2"
        >
          <v-col
            cols="12"
            sm="3"
          >
            <v-select
              v-model="region"
              :items="regions"
              :item-props="regionItemsProps"
              :label="$t('regions.title')"
              prepend-inner-icon="mdi-earth"
              variant="outlined"
              @keydown.enter="sendToUserView"
            />
          </v-col>

          <v-col
            cols="12"
            sm="6"
          >
            <v-text-field
              v-model="gameName"
              :label="$t('index.gameName')"
              prepend-inner-icon="mdi-account-outline"
              variant="outlined"
              :error-messages="gameNameError"
              @keydown.enter="sendToUserView"
            />
          </v-col>

          <v-col
            cols="12"
            sm="3"
          >
            <v-text-field
              v-model="tagLine"
              :label="$t('index.tagLine')"
              prepend-inner-icon="mdi-pound"
              center-affix
              :rules="[lengthRule($t, 5)]"
              :error-messages="tagLineError"
              @keydown.enter="sendToUserView"
            >
              <template #append>
                <v-btn
                  icon
                  size="small"
                  :loading="loading"
                  @click="sendToUserView"
                >
                  <v-icon
                    icon="mdi-chevron-right"
                    size="x-large"
                  />
                </v-btn>
              </template>
            </v-text-field>
          </v-col>

          <v-col
            cols="12"
            class="mb-6 mt-2"
            align="center"
          >
            <v-row
              align="center"
              font-italic
            >
              <v-col cols="5">
                <v-divider style="max-width: 500px" />
              </v-col>

              <v-col
                cols="2"
                class="font-italic"
              >
                {{ $t('index.or') }}
              </v-col>

              <v-col cols="5">
                <v-divider style="max-width: 500px" />
              </v-col>
            </v-row>
          </v-col>

          <v-col
            cols="12"
            align="center"
          >
            <v-autocomplete
              style="max-width: 600px;"
              prepend-inner-icon="mdi-magnify"
              menu-icon=""
              :label="$t('index.searchProOrChampion')"
              :items="filteredSearchItems"
              hide-no-data
              @update:search="(searchValue: string) => search = searchValue"
            >
              <template #item="{item}">
                <v-list-item
                  lines="two"
                  class="mb-2"
                  :to="item.raw.isChampion
                    ? `/champion/${item.raw.value}`
                    : `/player/${item.raw.team}/${item.raw.player}`"
                  :prepend-avatar="item.raw.isChampion
                    ? championIcons[item.raw.id]
                    : teamImages[item.raw.team]?.[item.raw.player.toLowerCase()]"
                >
                  {{ item.raw.title }}
                </v-list-item>
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-spacer />

    <v-spacer />

    <v-spacer />

    <v-card
      v-if="!mobile"
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
                          :src="teamImages[game.player.team]?.[game.player.player.toLowerCase()]"
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
                          :src="championIcons[game.participant.championId]"
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
  </v-container>
</template>
