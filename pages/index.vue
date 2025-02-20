<script setup lang="ts">
import { useDisplay } from 'vuetify'
// @ts-expect-error correct path
import logo from '~/assets/logo.png'
import { selectRegions } from '~/helpers/regions'
import { lengthRule } from '~/helpers/rules'

const { t } = useI18n()
const router = useRouter()
const { mobile } = useDisplay()

const proStore = useProPlayerStore()
const { savedPlayers } = storeToRefs(proStore)

const storageStore = useStorageStore()

const championStore = useChampionStore()
const { champions } = storeToRefs(championStore)

const appStore = useAppStore()
const { loading: appLoading } = storeToRefs(appStore)

useSummonerSpellsStore()

const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const region = ref('EUW')
const search = ref('')

const errorMessage = t('rules.requiredField')

onUnmounted(() => {
  clearValues()
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

const allProPlayers = computed(() => {
  if (!savedPlayers.value)
    return []

  return Object.values(savedPlayers.value).flatMap(region => Object.values(region).flat())
})

const searchItems = computed(() => {
  if (search.value.length < 3)
    return []

  const championItems = sortedChampions.value.map((champion) => {
    return {
      title: champion.title,
      value: champion.value,
      isChampion: true,
      id: champion.id,
    }
  })

  const proPlayerItems = allProPlayers.value.map((player) => {
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

  if (!tagLine.value) {
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
}

function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  router.push(`/account/${region.value}/${gameName.value}-${tagLine.value}`)
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

    <Loader v-if="appLoading" />

    <v-card
      v-else
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
                    ? `/champion/${item.raw.value.toLowerCase()}`
                    : `/player/${item.raw.team}/${item.raw.player}`"
                  :prepend-avatar="item.raw.isChampion
                    ? storageStore.getChampionIcon(item.raw.id)
                    : storageStore.getPlayerImage(item.raw.player)"
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

    <v-spacer />

    <LazyActiveProGames v-if="!mobile" />
  </v-container>
</template>
