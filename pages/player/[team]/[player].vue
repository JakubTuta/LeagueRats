<script setup lang="ts">
import { useDisplay } from 'vuetify'
// @ts-expect-error correct path
import topIcon from '~/assets/roles/top.png'
// @ts-expect-error correct path
import jngIcon from '~/assets/roles/jng.png'
// @ts-expect-error correct path
import midIcon from '~/assets/roles/mid.png'
// @ts-expect-error correct path
import adcIcon from '~/assets/roles/adc.png'
// @ts-expect-error correct path
import supIcon from '~/assets/roles/sup.png'
import { mapKDAToColor } from '~/helpers/kdaColors'
import { regionColors } from '~/helpers/regionColors'
import { teamPerRegion } from '~/helpers/regions'
import { calculateTotalLP } from '~/helpers/totalLP'
import { fullUrl } from '~/helpers/url'
import type { IAccount } from '~/models/account'
import type { ILeagueEntry } from '~/models/leagueEntry'
import type { IProPlayer } from '~/models/proPlayer'
import { useLeagueStore } from '~/stores/leagueStore'

interface IChampionHistory {
  championId: number
  championName: string
  games: number
  wins: number
  losses: number
  kills: number
  deaths: number
  assists: number
}

const route = useRoute()
const { smAndDown, mobile } = useDisplay()

const proStore = useProPlayerStore()
const { liveStreams, notLiveStreams } = storeToRefs(proStore)

const championStore = useChampionStore()
const { champions } = storeToRefs(championStore)

const accountStore = useAccountStore()
const leagueStore = useLeagueStore()
const storageStore = useStorageStore()

const player = ref<IProPlayer | null>(null)
const loading = ref(false)
const proAccounts = ref<{ account: IAccount, leagueEntry: ILeagueEntry | null }[]>([])
const historyStats = ref<{ [championId: number]: { wins: number, losses: number, kills: number, deaths: number, assists: number } } | null>(null)

onMounted(async () => {
  loading.value = true

  const team = (route.params.team as string).toUpperCase()
  const playerName = route.params.player as string
  const region = findRegionForTeam(team)

  proStore.getPlayerHistoryStats(team, playerName).then(stats => historyStats.value = stats)

  if (!region) {
    loading.value = false

    return
  }

  player.value = await proStore.getPlayer(region, team, playerName)

  if (!player.value) {
    loading.value = false

    return
  }

  const promises = player.value.puuid.map(async puuid => await accountStore.getAccount({ puuid }))
  const accounts = (await Promise.all(promises)).filter(account => account !== null) as IAccount[]

  const leagueEntryPromises = accounts.map(async account => await leagueStore.getLeagueEntry(account.puuid))
  const leagueEntries = (await Promise.all(leagueEntryPromises)).filter(entry => entry !== null) as ILeagueEntry[]

  proAccounts.value = accounts.map((account) => {
    const leagueEntry = leagueEntries.flat().find(e => e.queueType === 'RANKED_SOLO_5x5' && e.summonerId === account.id) || null

    return { account, leagueEntry }
  }).sort((a, b) => calculateTotalLP(b.leagueEntry) - calculateTotalLP(a.leagueEntry))

  loading.value = false
})

const liveStream = computed(() => liveStreams.value[player.value?.player || ''] || null)
const notLiveStream = computed(() => notLiveStreams.value[player.value?.player || ''] || null)

const groupedAccounts = computed(() => {
  const regions = proAccounts.value.reduce((acc, account) => {
    if (!acc[account.account.region])
      acc[account.account.region] = []

    acc[account.account.region].push(account)

    return acc
  }, {} as Record<string, { account: IAccount, leagueEntry: ILeagueEntry | null }[]>)

  const sortedRegions = Object.fromEntries(
    Object.entries(regions).sort((a, b) => b[1].length - a[1].length),
  )

  return sortedRegions
})

const mapChampionHistory = computed(() => {
  if (!historyStats.value)
    return []

  return Object.entries(historyStats.value).map(([championId, stats]) => {
    const championName = findChampionNameFromId(Number(championId))

    return {
      championId: Number(championId),
      championName,
      games: stats.wins + stats.losses,
      ...stats,
    }
  }).sort((a, b) => b.games - a.games)
})

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

function getPlayerRoleIcon(player: { role: string }) {
  switch (player.role) {
    case 'TOP':
      return topIcon
    case 'JNG':
      return jngIcon
    case 'MID':
      return midIcon
    case 'ADC':
      return adcIcon
    case 'SUP':
      return supIcon
    default:
      return ''
  }
}

function findChampionNameFromId(championId: number) {
  return champions.value[championId]?.value || ''
}

function getKDA(champion: IChampionHistory) {
  const kda = (champion.kills + champion.assists) / champion.deaths

  return kda.toFixed(2)
}

function getWinRatio(champion: IChampionHistory) {
  const winRatio = champion.wins / champion.games

  return (winRatio * 100).toFixed(2)
}

function findRegionForTeam(team: string) {
  if (!team)
    return

  for (const [region, teams] of Object.entries(teamPerRegion)) {
    if (teams.includes(team))
      return region
  }
}
</script>

