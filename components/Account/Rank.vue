<script setup lang="ts">
import type { ILeagueEntry } from '~/models/leagueEntry'

const props = defineProps<{
  leagueEntries: ILeagueEntry[]
  loading: boolean
}>()

const { leagueEntries, loading } = toRefs(props)

const storageStore = useStorageStore()
const { rankIcons } = storeToRefs(storageStore)

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

function romanToNumber(roman: string) {
  switch (roman) {
    case 'I':
      return 1
    case 'II':
      return 2
    case 'III':
      return 3
    case 'IV':
      return 4
    default:
      return 0
  }
}

const soloQueue = computed(() => {
  const object = leagueEntries.value.find(entry => entry.queueType === 'RANKED_SOLO_5x5') || null

  if (!object)
    return null

  return {
    priority: 1,
    queueType: object.queueType,
    wins: object.wins,
    losses: object.losses,
    winRate: (object.wins / (object.wins + object.losses) * 100).toFixed(0),
    tier: object.tier,
    rank: object.rank,
    leaguePoints: object.leaguePoints,
  }
})

watch(soloQueue, (value) => {
  if (!value)
    return

  storageStore.getRankIcon(value.tier.toLowerCase())
})

const flexQueue = computed(() => {
  const object = leagueEntries.value.find(entry => entry.queueType === 'RANKED_FLEX_SR') || null

  if (!object)
    return null

  return {
    priority: 2,
    queueType: object.queueType,
    wins: object.wins,
    losses: object.losses,
    winRate: (object.wins / (object.wins + object.losses) * 100).toFixed(0),
    tier: object.tier,
    rank: object.rank,
    leaguePoints: object.leaguePoints,
  }
})

watch(flexQueue, (value) => {
  if (!value)
    return

  if (!rankIcons.value[value.tier.toLowerCase()])
    storageStore.getRankIcon(value.tier.toLowerCase())
})

const items = computed(() => [
  soloQueue.value,
  flexQueue.value,
].filter(item => item !== null).sort((a, b) => a.priority - b.priority))
</script>

<template>
  <v-row
    v-if="!loading && !items.length"
    class="text-h5 mx-2 my-8"
    justify="center"
  >
    {{ $t('profile.rank.noRank') }}
  </v-row>

  <v-row
    v-else
    justify="center"
    class="my-8"
  >
    <v-col
      v-for="(entry, index) in items"
      :key="index"
      cols="12"
      sm="6"
      md="4"
    >
      <v-card
        :elevation="isDark
          ? 20
          : 5"
        class="mx-4"
      >
        <v-card-title align="center">
          {{ $t(`queueTypes.${entry.queueType}`) }}
        </v-card-title>

        <v-card-text class="mx-4">
          <v-row
            class="py-4"
            justify="center"
          >
            <v-avatar
              size="80"
            >
              <v-img
                :src="rankIcons[entry.tier.toLowerCase()]"
                lazy-src="~/assets/default.png"
              />
            </v-avatar>
          </v-row>

          <v-row
            class="text-subtitle-1 py-2"
            justify="center"
          >
            {{ `${$t(`ranks.${entry.tier}`)} ${romanToNumber(entry.rank)}` }}
          </v-row>

          <v-row
            class="text-subtitle-1 pb-4"
            justify="center"
          >
            {{ `${entry.leaguePoints} LP` }}
          </v-row>

          <v-row class="text-subtitle-1 justify-space-between">
            <span class="text-light-blue">
              {{ `${$t('profile.rank.wins')}: ${entry.wins}` }}
            </span>

            <span>
              {{ `${$t('profile.rank.winRate')}: ${entry.winRate}%` }}
            </span>
          </v-row>

          <v-row class="text-subtitle-1 justify-space-between py-2">
            <span class="text-red">
              {{ `${$t('profile.rank.losses')}: ${entry.losses}` }}
            </span>

            <span>
              {{ `${$t('profile.rank.games')}: ${entry.wins + entry.losses}` }}
            </span>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
