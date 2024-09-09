<script setup lang="ts">
import { useDisplay } from 'vuetify';
import { championIdsToTitles } from '~/helpers/championIds';
import type { IChampionMastery } from '~/models/championMastery';

const props = defineProps<{
  champions: IChampionMastery[]
  loading: boolean
}>()

const { champions, loading } = toRefs(props)

const { height } = useDisplay()

const storageStore = useStorageStore()
const { championIcons } = storeToRefs(storageStore)

const loadedChampions = ref<IChampionMastery[]>([])

watch(champions, (newChampions) => {
  if (!newChampions.length)
    return

  loadedChampions.value = newChampions.slice(0, 10)

  loadedChampions.value.forEach((champion) => {
    storageStore.getChampionIcon(champion.championId)
  })
})

function formatNumber(number: number) {
  const str = String(number)
  let result = ''
  let count = 0

  for (let i = str.length - 1; i >= 0; i--) {
    result = str[i] + result
    count++

    if (count % 3 === 0 && i !== 0) {
      result = ` ${result}`
    }
  }

  return result
}

function loadChampions({ done }: { done: (status: string) => void }) {
  const newChampions = champions.value.slice(loadedChampions.value.length, loadedChampions.value.length + 10)

  if (!newChampions.length) {
    done('empty')

    return
  }

  newChampions.forEach((champion) => {
    storageStore.getChampionIcon(champion.championId)
  })
  loadedChampions.value.push(...newChampions)

  done('ok')
}

const scrollHeight = computed(() => {
  if (height.value < 1000)
    return '50vh'
  else if (height.value < 1250)
    return '55vh'
  else if (height.value < 1500)
    return '60vh'
  else if (height.value < 1750)
    return '65vh'
  else if (height.value < 2000)
    return '70vh'
  else
    return '75vh'
})
</script>

<template>
  <v-row
    v-if="!champions.length && !loading"
    class="text-h5 my-4"
    justify="center"
  >
    {{ $t('profile.rank.noRank') }}
  </v-row>

  <v-row
    v-else-if="champions.length && !loading"
    justify="center"
  >
    <v-col cols="10">
      <v-infinite-scroll
        :height="scrollHeight"
        @load="loadChampions"
      >
        <template
          v-for="champion in loadedChampions"
          :key="champion.championId"
        >
          <v-list-item class="my-1">
            <v-list-item-title class="text-h6">
              {{ championIdsToTitles[champion.championId] }}
            </v-list-item-title>

            <v-list-item-subtitle>
              {{ formatNumber(champion.championPoints) }}
            </v-list-item-subtitle>

            <template #prepend>
              <v-avatar
                rounded="0"
                size="70"
              >
                <v-img
                  :src="championIcons[champion.championId]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </template>
          </v-list-item>
        </template>
      </v-infinite-scroll>
    </v-col>
  </v-row>
</template>
