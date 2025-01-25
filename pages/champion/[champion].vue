<script setup lang="ts">
import { useDisplay } from 'vuetify'
import type { IMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'

const route = useRoute()
const { height } = useDisplay()
const { t } = useI18n()

const championStore = useChampionStore()
const { champions, championStats, championMatches } = storeToRefs(championStore)

const storageStore = useStorageStore()
const { championIcons } = storeToRefs(storageStore)

const champion = ref<{ id: number, title: string, value: string } | null>(null)
const loading = ref(false)
const secondaryLoading = ref(false)
const loadedGames = ref<{ player: IProPlayer, match: IMatchData }[]>([])
const selectedPosition = ref('ALL')
const selectedEnemy = ref('ALL')

const gamesAmount = 10
const has2SecondsPassed = useTimeout(2000)

onMounted(async () => {
  loading.value = true

  if (!Object.keys(champions.value).length) {
    await championStore.getChampions()
  }

  await storageStore.getAllChampionIcons()

  loading.value = false
})

const positionItems = computed(() => [
  {
    title: t('positions.ALL'),
    value: 'ALL',
  },
  {
    title: t('positions.TOP'),
    value: 'TOP',
  },
  {
    title: t('positions.JUNGLE'),
    value: 'JUNGLE',
  },
  {
    title: t('positions.MIDDLE'),
    value: 'MIDDLE',
  },
  {
    title: t('positions.BOTTOM'),
    value: 'BOTTOM',
  },
  {
    title: t('positions.UTILITY'),
    value: 'UTILITY',
  },
])

const enemyItems = computed(() => {
  const mappedEnemies: { id: number, title: string, value: string }[] = [
    {
      id: 0,
      title: t('champion.enemyAll'),
      value: 'ALL',
    },
  ]

  if (champion.value) {
    for (const [id, value] of Object.entries(champions.value)) {
      if (value.value.toLowerCase() === champion.value.value.toLowerCase()) {
        continue
      }

      mappedEnemies.push({
        id: Number(id),
        title: value.title,
        value: value.value,
      })
    }
  }

  return mappedEnemies
})

const filterGamesByPosition = computed(() => {
  if (selectedPosition.value === 'ALL') {
    return loadedGames.value
  }

  return loadedGames.value.filter((game) => {
    const playerParticipant = game.match.info.participants.find(participant => game.player.puuid.includes(participant.puuid))

    return playerParticipant?.teamPosition === selectedPosition.value
  })
})

const filterGamesByEnemy = computed(() => {
  if (selectedEnemy.value === 'ALL') {
    return loadedGames.value
  }

  const enemyChampion = enemyItems.value.find(enemy => enemy.value === selectedEnemy.value)

  if (!enemyChampion) {
    return loadedGames.value
  }

  return loadedGames.value.filter((game) => {
    const playerParticipant = game.match.info.participants.find(participant => game.player.puuid.includes(participant.puuid))
    const enemyParticipant = game.match.info.participants.find(participant => playerParticipant?.teamPosition === participant.teamPosition && participant.puuid !== playerParticipant?.puuid)

    return enemyParticipant?.championId === enemyChampion.id
  })
})

const filterGames = computed(() => {
  return filterGamesByPosition.value.filter(game => filterGamesByEnemy.value.includes(game))
})

watch(champions, (newChampions) => {
  if (Object.keys(newChampions).length) {
    loading.value = true

    for (const [id, value] of Object.entries(newChampions)) {
      if (value.value.toLowerCase() === String(route.params.champion).toLowerCase()) {
        champion.value = { id: Number(id), title: value.title, value: value.value }
        break
      }
    }

    loading.value = false
  }
}, { immediate: true })

watch(champion, async (newChampion) => {
  if (!newChampion?.id || secondaryLoading.value)
    return

  secondaryLoading.value = true

  const promises = [
    championStore.getChampionStats(newChampion.id),
    championStore.getChampionMatches(newChampion.id, gamesAmount),
  ]
  await Promise.all(promises)

  if (championMatches.value[newChampion.id]?.length)
    loadedGames.value = championMatches.value[newChampion.id].slice(0, gamesAmount)

  secondaryLoading.value = false
}, { immediate: true })

async function loadGames({ done }: { done: (status: string) => void }) {
  if (!has2SecondsPassed.value) {
    done('done')

    return
  }

  await championStore.getChampionMatches(champion.value!.id, gamesAmount)
  loadedGames.value = championMatches.value[champion.value!.id]

  if (loadedGames.value.length >= championStats.value[champion.value!.id].games) {
    done('empty')

    return
  }

  done('done')
}

function againstAutocompleteFocusChange(value: boolean) {
  if (value && selectedEnemy.value === 'ALL') {
    selectedEnemy.value = ''
  }
  else if (!value && !selectedEnemy.value) {
    selectedEnemy.value = 'ALL'
  }
}
</script>

<template>
  <v-container>
    <v-card v-if="loading">
      <v-skeleton-loader
        type="card"
        width="80%"
        class="mx-auto my-8"
      />
    </v-card>

    <v-card v-else-if="!loading && !champion">
      <v-card-title
        align="center"
        class="text-h5 my-4"
      >
        {{ $t('champion.notFound') }}
      </v-card-title>
    </v-card>

    <v-card v-else-if="!loading && champion">
      <v-card-title>
        <v-row
          style="display: flex; justify-content: space-between; align-items: start"
          class="mt-0"
        >
          <v-col
            cols="0"
            sm="2"
          />

          <v-col
            cols="12"
            sm="4"
            align="center"
          >
            <v-avatar
              align="center"
              size="100"
            >
              <v-img
                :src="championIcons[champion.id]"
                lazy-src="~assets/default.png"
              />
            </v-avatar>

            <p class="text-h5 mt-2">
              {{ champion.title }}
            </p>
          </v-col>

          <v-col
            v-if="!secondaryLoading && championMatches[champion.id]?.length"
            cols="12"
            sm="4"
            style="display: flex; align-items: center; justify-content: center"
          >
            <div>
              <PieChart
                :wins="championStats[champion.id]?.wins || 0"
                :losses="championStats[champion.id]?.losses || 0"
                :size="100"
              />
            </div>

            <div class="text-subtitle-1 ml-5">
              <p class="text-light-blue">
                {{ `${$t('profile.rank.wins')}: ${championStats[champion.id].wins}` }}
              </p>

              <p class="text-red">
                {{ `${$t('profile.rank.losses')}: ${championStats[champion.id].losses}` }}
              </p>

              <p>
                {{ `${$t('profile.rank.winRate')}: ${(championStats[champion.id].wins / championStats[champion.id].games * 100).toFixed(0)}%` }}
              </p>
            </div>
          </v-col>

          <v-col
            cols="0"
            sm="2"
          />
        </v-row>
      </v-card-title>

      <v-card-text
        v-if="secondaryLoading"
      >
        <v-skeleton-loader
          type="table-heading, table-row@8, table-tfoot"
          width="80%"
          class="mx-auto my-8"
        />
      </v-card-text>

      <v-card-text
        v-else-if="!secondaryLoading && !championMatches[champion.id]?.length"
        align="center"
      >
        <span class="text-h6">
          {{ $t('champion.noMatches') }}
        </span>
      </v-card-text>

      <v-card-text v-else-if="!secondaryLoading && championMatches[champion.id]?.length">
        <v-row class="mx-2 mt-0">
          <v-col cols="6">
            <v-select
              v-model="selectedPosition"
              :items="positionItems"
              :label="$t('champion.position')"
            />
          </v-col>

          <v-col cols="6">
            <v-autocomplete
              v-model="selectedEnemy"

              clearable
              auto-select-first
              :items="enemyItems"
              :label="$t('champion.enemy')"
              @click:clear="selectedEnemy = 'ALL'"
              @update:focused="againstAutocompleteFocusChange"
            />
          </v-col>
        </v-row>

        <v-divider />

        <v-infinite-scroll
          :height="`${height - 435}px`"
          empty-text=""
          @load="loadGames"
        >
          <template
            v-for="game in filterGames"
            :key="game.match.metadata.matchId"
          >
            <ProChampionHistory
              class="mb-4"
              :player="game.player"
              :match="game.match"
            />
          </template>
        </v-infinite-scroll>
      </v-card-text>
    </v-card>
  </v-container>
</template>
