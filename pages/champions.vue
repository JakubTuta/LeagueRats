<script setup lang="ts">
import { useDisplay } from 'vuetify';

const { height } = useDisplay()

const championStore = useChampionStore()
const { champions } = storeToRefs(championStore)

const storageStore = useStorageStore()
const { championIcons } = storeToRefs(storageStore)

const loading = ref(false)

onMounted(async () => {
  loading.value = true

  if (!Object.keys(champions.value).length) {
    await championStore.getChampions()
  }

  await storageStore.getAllChampionIcons()

  loading.value = false
})

const sortedChampions = computed(() => {
  return Object.entries(champions.value).sort((a, b) => {
    return a[1].value.localeCompare(b[1].value, 'en', { sensitivity: 'base' })
  }).map(item => ({ id: item[0], title: item[1].title, value: item[1].value }))
})
</script>

<template>
  <v-container>
    <v-card v-if="loading">
      <v-skeleton-loader
        type="image"
        width="80%"
        class="mx-auto my-8"
      />
    </v-card>

    <v-card v-else>
      <v-card-title class="text-h5">
        {{ $t('navbar.champions') }}
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-row :style="`overflow-y: auto; height: ${height - 220}px`">
          <v-col
            v-for="champion in sortedChampions"
            :key="champion.id"
            cols="6"
            sm="4"
            md="3"
            align="center"
            class="my-2"
          >
            <v-card
              variant="flat"
              :to="`/champion/${champion.value}`"
            >
              <v-card-text class="my-1">
                <v-avatar
                  size="90"
                  :image="championIcons[Number(champion.id)]"
                />

                <p class="text-h6 mt-1">
                  {{ champion.title }}
                </p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>
