<script setup lang="ts">
import { useDisplay } from 'vuetify'
import type { IMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'

const route = useRoute()
const { height } = useDisplay()
const { t } = useI18n()

const championStore = useChampionStore()
const { champions, championStats, championMatches } = storeToRefs(championStore)

const appStore = useAppStore()
const { loading: appLoading } = storeToRefs(appStore)

const storageStore = useStorageStore()

const champion = ref<{ id: number, title: string, value: string } | null>(null)
const loading = ref(true)
const secondaryLoading = ref(false)
const loadedGames = ref<{ player: IProPlayer, match: IMatchData }[]>([])
const selectedPosition = ref('ALL')
const selectedEnemy = ref({ id: 0, title: t('champion.enemyAll'), value: 'ALL' })

const gamesAmount = 10
const has2SecondsPassed = useTimeout(2000)

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

const sortedChampions = computed(() => {
  if (!Object.keys(champions.value).length) {
    return []
  }

  return Object.entries(champions.value).sort((a, b) => {
    return a[1].value.localeCompare(b[1].value, 'en', { sensitivity: 'base' })
  }).map(item => ({ id: item[0], title: item[1].title, value: item[1].value }))
})

const enemyItems = computed(() => {
  const mappedEnemies: { id: number, title: string, value: string }[] = [
    {
      id: 0,
      title: t('champion.enemyAll'),
      value: 'ALL',
    },
  ]

  if (champion.value) {
    for (const item of Object.values(sortedChampions.value)) {
      if (Number(item.id) === champion.value.id) {
        continue
      }

      mappedEnemies.push({
        id: Number(item.id),
        title: item.title,
        value: item.value,
      })
    }
  }

  return mappedEnemies
})

watch(champions, (newChampions) => {
  if (!Object.keys(newChampions).length) {
    return
  }

  for (const [id, value] of Object.entries(newChampions)) {
    if (value.value.toLowerCase() === String(route.params.champion).toLowerCase()) {
      champion.value = { id: Number(id), title: value.title, value: value.value }
      break
    }
  }

  loading.value = false
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

  const lane = selectedPosition.value === 'ALL'
    ? null
    : selectedPosition.value
  const versus = !selectedEnemy.value || selectedEnemy.value.value === 'ALL'
    ? null
    : selectedEnemy.value.id.toString()

  const response = await championStore.getChampionMatches(champion.value!.id, gamesAmount, lane, versus)
  loadedGames.value = championMatches.value[champion.value!.id]

  if (response.length === 0 || loadedGames.value.length >= championStats.value[champion.value!.id].games) {
    done('empty')

    return
  }

  done('done')
}

watch(selectedPosition, async (value) => {
  championStore.clearChampionMatches(champion.value!.id)

  const lane = value === 'ALL'
    ? null
    : value
  const versus = !selectedEnemy.value || selectedEnemy.value.value === 'ALL'
    ? null
    : selectedEnemy.value.id.toString()

  await championStore.getChampionMatches(champion.value!.id, gamesAmount, lane, versus)
  loadedGames.value = championMatches.value[champion.value!.id]
})

watch(selectedEnemy, async (value) => {
  championStore.clearChampionMatches(champion.value!.id)

  const lane = selectedPosition.value === 'ALL'
    ? null
    : selectedPosition.value
  const versus = !value || value.value === 'ALL'
    ? null
    : value.id.toString()

  await championStore.getChampionMatches(champion.value!.id, gamesAmount, lane, versus)
  loadedGames.value = championMatches.value[champion.value!.id]
})
</script>

<template>
  <v-container>
    <Loader v-if="loading || appLoading" />

    <v-card v-else-if="!champion">
      <v-card-title
        align="center"
        class="text-h5 my-4"
      >
        {{ $t('champion.notFound') }}
      </v-card-title>
    </v-card>

    <v-card v-else>
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
                :src="storageStore.getChampionIcon(champion.id) || ''"
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

      <v-card-text>
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
              return-object
              :items="enemyItems"
              :label="$t('champion.enemy')"
              @click:clear="selectedEnemy.value = 'ALL'"
            />
          </v-col>
        </v-row>

        <v-divider />

        <Loader v-if="secondaryLoading" />

        <v-infinite-scroll
          v-if="championMatches[champion.id]?.length"
          :height="`${height - 435}px`"
          :empty-text="$t('champion.noMatches')"
          mode="manual"
          @load="loadGames"
        >
          <template
            v-for="game in loadedGames"
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
