<script setup lang="ts">
import { lengthRule } from '~/helpers/rules';
import type { ActiveGameModel } from '~/models/activeGame';
import { useAccountStore } from '~/stores/accountStore';
import { useRestStore } from '~/stores/restStore';

const { t } = useI18n()

const router = useRouter()

const accountStore = useAccountStore()
const restStore = useRestStore()

const search = ref<string | null>(null)
const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const userNotExistSnackbar = ref(false)
const featuredGames = ref<ActiveGameModel[]>([])
// const region = ref('europe')

const errorMessage = t('rules.requiredField')

// const regions = computed(() => [
//   {
//     title: t('regions.europe'),
//     value: 'europe',
//   },
//   {
//     title: t('regions.america'),
//     value: 'america',
//   },
//   {
//     title: t('regions.asia'),
//     value: 'asia',
//   },
// ])

onMounted(async () => {
  featuredGames.value = await restStore.getFeaturedGames()
})

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
  search.value = ''
  gameName.value = ''
  tagLine.value = ''
  gameNameError.value = ''
  tagLineError.value = ''
  loading.value = false
  userNotExistSnackbar.value = false
}

async function getAccountDetails(gameName: string, tagLine: string) {
  loading.value = true

  const databaseAccountDetails = await accountStore.getAccountDetails(gameName, tagLine)

  if (databaseAccountDetails) {
    return databaseAccountDetails
  }

  const apiAccountDetails = await restStore.getAccountDetailsByRiotId(gameName, tagLine)

  if (apiAccountDetails) {
    accountStore.saveAccount(apiAccountDetails)

    return apiAccountDetails
  }

  loading.value = false

  return null
}

async function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  const accountDetails = await getAccountDetails(gameName.value, tagLine.value)

  if (!accountDetails) {
    userNotExistSnackbar.value = true

    return
  }

  const accountName = `${gameName.value}-${tagLine.value}`

  router.push(`/account/${accountName}`)
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

watch(userNotExistSnackbar, (newValue, oldValue) => {
  if (!oldValue && newValue) {
    setTimeout(() => {
      userNotExistSnackbar.value = false
    }, 5000)
  }
})
</script>

<template>
  <v-container>
    <!--
      <v-autocomplete
      v-model="search"
      prepend-inner-icon="mdi-magnify"
      clearable
      :label="$t('index.champion')"
      :items="champions"
      :custom-filter="searchChampion"
      />

      <v-spacer class="my-5" />
    -->

    <v-row align-content="center">
      <!--
        <v-col
        cols="12"
        sm="2"
        >
        <v-select
        v-model="region"
        :items="regions"
        :label="$t('regions.title')"
        prepend-inner-icon="mdi-earth"
        />
        </v-col>
      -->

      <v-col
        cols="12"
        sm="8"
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
        sm="4"
      >
        <v-text-field
          v-model="tagLine"
          :label="$t('index.tagLine')"
          prepend-inner-icon="mdi-pound"
          append-icon="mdi-arrow-right"
          :rules="[lengthRule($t, 5)]"
          :error-messages="tagLineError"
          @click:append="sendToUserView"
          @keydown.enter="sendToUserView"
        />
      </v-col>

      <v-col cols="12">
        <v-alert
          v-model="userNotExistSnackbar"
          type="warning"
          variant="tonal"
          closable
        >
          {{ $t('index.userNotExist') }}
        </v-alert>
      </v-col>
    </v-row>

    <v-spacer class="my-16" />

    <v-card
      v-if="featuredGames.length > 0"
      variant="flat"
    >
      <v-card-title>
        {{ $t('index.featuredGames') }}
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col
            v-for="game in featuredGames"
            :key="game.gameId"
            cols="12"
            md="6"
            class="my-3"
          >
            <v-expansion-panels>
              <v-expansion-panel>
                <v-expansion-panel-title style="height: 70px;">
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
                  </span>
                </v-expansion-panel-title>

                <v-expansion-panel-text>
                  <AccountGameTable
                    v-expansion-panel-text
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
