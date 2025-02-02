<script setup lang="ts">
import { useDisplay } from 'vuetify'

const { height } = useDisplay()

const championStore = useChampionStore()
const { champions } = storeToRefs(championStore)

const appStore = useAppStore()
const { loading: appLoading } = storeToRefs(appStore)

const storageStore = useStorageStore()

const search = ref('')

const sortedChampions = computed(() => {
  return Object.entries(champions.value).sort((a, b) => {
    return a[1].value.localeCompare(b[1].value, 'en', { sensitivity: 'base' })
  }).map(item => ({ id: item[0], title: item[1].title, value: item[1].value }))
})

const filteredChampions = computed(() => {
  if (!search.value)
    return sortedChampions.value

  return sortedChampions.value.filter((champion) => {
    return champion.title.toLowerCase().includes(search.value.toLowerCase())
  })
})
</script>

<template>
  <v-container>
    <Loader v-if="appLoading" />

    <v-card v-else>
      <v-card-title class="text-h5">
        {{ $t('navbar.champions') }}
      </v-card-title>

      <v-row justify="end">
        <v-col
          cols="12"
          sm="6"
          md="4"
        >
          <v-text-field
            v-model="search"
            class="mx-4"
            :label="$t('universal.search')"

            dense
            outlined
            clearable
            prepend-inner-icon="mdi-magnify"
          />
        </v-col>
      </v-row>

      <v-divider />

      <v-card-text>
        <v-row :style="`overflow-y: auto; height: ${height - 300}px`">
          <v-col
            v-for="champion in filteredChampions"
            :key="champion.id"
            cols="4"
            sm="3"
            md="2"
            align="center"
            class="my-2"
          >
            <v-card
              variant="flat"
              :to="`/champion/${champion.value.toLowerCase()}`"
            >
              <v-card-text class="my-1">
                <v-avatar
                  size="80"
                >
                  <v-img
                    :src="storageStore.getChampionIcon(champion.id)"
                    lazy-src="~/assets/default.png"
                  />
                </v-avatar>

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
