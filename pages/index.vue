<script setup lang="ts">
import { useDisplay } from 'vuetify';
// @ts-expect-error correct path
import logo from '~/assets/logo.png';
import { selectRegions } from '~/helpers/regions';
import { lengthRule } from '~/helpers/rules';

const { t } = useI18n()
const router = useRouter()
const { mobile } = useDisplay()

const proStore = useProPlayerStore()
const { activeGames } = storeToRefs(proStore)

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const region = ref('EUW')
const isLoadingGames = ref(false)

const cardColor = computed(() => {
  return isDark.value
    ? 'rgba(50, 50, 50, 0.85)'
    : 'rgba(200, 200, 200, 0.85)'
})

const errorMessage = t('rules.requiredField')

const splitProGames = computed(() => {
  if (!activeGames.value)
    return []

  console.log(activeGames.value)
  const shuffledGames = [...activeGames.value].sort(() => Math.random() - 0.5)

  const chunkSize = 4
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

onMounted(async () => {
  isLoadingGames.value = true
  await proStore.getActiveProGames()
  isLoadingGames.value = false
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

function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

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
      height="250px"
    >
      <v-card-text v-if="isLoadingGames">
        <v-skeleton-loader
          type="card"
          :color="cardColor"
        />
      </v-card-text>

      <v-card-text v-else>
        <v-carousel>
          <v-carousel-item
            v-for="(games, index) in splitProGames"
            :key="index"
          >
            <v-row>
              <v-col
                v-for="game in games"
                :key="game.game.gameId"
                cols="3"
              >
                <v-card
                  align="center"
                  style="height: 220px"
                >
                  <v-card-text style="height: 100%; display: flex; flex-direction: column; justify-content: space-between">
                    <div>
                      <v-avatar
                        image="~/assets/default.png"
                        size="80"
                      />

                      <p class="mt-2">
                        {{ `${game.player.team} ${game.player.player}` }}
                      </p>
                    </div>

                    <div>
                      <p
                        class="text-subtitle-2 mt-1 text-gray"
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
