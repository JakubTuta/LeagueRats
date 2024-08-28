<script setup lang="ts">
import { selectRegions } from '~/helpers/regions'
import { lengthRule } from '~/helpers/rules'
import type { IActiveGame } from '~/models/activeGame'
import { useAccountStore } from '~/stores/accountStore'
import { useRestStore } from '~/stores/restStore'

const { t } = useI18n()
const router = useRouter()

const accountStore = useAccountStore()
const restStore = useRestStore()

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const featuredGames = ref<IActiveGame[]>([])
const region = ref('EUW')

const errorMessage = t('rules.requiredField')

const regions = computed(() => {
  return selectRegions.map((region) => {
    return {
      title: t(`regions.${region.toLowerCase()}`),
      value: region,
    }
  })
})

onMounted(async () => {
  featuredGames.value = await restStore.getFeaturedGames()
})

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

async function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  loading.value = true

  const response = await accountStore.getAccount(gameName.value, tagLine.value, region.value, false)

  if (!response) {
    router.push(`/search-account/${gameName.value}-${tagLine.value}`)

    return
  }

  router.push(`/account/${region.value}/${gameName.value}-${tagLine.value}`)
}

watch(gameName, (newGameName, oldGameName) => {
  if (newGameName && !oldGameName)
    clearError()
})

watch(tagLine, (newTagLine, oldTagLine) => {
  if (newTagLine && !oldTagLine)
    clearError()
})

onUnmounted(() => {
  clearValues()
})

function formatTime(time: number) {
  const minutes = Math.floor(time / 60)
  const seconds = time % 60

  return `${minutes}:${seconds < 10
? `0${seconds}`
: seconds}`
}

setInterval(() => {
  for (const game of featuredGames.value) {
    game.gameLength += 1
  }
}, 1000)
</script>

<template>
  <v-container
    style="max-width: 1000px; height: 100%"
    class="d-flex flex-column justify-center"
  >
    <v-spacer />

    <v-row style="justify-content: center; align-items: center">
      <v-col
        cols="12"
        sm="6"
        md="5"
      >
        <v-card
          :color="isDark
            ? 'rgba(50, 50, 50, 0.75)'
            : 'rgba(200, 200, 200, 0.75)'"
          :class="isDark
            ? 'text-h3 text-grey-lighten-1 my-1'
            : 'text-h3 text-grey-darken-3 my-1'"
          height="120px"
          rounded="pill"
          style="display: flex; align-items: center; justify-content: center;"
        >
          {{ $t('universal.title') }}
        </v-card>
      </v-col>
    </v-row>

    <v-spacer />

    <v-card
      :color="isDark
        ? 'rgba(50, 50, 50, 0.75)'
        : 'rgba(200, 200, 200, 0.75)'"
      class="my-auto"
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

    <v-spacer class="mb-10" />

    <v-card
      v-if="featuredGames.length > 0"
      :color="isDark
        ? 'rgba(50, 50, 50, 0.75)'
        : 'rgba(200, 200, 200, 0.75)'"
      variant="flat"
      class="mt-auto"
    >
      <v-card-title align="center">
        {{ $t('index.featuredGames') }}
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col
            v-for="game in featuredGames"
            :key="game.gameId"
            cols="12"
            class="my-3"
          >
            <v-expansion-panels
              :color="isDark
                ? 'rgba(50, 50, 50, 0.75)'
                : 'rgba(200, 200, 200, 0.75)'"
            >
              <v-expansion-panel>
                <v-expansion-panel-title
                  style="height: 70px;"
                  :color="isDark
                    ? 'rgba(50, 50, 50, 1)'
                    : 'rgba(200, 200, 200, 1)'"
                >
                  <v-img
                    v-if="game.gameMode === 'CLASSIC'"
                    src="~/assets/classic_icon.png"
                    lazy-src="~/assets/default.png"
                    width="30"
                    height="30"
                    style="position: absolute; left: 10px"
                  />

                  <v-img
                    v-else
                    src="~/assets/aram_icon.png"
                    lazy-src="~/assets/default.png"
                    width="30"
                    height="30"
                    style="position: absolute; left: 10px"
                  />

                  <span style="position: absolute; left: 60px;">
                    {{ $t(`game.${game.gameMode.toLowerCase()}`) }}

                    <span v-if="game.gameMode !== 'ARAM'">
                      {{ $t(`queueTypes.${game.gameQueueConfigId}`) }}
                    </span>
                  </span>

                  <span
                    style="position: absolute; right: 75px"
                  >
                    {{ formatTime(game.gameLength) }}
                  </span>
                </v-expansion-panel-title>

                <v-expansion-panel-text
                  :style="isDark
                    ? 'background-color: rgba(50, 50, 50, 1);'
                    : 'background-color: rgba(200, 200, 200, 1);'"
                  class="black"
                >
                  <AccountGameTable
                    :game="game"
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>
