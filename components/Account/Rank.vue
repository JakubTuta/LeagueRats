<script setup lang="ts">
import type { ILeagueEntry } from '~/models/leagueEntry';

const props = defineProps<{
  leagueEntries: ILeagueEntry[]
}>()

const { leagueEntries } = toRefs(props)

const storageStore = useStorageStore()

const rankIcons = ref<Record<string, string>>({})

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

watch(soloQueue, async (value) => {
  if (!value)
    return

  if (!rankIcons.value[value.tier.toLowerCase()])
    rankIcons.value[value.tier.toLowerCase()] = await storageStore.getRankIcon(value.tier.toLowerCase())
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

watch(flexQueue, async (value) => {
  if (!value)
    return

  if (!rankIcons.value[value.tier.toLowerCase()])
    rankIcons.value[value.tier.toLowerCase()] = await storageStore.getRankIcon(value.tier.toLowerCase())
})

const items = computed(() => [
  soloQueue.value,
  flexQueue.value,
].filter(item => item !== null).sort((a, b) => a.priority - b.priority))
</script>

<template>
  <v-row>
    <v-col
      v-for="(entry, index) in items"
      :key="index"
      cols="12"
      sm="6"
    >
      <v-card>
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
            {{ `${entry.tier} ${romanToNumber(entry.rank)}` }}
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

          <!--
            <v-row class="text-subtitle-1 pb-2">
            {{ `${$t('profile.rank.winRate')}: ${entry.winRate}%` }}
            </v-row>

            <v-row class="text-subtitle-1">
            {{ `${$t('profile.rank.games')}: ${entry.wins + entry.wins}` }}
            </v-row>
          -->
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
