<script setup lang="ts">
import { selectRegions } from '~/helpers/regions'
import type { IAccount } from '~/models/account'

const route = useRoute()
const router = useRouter()

const accountStore = useAccountStore()

const storageStore = useStorageStore()
const { regionIcons } = storeToRefs(storageStore)

const username = ref('')
const tag = ref('')
const loading = ref(false)
const accounts = ref<Record<string, IAccount | null>>({})

onMounted(async () => {
  loading.value = true

  try {
    const paramsData = String(route.params.searchaccount)
    username.value = paramsData.split('-')[0]
    tag.value = paramsData.split('-')[1]
  }
  // eslint-disable-next-line unused-imports/no-unused-vars
  catch (error) {
    router.push('/')
  }

  selectRegions.forEach(region => storageStore.getRegionIcon(region))

  try {
    const response = await accountStore.getAccountsInAllRegions(username.value, tag.value)

    if (response) {
      accounts.value = Object.entries(response).reduce((acc, [region, account]) => {
        if (account?.puuid) {
          acc[region] = account
        }

        return acc
      }, {} as Record<string, IAccount | null>)
    }
  }
  // eslint-disable-next-line unused-imports/no-unused-vars
  catch (error) {
    router.push('/')
  }
})

watch(accounts, (newAccounts) => {
  if (newAccounts) {
    loading.value = false
  }
}, { deep: true })
</script>

<template>
  <v-container
    align="center"
  >
    <Loader v-if="loading" />

    <v-card
      v-else-if="!loading && !Object.keys(accounts).length"
      min-height="150"
      style="display: flex; flex-direction: column; justify-content: center; align-items: center;"
    >
      <v-card-title class="text-h5">
        {{ $t('profile.search.title', {username,
                                       tag}) }}
      </v-card-title>

      <v-card-subtitle class="text-h6 mb-4">
        {{ $t('profile.search.subtitle1') }}
      </v-card-subtitle>
    </v-card>

    <v-card v-else-if="!loading && Object.keys(accounts).length">
      <v-card-title class="text-h5">
        {{ $t('profile.search.title', {username,
                                       tag}) }}
      </v-card-title>

      <v-card-subtitle class="text-h6">
        {{ $t('profile.search.subtitle2') }}
      </v-card-subtitle>

      <v-card-text>
        <v-list lines="two">
          <v-row
            class="ma-1"
            justify-center
          >
            <v-col
              v-for="[
                region,
                account,
              ] in Object.entries(accounts)"
              :key="region"
              cols="12"
              sm="6"
            >
              <v-list-item
                :variant="account
                  ? 'tonal'
                  : 'plain'"
                rounded="xl"
                class="ma-2"
                :to="account
                  ? `/account/${account.region}/${account.gameName}-${account.tagLine}`
                  : ''"
              >
                <template #prepend>
                  <v-avatar rounded="0">
                    <v-img
                      :src="regionIcons[region]"
                      lazy-src="~/assets/default.png"
                    />
                  </v-avatar>
                </template>

                <v-list-item-title v-if="account">
                  {{ account.gameName }}

                  <span class="text-gray font-italic">
                    #{{ account?.tagLine || '' }}
                  </span>
                </v-list-item-title>

                <v-list-item-subtitle>
                  {{ region }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-col>
          </v-row>
        </v-list>
      </v-card-text>
    </v-card>
  </v-container>
</template>
