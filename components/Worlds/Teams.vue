<script setup lang="ts">
import { teamFullName } from '~/helpers/regions'

const storageStore = useStorageStore()

const teamsPerRegion = computed(() => ({
  LEC: ['G2', 'FNC', 'MKOI'],
  LCS: ['FLY', 'TL', '100'],
  LCK: ['HLE', 'GENG', 'DK', 'T1'],
  LPL: ['BLG', 'TES', 'LNG', 'WBG'],
}))
</script>

<template>
  <v-list lines="three">
    <v-list-item
      v-for="([
        region,
        teams,
      ]) in Object.entries(teamsPerRegion)"
      :key="region"
      class="mb-2"
    >
      <span class="text-h5">
        {{ region }}
      </span>

      <v-row class="mt-1">
        <v-col
          v-for="team in teams"
          :key="team"
          cols="6"
          md="3"
        >
          <v-card
            elevation="0"
            :to="`/team/${team}`"
            align="center"
          >
            <v-avatar
              size="100"
              rounded="0"
              class="pa-2"
            >
              <v-img
                :src="storageStore.getTeamLogo(team)"
                aspect-ratio="1"
                cover
              />
            </v-avatar>

            <v-card-title>
              {{ teamFullName[team] }}
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>

      <v-divider class="mt-4" />
    </v-list-item>
  </v-list>
</template>
