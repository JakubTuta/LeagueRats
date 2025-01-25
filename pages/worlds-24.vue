<script setup lang="ts">
import { useDisplay } from 'vuetify'

const { t } = useI18n()
const { mobile } = useDisplay()

const selectedTab = ref('teams')

const tabs = computed(() => [
  {
    title: t('proPlayers.teams'),
    value: 'teams',
  },
  {
    title: 'Bootcamp',
    value: 'bootcamp',
  },
])
</script>

<template>
  <v-container
    :class="mobile
      ? ''
      : 'fill-height'"
  >
    <v-row
      class="pa-3"
      align="center"
      justify="center"
    >
      <v-card>
        <v-card-title>
          <v-tabs
            v-model="selectedTab"
            align-tabs="center"
            color="primary"
            grow
            :show-arrows="false"
            density="comfortable"
          >
            <v-tab
              v-for="tab in tabs"
              :key="tab.title"
              :value="tab.value"
              size="default"
            >
              {{ tab.title }}
            </v-tab>
          </v-tabs>
        </v-card-title>

        <v-card-text>
          <WorldsTeams v-if="selectedTab === 'teams'" />

          <WorldsBootcamp v-if="selectedTab === 'bootcamp'" />
        </v-card-text>
      </v-card>
    </v-row>
  </v-container>
</template>
