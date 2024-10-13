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
import { championIdsToTitles } from '~/helpers/championIds'
import { mapKDAToColor } from '~/helpers/kdaColors'
import { queueTypes } from '~/helpers/queueTypes'
import { regionColors } from '~/helpers/regionColors'
import { proRegionToSelectRegion } from '~/helpers/regions'
import { calculateTotalLP } from '~/helpers/totalLP'
import { fullUrl } from '~/helpers/url'
import type { IAccount } from '~/models/account'
import type { ILeagueEntry } from '~/models/leagueEntry'
import type { IMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'

interface IChampionHistory {
  championId: number
  games: number
  wins: number
  loses: number
  kills: number
  deaths: number
  assists: number
}

const route = useRoute()
const { smAndDown, mobile } = useDisplay()

const storageStore = useStorageStore()
const { teamImages, rankIcons, championIcons } = storeToRefs(storageStore)

const proStore = useProPlayerStore()
const { liveStreams, notLiveStreams } = storeToRefs(proStore)

const accountStore = useAccountStore()
const restStore = useRestStore()

const player = ref<IProPlayer | null>(null)
const loading = ref(false)
const proAccounts = ref<{ account: IAccount, leagueEntry: ILeagueEntry | null }[]>([])
const lastGames = ref<IMatchData[]>([])

onMounted(async () => {
  loading.value = true

  proStore.getLiveStreams()
  proStore.getNotLiveStreams()

  const team = (route.params.team as string).toUpperCase()
  const playerName = route.params.player as string

  player.value = await proStore.getPlayerFromTeam(team, playerName)

  if (player.value) {
    const region = proRegionToSelectRegion[player.value.region]

    const promises = player.value.puuid.map(async puuid => await accountStore.getAccount(puuid, region, false))
    const accounts = (await Promise.all(promises)).filter(account => account !== null) as IAccount[]

    accounts.forEach(account => getLastGames(account))

    const leagueEntryPromises = accounts.map(async account => await restStore.getLeagueEntryBySummonerId(account.id, account.region))
    const leagueEntries = await Promise.all(leagueEntryPromises)

    proAccounts.value = accounts.map((account) => {
      const leagueEntry = leagueEntries.flat().find(e => e.queueType === 'RANKED_SOLO_5x5' && e.summonerId === account.id) || null

      if (leagueEntry)
        storageStore.getRankIcon(leagueEntry.tier.toLowerCase())

      return { account, leagueEntry }
    }).sort((a, b) => calculateTotalLP(b.leagueEntry) - calculateTotalLP(a.leagueEntry))

    storageStore.getTeamImages(player.value.region, team)
  }

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

async function getLastGames(account: IAccount) {
  const requestQueueType = queueTypes.SOLOQ

  const optionalKeys = {
    count: 20,
    queue: requestQueueType.id,
    type: requestQueueType.name,
    startTime: Math.floor(new Date(new Date().getFullYear(), 0, 1).getTime() / 1000),
  }

  const matchIds = await restStore.getAccountMatchHistory(account, optionalKeys)

  const promises = matchIds.map(async matchId => await restStore.getMatchData(matchId))
  const matchData = (await Promise.all(promises))
    .filter(item => item !== null)
    .sort((a, b) => b.info.gameStartTimestamp.seconds - a.info.gameStartTimestamp.seconds)

  lastGames.value.push(...matchData)

  const playerChampions = matchData.map(match => match.info.participants.find(participant => participant.puuid === account.puuid)!.championId)
  playerChampions.forEach(championId => storageStore.getChampionIcon(championId))
}

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

const mapChampionHistory = computed(() => {
  if (!player.value)
    return []

  // eslint-disable-next-line vue/no-side-effects-in-computed-properties
  return lastGames.value
    .sort((a, b) => b.info.gameStartTimestamp.seconds - a.info.gameStartTimestamp.seconds)
    .slice(0, 20)
    .reduce((acc, game) => {
      const participant = game.info.participants.find(participant => player.value!.puuid.includes(participant.puuid))!

      let champion = acc.find(champ => champ.championId === participant.championId)

      if (!champion) {
        champion = {
          championId: participant.championId,
          games: 0,
          wins: 0,
          loses: 0,
          kills: 0,
          deaths: 0,
          assists: 0,
        }
        acc.push(champion)
      }

      champion.games++
      champion.kills += participant.kills
      champion.deaths += participant.deaths
      champion.assists += participant.assists

      if (participant.win) {
        champion.wins++
      }
      else {
        champion.loses++
      }

      return acc
    }, [] as IChampionHistory[])
    .sort((a, b) => b.games - a.games)
})

function getKDA(champion: IChampionHistory) {
  const kda = (champion.kills + champion.assists) / champion.deaths

  return kda.toFixed(2)
}

function getWinRatio(champion: IChampionHistory) {
  const winRatio = champion.wins / champion.games

  return (winRatio * 100).toFixed(2)
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
      <v-card v-if="loading">
        <v-skeleton-loader
          type="card"
          width="80%"
          class="mx-auto my-8"
        />
      </v-card>

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
                :src="teamImages[player.team]?.[player.player.toLowerCase()]"
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
                          :src="rankIcons[account.leagueEntry.tier.toLowerCase()]"
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
              v-if="lastGames.length"
              cols="12"
              md="5"
              :order="smAndDown
                ? 1
                : 2"
              class="mb-6"
            >
              <span class="text-h5 ml-5">
                {{ $t('proPlayers.lastGames', {"games": lastGames.length > 20
                  ? 20
                  : lastGames.length}) }}
              </span>

              <v-list
                class="scroll-list"
                lines="two"
              >
                <v-list-item
                  v-for="champion in mapChampionHistory"
                  :key="champion.championId"
                >
                  <template #prepend>
                    <v-avatar
                      size="45"
                    >
                      <v-img
                        :src="championIcons[champion.championId]"
                        lazy-src="~/assets/default.png"
                      />
                    </v-avatar>
                  </template>

                  <v-row align="center">
                    <v-col cols="4">
                      <p class="text-h6">
                        {{ championIdsToTitles[champion.championId] }}
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
