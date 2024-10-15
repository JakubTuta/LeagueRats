<script setup lang="ts">
const route = useRoute()

const championStore = useChampionStore()
const { champions, championStats, championMatches } = storeToRefs(championStore)

const storageStore = useStorageStore()
const { championIcons } = storeToRefs(storageStore)

const champion = ref<{ id: number, title: string, value: string } | null>(null)
const loading = ref(false)
const secondaryLoading = ref(false)

onMounted(async () => {
  loading.value = true

  if (!Object.keys(champions.value).length) {
    await championStore.getChampions()
  }

  loading.value = false
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
  if (newChampion) {
    secondaryLoading.value = true

    const promises = [
      storageStore.getChampionIcon(newChampion.id),
      championStore.getChampionStats(newChampion.id),
      championStore.getChampionMatches(newChampion.id),
    ]
    await Promise.all(promises)

    secondaryLoading.value = false
  }
}, { immediate: true })
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
      <v-card-title
        align="center"
      >
        <v-avatar
          align="center"
          size="130"
          :image="championIcons[champion.id]"
        />

        <p class="text-h4 mt-2">
          {{ champion.title }}
        </p>
      </v-card-title>

      <v-spacer class="my-2" />

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
        v-else-if="!secondaryLoading && !championMatches[champion.id].length"
        align="center"
      >
        <span class="text-h6">
          {{ $t('champion.noMatches') }}
        </span>
      </v-card-text>

      <v-card-text
        v-else-if="!secondaryLoading && championMatches[champion.id].length"
      >
        <span
          style="width: 100%; display: flex; justify-content: center;"
          class="text-h6"
        >
          {{ championStats[champion.id] }}
        </span>

        <v-divider class="mb-4 mt-2" />

        <ProChampionHistory
          v-for="match in championMatches[champion.id]"
          :key="match.match.metadata.matchId"
          class="mt-5"
          :player="match.player"
          :match="match.match"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>
