<script setup lang="ts">
import { useDisplay } from 'vuetify'
// @ts-expect-error correct path
import logo from '~/assets/logo.png'
import { championIdsToTitles } from '~/helpers/championIds'
import { selectRegions, teamPerRegion } from '~/helpers/regions'
import { lengthRule } from '~/helpers/rules'
import type { IProActiveGame } from '~/models/proActiveGame'

const { t } = useI18n()
const router = useRouter()
const { mobile } = useDisplay()

const proStore = useProPlayerStore()
const { activeGames } = storeToRefs(proStore)

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const storageStore = useStorageStore()
const { championIcons, teamImages } = storeToRefs(storageStore)

const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const region = ref('EUW')
const refreshTime = ref('00:00')

const errorMessage = t('rules.requiredField')

onMounted(() => {
  proStore.getActiveProGamesFromDatabase()
})

onUnmounted(() => {
  clearValues()
})

const cardColor = computed(() => {
  return isDark.value
    ? 'rgba(50, 50, 50, 0.85)'
    : 'rgba(200, 200, 200, 0.85)'
})

const splitProGames = computed(() => {
  if (!activeGames.value)
    return []

  const shuffledGames = shuffleArray(activeGames.value.map(e => e))

  getIcons()

  const chunkSize = 3
  const result = []
  let i = 0

  while (i < shuffledGames.length) {
    const end = Math.min(i + chunkSize, shuffledGames.length)
    result.push(shuffledGames.slice(i, end))
    i += chunkSize
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

watch(gameName, (newGameName, oldGameName) => {
  if (newGameName && !oldGameName)
    clearError()
})

watch(tagLine, (newTagLine, oldTagLine) => {
  if (newTagLine && !oldTagLine)
    clearError()
})

setInterval(getNextUpdateTIme, 1000)

function shuffleArray<T>(array: T[]): T[] {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]]
  }

  return array
}

function findRegionForTeam(team: string) {
  for (const [key, value] of Object.entries(teamPerRegion)) {
    if (value.includes(team)) {
      return key
    }
  }

  return null
}

function getIcons() {
  const uniqueTeams = [...new Set(activeGames.value.map(game => game.player.team))]
  uniqueTeams.forEach((team) => {
    const teamRegion = findRegionForTeam(team)

    if (!teamRegion)
      return

    storageStore.getTeamImages(teamRegion, team)
  })

  const uniqueChampionIds = [...new Set(activeGames.value.map(game => findPlayerParticipant(game).championId))]
  uniqueChampionIds.forEach(championId => storageStore.getChampionIcon(championId))
}

function findPlayerParticipant(game: IProActiveGame) {
  return game.game.participants.find(participant => participant.puuid === game.player.puuid)!
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
}

function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  router.push(`/account/${region.value}/${gameName.value}-${tagLine.value}`)
}

function getNextUpdateTIme() {
  const now = new Date()
  const next10Minutes = new Date()
  next10Minutes.setSeconds(0)

  const minutes = now.getMinutes()

  if (minutes < 10) {
    next10Minutes.setMinutes(10)
  }

  else if (minutes < 20) {
    next10Minutes.setMinutes(20)
  }

  else if (minutes < 30) {
    next10Minutes.setMinutes(30)
  }

  else if (minutes < 40) {
    next10Minutes.setMinutes(40)
  }

  else if (minutes < 50) {
    next10Minutes.setMinutes(50)
  }

  else {
    next10Minutes.setHours(now.getHours() + 1)
    next10Minutes.setMinutes(0)
  }

  const diff = next10Minutes.getTime() - now.getTime()
  const minutesDiff = String(Math.floor(diff / 60000)).padStart(2, '0')
  const secondsDiff = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0')

  refreshTime.value = `${minutesDiff}:${secondsDiff}`
}
</script>

<template>
  <v-container
    style="max-width: 1000px; height: 100%"
    class="d-flex flex-column justify-space-between"
  >
    <v-spacer />

    <v-row
      justify="center"
      align="center"
    >
      <v-img
        :src="logo"
        draggable="false"
        max-width="400"
        rounded="pill"
      />
    </v-row>

    <v-spacer />

    <v-card
      :color="cardColor"
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
        </v-row>
      </v-card-text>
    </v-card>

    <v-spacer />

    <v-spacer />

    <v-spacer />

    <v-card
      v-if="!mobile"
      :color="cardColor"
      height="300px"
    >
      <v-card-text v-if="!activeGames.length">
        {{ $t('index.nextUpdate', {"time": refreshTime}) }}
        <v-skeleton-loader
          type="card"
          class="mt-5"
          :color="cardColor"
        />
      </v-card-text>

      <v-card-text v-else>
        {{ $t('index.nextUpdate', {"time": refreshTime}) }}
        <v-carousel
          class="mt-1"
          hide-delimiters
          interval="10000"
          cycle
          height="250"
          :show-arrows="splitProGames.length > 1"
        >
          <v-carousel-item
            v-for="(games, index) in splitProGames"
            :key="index"
          >
            <v-row
              :class="splitProGames.length > 1
                ? 'mx-15'
                : ''"
            >
              <v-col
                v-for="game in games"
                :key="game.game.gameId"
                cols="4"
              >
                <v-card
                  align="center"
                  style="height: 250px"
                  :ripple="false"
                  :to="`/account/${game.player.region}/${game.player.gameName}-${game.player.tagLine}`"
                >
                  <v-card-text style="height: 100%; display: flex; flex-direction: column; justify-content: space-between">
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
                      <!--
                        <v-avatar
                        size="40"
                        class="mr-2"
                        >
                        <v-tooltip
                        activator="parent"
                        location="bottom"
                        >
                        {{ game.game.gameMode === 'ARAM'
                        ? $t('universal.aram')
                        : $t('universal.classic') }}
                        </v-tooltip>

                        <v-img
                        :src="game.game.gameMode === 'ARAM'
                        ? aramIcon
                        : classicIcon"
                        />
                        </v-avatar>
                      -->

                      <v-avatar
                        size="40"
                      >
                        <v-tooltip
                          activator="parent"
                          location="bottom"
                        >
                          {{ championIdsToTitles[findPlayerParticipant(game).championId] }}
                        </v-tooltip>

                        <v-img
                          lazy-src="~/assets/default.png"
                          :src="championIcons[findPlayerParticipant(game).championId]"
                        />
                      </v-avatar>
                    </div>

                    <div>
                      <p
                        class="text-subtitle-2 text-gray"
                        style="margin-top: auto"
                      >
                        {{ game.player.region }}
                      </p>

                      <p>
                        {{ game.player.gameName }}
                        <span class="text-gray">
                          {{ ` #${game.player.tagLine}` }}
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
