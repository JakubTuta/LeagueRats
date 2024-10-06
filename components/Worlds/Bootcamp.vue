<script setup lang="ts">
import { colorForTeam } from '~/helpers/teamUniqueColors';
import { calculateTotalLP } from '~/helpers/totalLP';

const { t } = useI18n()

const proStore = useProPlayerStore()
const { bootcampAccounts } = storeToRefs(proStore)

const nextUpdateTime = ref('00:00')
const search = ref('')
const loading = ref(false)

const romanToNumber: { [key: string]: number } = {
  I: 1,
  II: 2,
  III: 3,
  IV: 4,
}

onMounted(async () => {
  if (!bootcampAccounts.value.length) {
    loading.value = true
    await proStore.getBootcampAccounts()
    loading.value = false
  }
})

const headers = computed(() => [
  {
    title: t('bootcamp.team'),
    key: 'team',
    value: 'team',
    align: 'center',
  },
  {
    title: t('bootcamp.player'),
    key: 'player',
    value: 'player',
  },
  {
    title: t('bootcamp.account'),
    key: 'account',
    value: 'account',
    sortRaw: (a: any, b: any) => {
      return a.gameName.localeCompare(b.gameName)
    },
  },
  {
    title: t('bootcamp.rank'),
    key: 'rank',
    value: 'rank',
    isSorted: true,
    sortRaw: (a: any, b: any) => {
      return calculateTotalLP(a) - calculateTotalLP(b)
    },
  },
  {
    title: t('bootcamp.totalGames'),
    key: 'totalGames',
    value: 'totalGames',
    align: 'center',
    sortRaw: (a: any, b: any) => {
      return (a.wins + a.losses) - (b.wins + b.losses)
    },
  },
  {
    title: t('bootcamp.wins'),
    key: 'wins',
    value: 'wins',
    align: 'center',
  },
  {
    title: t('bootcamp.losses'),
    key: 'losses',
    value: 'losses',
    align: 'center',
  },
  {
    title: t('bootcamp.winRate'),
    key: 'winRate',
    value: 'winRate',
    align: 'center',
    sortRaw: (a: any, b: any) => {
      return a.wins / (a.wins + a.losses) - b.wins / (b.wins + b.losses)
    },
  },
])

setInterval(getNextUpdateTime, 1000)

function getNextUpdateTime() {
  const now = new Date()
  const nextHour = new Date(now)

  nextHour.setHours(nextHour.getHours() + 1)
  nextHour.setMinutes(0)
  nextHour.setSeconds(0)

  const minutes = String(Math.floor((nextHour.getTime() - now.getTime()) / 60000)).padStart(2, '0')
  const seconds = String(Math.floor((nextHour.getTime() - now.getTime()) / 1000) % 60).padStart(2, '0')

  nextUpdateTime.value = `${minutes}:${seconds}`
}

function customFilter(_value: string, query: string, item: any) {
  const player = item.raw.player.toLowerCase()
  const team = item.raw.team.toLowerCase()

  return player.includes(query.toLowerCase()) || team.includes(query.toLowerCase())
}
</script>

<template>
  <v-card
    v-if="loading"
    variant="flat"
  >
    <v-skeleton-loader
      type="table-heading, table-row, table-row, table-row, table-row, table-row, table-row, table-row, table-row, table-tfoot"
      width="90%"
      class="mx-auto my-8"
    />
  </v-card>

  <v-card
    v-else
    variant="flat"
  >
    <v-card-title class="text-h5">
      {{ t('bootcamp.title') }}
    </v-card-title>

    <v-card-subtitle>
      {{ $t('bootcamp.nextUpdate', {"time": nextUpdateTime}) }}
    </v-card-subtitle>

    <v-row class="mx-4 mt-4">
      <v-col
        cols="12"
        sm="6"
        md="5"
      >
        <v-text-field
          v-model="search"
          :label="$t('universal.search')"
          append-inner-icon="mdi-magnify"
        />
      </v-col>
    </v-row>

    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="bootcampAccounts"
        :items-per-page="10"
        :custom-filter="customFilter"
        :search="search"
        must-sort
        :sort-by="[
          {
            'key': 'rank',
            'order': 'desc',
          },
        ]"
        :items-per-page-options="[
          {'title': '10',
           'value': 10},
        ]"
      >
        <template #item.team="{item}">
          <NuxtLink
            class="pa-1"
            style="cursor: pointer; text-decoration: none; color: inherit;"
            :to="`/team/${item.team}`"
          >
            <v-chip
              width="100px"
              :color="colorForTeam[item.team]"
            >
              {{ item.team }}
            </v-chip>
          </NuxtLink>
        </template>

        <template #item.player="{item}">
          <NuxtLink
            class="pa-1"
            style="cursor: pointer; text-decoration: none; color: inherit;"
            :to="`/player/${item.team}/${item.player}`"
          >
            {{ item.player }}
          </NuxtLink>
        </template>

        <template #item.account="{item}">
          <NuxtLink
            class="pa-1"
            style="cursor: pointer; text-decoration: none; color: inherit;"
            :to="`/account/EUW/${item.gameName}-${item.tagLine}`"
          >
            {{ item.gameName }} #{{ item.tagLine }}
          </NuxtLink>
        </template>

        <template #item.rank="{item}">
          <span
            v-if="[
              'CHALLANGER',
              'GRANDMASTER',
              'MASTER',
            ].includes(item.tier)"
          >
            {{ `${$t(`ranks.${item.tier}`)} ${item.leaguePoints}LP` }}
          </span>

          <span v-else>
            {{ `${$t(`ranks.${item.tier}`)} ${romanToNumber[item.rank]} ${item.leaguePoints}LP` }}
          </span>
        </template>

        <template #item.totalGames="{item}">
          {{ item.wins + item.losses }}
        </template>

        <template #item.winRate="{item}">
          {{ (item.wins / (item.wins + item.losses) * 100).toFixed(2) }}%
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
