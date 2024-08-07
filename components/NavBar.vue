<script setup lang="ts">
import { useDisplay } from 'vuetify';
import { selectRegions } from '~/helpers/regions';
import { lengthRule } from '~/helpers/rules';

const router = useRouter()
const route = useRoute()
const { mobile } = useDisplay()
const { t } = useI18n()

const accountStore = useAccountStore()
const restStore = useRestStore()

const loading = ref(false)
const gameName = ref<string | null>(null)
const tagLine = ref<string | null>(null)
const region = ref('EUW')
const gameNameError = ref('')
const tagLineError = ref('')

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

async function sendToUserView() {
  if (!gameName.value || !tagLine.value || tagLine.value.length > 5) {
    showError()

    return
  }

  loading.value = true
  const accountName = `${gameName.value}-${tagLine.value}`
  const lowerCaseRegion = region.value.toLowerCase()

  const databaseAccount = await accountStore.findAccount(gameName.value, tagLine.value, region.value)

  if (databaseAccount) {
    router.push(`/account/${lowerCaseRegion}/${accountName}`)
    loading.value = false

    return
  }

  const apiAccount = await restStore.getAccountDetailsByRiotId(gameName.value, tagLine.value)

  if (!apiAccount) {
    router.push(`/account/unknown-region/${accountName}`)
    loading.value = false

    return
  }

  const apiSummoner = await restStore.getSummonerDetailsByPuuid(apiAccount.puuid, region.value)

  if (!apiSummoner) {
    router.push(`/account/unknown-region/${accountName}`)
    loading.value = false

    return
  }

  router.push(`/account/${lowerCaseRegion}/${accountName}`)
  loading.value = false
}
</script>

<template>
  <v-app-bar>
    <template
      v-if="!mobile && route.path !== '/'"
      #extension
    >
      <v-row
        no-gutters
        align="center"
        class="mt-4"
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
          sm="6"
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
          sm="3"
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

    <v-app-bar-title>
      <v-tooltip
        :text="$t('navbar.home')"
        location="bottom"
      >
        <template #activator="{props}">
          <NuxtLink
            style="cursor: pointer; text-decoration: none; color: inherit;"
            v-bind="props"
            to="/"
          >
            {{ $t('universal.title') }}
          </NuxtLink>
        </template>
      </v-tooltip>
    </v-app-bar-title>
  </v-app-bar>
</template>
