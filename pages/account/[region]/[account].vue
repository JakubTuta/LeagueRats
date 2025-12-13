<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { selectRegions } from '~/helpers/regions'

const route = useRoute()
const router = useRouter()
const { mobile } = useDisplay()
const { t } = useI18n()

const accountStore = useAccountStore()
const leagueStore = useLeagueStore()
const matchStore = useMatchStore()
const championStore = useChampionStore()
const storageStore = useStorageStore()

const proStore = useProPlayerStore()
const { proAccountNames } = storeToRefs(proStore)

const appStore = useAppStore()
const { loading: appLoading } = storeToRefs(appStore)

const selectedTab = ref(0)
const region = ref('')
const gameName = ref('')
const tagLine = ref('')

const proPlayer = ref<{ team: string, player: string } | null>(null)
const isShowTeamDialog = ref(false)
const selectedTeam = ref('')

const tabs = computed(() => [
  { text: t('profile.rank.title'), value: 0 },
  { text: t('profile.matchHistory.title'), value: 1 },
  { text: t('profile.currentGame.title'), value: 2 },
  { text: t('profile.champions.title'), value: 3 },
])

const account = computed(() => accountStore.getAccountData(region.value, gameName.value, tagLine.value))
const accountLoading = computed(() => accountStore.isAccountLoading(region.value, gameName.value, tagLine.value))

onMounted(async () => {
  try {
    const paramsData = route.params as { region: string, account: string }
    region.value = paramsData.region.toUpperCase()
    const accountData = paramsData.account

    if (!accountData.includes('-'))
      throw new Error('Invalid account data')

    gameName.value = accountData.split('-')[0]
    tagLine.value = accountData.split('-')[1]
  }
  catch (error) {
    router.push('/404')

    return
  }

  if (!selectRegions.includes(region.value)) {
    router.push(`/search-account/${gameName.value}-${tagLine.value}`)

    return
  }

  const fetchedAccount = await accountStore.fetchAccount(region.value, gameName.value, tagLine.value)

  if (!fetchedAccount) {
    router.push(`/search-account/${gameName.value}-${tagLine.value}`)

    return
  }

  prefetchAllData(fetchedAccount)
})

watch(account, (acc) => {
  checkIfAccountIsPro(acc)
}, { immediate: true })

watch(isShowTeamDialog, (value) => {
  if (!value)
    selectedTeam.value = ''
})

async function prefetchAllData(acc: any) {
  if (!acc)
    return

  await Promise.all([
    leagueStore.fetchLeagueEntry(acc),
    matchStore.fetchActiveMatch(acc),
    championStore.fetchChampionMastery(acc),
  ])
}

function checkIfAccountIsPro(acc: any) {
  if (!acc?.puuid || !proAccountNames.value)
    return

  proPlayer.value = proAccountNames.value[acc.puuid] || null
}
</script>

<template>
  <v-container>
    <Loader v-if="accountLoading || appLoading" />

    <v-card
      v-else
      rounded="shaped"
    >
      <v-card-title
        align="center"
        class="text-h5 my-4"
      >
        <p
          v-if="proPlayer"
          class="mb-1"
        >
          <v-avatar size="100">
            <v-img
              :src="storageStore.getPlayerImage(proPlayer.player) || undefined"
              lazy-src="~/assets/default.png"
            />
          </v-avatar>
        </p>

        <p
          v-if="proPlayer"
          class="text-subtitle-1 mb-2"
        >
          <NuxtLink
            class="text-blue"
            style="cursor: pointer; text-decoration: none; color: inherit;"
            :to="`/team/${proPlayer.team}`"
          >
            {{ `[${proPlayer.team}]` }}
          </NuxtLink>

          {{ proPlayer.player }}
        </p>

        {{ account?.gameName || '' }}

        <span class="text-gray font-italic">
          #{{ account?.tagLine || '' }}
        </span>
      </v-card-title>

      <v-tabs
        v-if="!accountLoading"
        v-model="selectedTab"
        color="primary"
        align-tabs="center"
        grow
        :show-arrows="mobile"
      >
        <v-tab
          v-for="tab in tabs"
          :key="tab.value"
          :value="tab.value"
        >
          {{ tab.text }}
        </v-tab>
      </v-tabs>

      <v-card-text v-if="!accountLoading">
        <AccountRank
          v-if="selectedTab === 0"
          :region="region"
          :game-name="gameName"
          :tag-line="tagLine"
        />

        <AccountMatchHistory
          v-if="selectedTab === 1"
          :account="account"
        />

        <AccountCurrentGame
          v-if="selectedTab === 2"
          :region="region"
          :game-name="gameName"
          :tag-line="tagLine"
          :account="account"
        />

        <AccountChampions
          v-if="selectedTab === 3"
          :region="region"
          :game-name="gameName"
          :tag-line="tagLine"
          :account="account"
        />
      </v-card-text>
    </v-card>
  </v-container>

  <AccountProTeam
    v-model:is-show="isShowTeamDialog"
    :team="selectedTeam"
  />
</template>
