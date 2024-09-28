<script setup lang="ts">
import { useDisplay } from 'vuetify';
import { selectRegions } from '~/helpers/regions';
import { lengthRule } from '~/helpers/rules';

const router = useRouter()
const route = useRoute()
const { mobile } = useDisplay()
const { t } = useI18n()

const accountStore = useAccountStore()

const loading = ref(false)
const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const region = ref('EUW')
const gameNameError = ref('')
const tagLineError = ref('')
const isShowSettings = ref(false)

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const tabs = computed(() => [
  {
    title: t('navbar.proPlayers'),
    to: '/pro-players',
  },
])

const errorMessage = t('rules.requiredField')

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

  router.push(`/account/${region.value.toLowerCase()}/${gameName.value}-${tagLine.value}`)
  loading.value = false
}

const isExtension = computed(() => !mobile.value && route.path !== '/')

function toggleSettings() {
  isShowSettings.value = !isShowSettings.value
}
</script>

<template>
  <v-app-bar
    rounded="xl"
    flat
    extension-height="60"
    :color="isDark
      ? 'rgba(50, 50, 50, 0.85)'
      : 'rgba(200, 200, 200, 0.85)'"
    scroll-behavior="fully-hide"
    scroll-threshold="100"
  >
    <template
      v-if="isExtension"
      #extension
    >
      <v-row
        no-gutters
        align="center"
        class="mt-6"
        style="max-width: 800px; display: flex; flex-wrap: wrap; margin: 0 auto;"
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
            density="compact"
            @keydown.enter="sendToUserView"
          />
        </v-col>

        <v-col
          cols="12"
          sm="5"
        >
          <v-text-field
            v-model="gameName"
            :label="$t('index.gameName')"
            prepend-inner-icon="mdi-account-outline"
            variant="outlined"
            density="compact"
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
            center-affix
            density="compact"
            :rules="[lengthRule($t, 5)]"
            :error-messages="tagLineError"
            @keydown.enter="sendToUserView"
          >
            <template #append>
              <v-btn
                icon
                size="small"
                :loading="loading"
                variant="flat"
                @click="sendToUserView"
              >
                <v-icon
                  icon="mdi-chevron-right"
                  size="large"
                />
              </v-btn>
            </template>
          </v-text-field>
        </v-col>
      </v-row>
    </template>

    <v-img
      src="~/assets/default.png"
      max-height="40"
      max-width="40"
      class="ml-4"
      rounded="circle"
    />

    <span
      z-1
      class="text-h6 ml-4"
    >
      <NuxtLink
        class="pa-1"
        style="cursor: pointer; text-decoration: none; color: inherit;"
        to="/"
      >
        <v-tooltip
          activator="parent"
          location="bottom"
          :text="$t('navbar.home')"
        />

        {{ $t('universal.title') }}
      </NuxtLink>
    </span>

    <v-tabs
      v-if="!mobile"
      height="50px"
      style="position: absolute; left: 0; right: 0"
      align-tabs="center"
      color="primary"
    >
      <v-tab
        v-for="tab in tabs"
        :key="tab.title"
        :to="tab.to"
      >
        {{ tab.title }}
      </v-tab>
    </v-tabs>

    <template #append>
      <v-btn
        icon
        class="mr-2"
        @click="toggleSettings"
      >
        <v-icon
          icon="mdi-cog-outline"
        />
      </v-btn>
    </template>
  </v-app-bar>

  <SettingsDialog
    :is-show="isShowSettings"
    @close="toggleSettings"
  />
</template>
