<script setup lang="ts">
import { championIdsToTitles } from '~/helpers/championIds';
import type { IChampionMastery } from '~/models/championMastery';

const props = defineProps<{
  champions: IChampionMastery[]
  loading: boolean
}>()

const { champions, loading } = toRefs(props)

const storageStore = useStorageStore()
const { championIcons } = storeToRefs(storageStore)

const loadedChampions = ref<IChampionMastery[]>([])

watch(champions, (newChampions) => {
  if (!newChampions.length)
    return

  loadedChampions.value = newChampions.slice(0, 10)

  newChampions.forEach((champion) => {
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

  loadedChampions.value.push(...newChampions)

  done('ok')
}
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
        height="70vh"
        :items="loadedChampions"
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