<!-- eslint-disable vue/no-bare-strings-in-template -->
<template>
  <v-container
    :class="mobile
      ? ''
      : 'fill-height'"
  >
    <v-row
      class="pa-3"
      align="center"
      justify="center"
    >
      <Loader v-if="loading" />

      <v-card v-else-if="!loading && !player">
        <v-card-title
          align="center"
          class="my-3"
        >
          {{ $t('proPlayers.notFound') }}
        </v-card-title>
      </v-card>

      <v-card v-else-if="!loading && player">
        <NuxtLink
          v-if="liveStream"
          external
          :to="`${fullUrl.twitch}/${liveStream.twitch}`"
        >
          <v-avatar
            style="position: absolute; top: 25px; right: 25px;"
            size="70"
            rounded="0"
            variant="flat"
          >
            <v-badge
              dot
              color="red"
            >
              <v-icon
                size="60"
                icon="mdi-twitch"
                color="secondary"
              />

              <v-tooltip
                activator="parent"
                location="bottom"
              >
                {{ $t('proPlayers.isLive', {"player": player.player}) }}
              </v-tooltip>
            </v-badge>
          </v-avatar>
        </NuxtLink>

        <NuxtLink
          v-else-if="notLiveStream"
          external
          :to="`${fullUrl.twitch}/${notLiveStream.twitch}`"
        >
          <v-avatar
            style="position: absolute; top: 25px; right: 25px;"
            size="70"
            rounded="0"
            variant="flat"
          >
            <v-icon
              size="60"
              icon="mdi-twitch"
              color="gray"
            />
          </v-avatar>
        </NuxtLink>

        <v-card-title align="center">
          <p class="my-4">
            <v-avatar size="150">
              <v-img
                :src="storageStore.getPlayerImage(player.player)"
                lazy-src="~/assets/default.png"
              />
            </v-avatar>
          </p>

          <div style="display: flex; justify-content: center; align-items: center">
            <v-avatar
              rounded="0"
              size="30"
              class="mr-3"
            >
              <v-img :src="getPlayerRoleIcon(player)" />
            </v-avatar>

            <NuxtLink
              class="mr-1 text-blue"
              style="cursor: pointer; text-decoration: none; color: inherit;"
              :to="`/team/${player.team}`"
            >
              {{ `[${player.team}]` }}
            </NuxtLink>

            {{ player.player }}
          </div>
        </v-card-title>

        <v-card-text
          v-if="!proAccounts.length"
          class="text-h5 ma-6"
        >
          {{ $t('proPlayers.noAccounts') }}
        </v-card-text>

        <v-card-text
          v-else
          class="mt-4"
        >
          <v-row>
            <v-col
              cols="12"
              md="7"
              :order="smAndDown
                ? 2
                : 1"
            >
              <span class="text-h5 ml-5">
                {{ $t('proPlayers.accounts') }}
              </span>

              <v-list
                v-for="[
                  region,
                  accounts,
                ] in Object.entries(groupedAccounts)"
                :key="region"
                lines="three"
                class="my-4"
              >
                <v-chip
                  class="ml-8"
                  variant="elevated"
                  :color="regionColors[region]"
                  size="large"
                >
                  {{ region }}
                </v-chip>

                <v-list-item
                  v-for="account in accounts"
                  :key="account.account.puuid"
                  class="my-2"
                  justify="center"
                  :to="`/account/${account.account.region}/${account.account.gameName}-${account.account.tagLine}`"
                >
                  <template
                    v-if="account.leagueEntry"
                    #prepend
                  >
                    <div align="center">
                      <v-avatar
                        size="70"
                      >
                        <v-img
                          :src="storageStore.getRankIcon(account.leagueEntry.tier)"
                          lazy-src="~/assets/default.png"
                        />
                      </v-avatar>

                      <p
                        v-if="[
                          'CHALLENGER',
                          'GRANDMASTER',
                          'MASTER',
                        ].includes(account.leagueEntry.tier)"
                        class="text-subtitle-2"
                      >
                        {{ `${account.leagueEntry.tier} ${account.leagueEntry.leaguePoints}LP` }}
                      </p>

                      <p v-else>
                        {{ `${account.leagueEntry.tier} ${romanToNumber(account.leagueEntry.rank)}` }}
                      </p>
                    </div>
                  </template>

                  <v-list-item-title class="text-h6 ml-7">
                    {{ account.account.gameName }}

                    <span class="text-gray">
                      {{ ` #${account.account.tagLine}` }}
                    </span>
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>

            <v-col
              v-if="mapChampionHistory.length"
              cols="12"
              md="5"
              :order="smAndDown
                ? 1
                : 2"
              class="mb-6"
            >
              <span class="text-h5 ml-5">
                {{ $t('proPlayers.lastGames', {"games": mapChampionHistory.length}) }}
              </span>

              <v-list
                class="scroll-list"
                lines="two"
              >
                <v-list-item
                  v-for="champion in mapChampionHistory"
                  :key="champion.championId"
                  :to="`/champion/${champion.championName.toLowerCase()}`"
                >
                  <template #prepend>
                    <v-avatar
                      size="45"
                    >
                      <v-img
                        :src="storageStore.getChampionIcon(champion.championId)"
                        lazy-src="~/assets/default.png"
                      />
                    </v-avatar>
                  </template>

                  <v-row align="center">
                    <v-col cols="4">
                      <p class="text-h6">
                        {{ champions[champion.championId]?.title || '' }}
                      </p>

                      <p class="text-subtitle-2">
                        {{ `${$t('proPlayers.games')}: ${champion.games}` }}
                      </p>
                    </v-col>

                    <v-col
                      cols="4"
                      align="center"
                    >
                      <p class="text-h6">
                        {{ getWinRatio(champion) }}%
                      </p>

                      <p class="text-caption">
                        Win rate
                      </p>
                    </v-col>

                    <v-col
                      cols="4"
                      align="center"
                    >
                      <p :class="`text-h6 text-${mapKDAToColor(Number(getKDA(champion)))}`">
                        {{ getKDA(champion) }}
                      </p>

                      <p class="text-caption">
                        KDA
                      </p>
                    </v-col>
                  </v-row>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-row>
  </v-container>
</template>

<style scoped>
.scroll-list {
  height: 310px;
  overflow-y: auto
}
</style>
