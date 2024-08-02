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

const search = ref<string | null>(null)
const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const gameNameError = ref('')
const tagLineError = ref('')
const loading = ref(false)
const userNotExistSnackbar = ref(false)
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
    title: item.title,
    value: item.value,
    subtitle: item.value,
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
  search.value = ''
  gameName.value = ''
  tagLine.value = ''
  gameNameError.value = ''
  tagLineError.value = ''
  loading.value = false
  userNotExistSnackbar.value = false
}

async function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  loading.value = true
  const accountName = `${gameName.value}-${tagLine.value}`

  const databaseAccount = await accountStore.findAccount(gameName.value, tagLine.value)

  if (!databaseAccount) {
    const apiAccount = await restStore.getAccountDetailsByRiotId(gameName.value, tagLine.value)

    if (!apiAccount)
      router.push(`/account/unknown-region/${accountName}`)
  }

  router.push(`/account/${region.value}/${accountName}`)
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

async function print() {
  const data = await restStore.findAccountsInAllRegions('ZawodowyLoL', 'xdd')

  console.log(data)
}
</script>

<template>
  <v-container>
    <v-btn @click="print">
      Print
    </v-btn>

    <v-row
      align-content="center"
      class="my-16"
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
