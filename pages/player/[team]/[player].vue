<script setup lang="ts">
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
import { selectRegionToProRegion } from '~/helpers/regions'
import type { IAccount } from '~/models/account'
import type { ILeagueEntry } from '~/models/leagueEntry'
import type { IProPlayer } from '~/models/proPlayer'

const route = useRoute()

const storageStore = useStorageStore()
const { teamImages, rankIcons } = storeToRefs(storageStore)

const proStore = useProPlayerStore()
const accountStore = useAccountStore()
const restStore = useRestStore()

const player = ref<IProPlayer | null>(null)
const loading = ref(false)
const proAccounts = ref<{ account: IAccount, leagueEntry: ILeagueEntry | null }[]>([])

onMounted(async () => {
  loading.value = true

  const team = (route.params.team as string).toUpperCase()
  const playerName = route.params.player as string

  player.value = await proStore.getPlayerFromTeam(team, playerName)

  if (player.value) {
    const promises = player.value.puuid.map(async puuid => await accountStore.getAccount(puuid, player.value!.region, false))
    const accounts = (await Promise.all(promises)).filter(account => account !== null) as IAccount[]

    const leagueEntryPromises = accounts.map(async account => await restStore.getLeagueEntryBySummonerId(account.id, account.region))
    const leagueEntries = await Promise.all(leagueEntryPromises)

    proAccounts.value = accounts.map((account) => {
      const leagueEntry = leagueEntries.flat().find(e => e.queueType === 'RANKED_SOLO_5x5' && e.summonerId === account.id) || null

      if (leagueEntry)
        storageStore.getRankIcon(leagueEntry.tier.toLowerCase())

      return { account, leagueEntry }
    })

    const proRegion = selectRegionToProRegion[player.value.region]

    if (proRegion)
      storageStore.getTeamImages(proRegion, team)
  }

  loading.value = false
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
</script>

<template>
  <div
    style="display: flex;
    justify-content: center;
    align-items: center;
    height: 90%;"
  >
    <v-container>
      <v-card v-if="loading">
        <v-skeleton-loader
          type="card"
          width="90%"
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

        <v-card-text class="mt-4">
          <span class="text-h5 ml-5">
            {{ $t('proPlayers.accounts') }}
          </span>

          <p
            v-if="!proAccounts.length"
            class="text-subtitle-1 ma-4"
          >
            {{ $t('proPlayers.noAccounts') }}
          </p>

          <v-list
            v-else
            lines="three"
          >
            <v-list-item
              v-for="account in proAccounts"
              :key="account.account.puuid"
              :to="`/account/${account.account.region}/${account.account.gameName}-${account.account.tagLine}`"
            >
              <template
                v-if="account.leagueEntry"
                #prepend
              >
                <div>
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
        </v-card-text>
      </v-card>
    </v-container>
  </div>
</template>
