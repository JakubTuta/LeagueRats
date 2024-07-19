<script setup lang="ts">
import type { ActiveGameModel } from '~/models/activeGame';

const props = defineProps<{
  game: ActiveGameModel | null
}>()

const { game } = toRefs(props)

const teamColors = ['blue', 'red']

const teamIds = computed(() => {
  if (!game.value)
    return []

  return Array.from(new Set(game.value.participants.map(participant => participant.teamId)))
})

const team1 = computed(() => {
  if (!game.value || teamIds.value.length !== 2)
    return []

  return game.value.participants.filter(participant => participant.teamId === teamIds.value[0])
})

const team2 = computed(() => {
  if (!game.value || teamIds.value.length !== 2)
    return []

  return game.value.participants.filter(participant => participant.teamId === teamIds.value[1])
})
</script>

<template>
  <v-row>
    <v-col
      v-for="(team, teamIndex) in [
        team1,
        team2,
      ]"
      :key="teamIndex"
      cols="12"
      md="6"
    >
      <v-card
        :color="teamColors[teamIndex]"
        variant="tonal"
      >
        <v-card-title>
          {{ $t(`game.team${teamIndex + 1}`) }}
        </v-card-title>

        <v-card-text>
          <v-list>
            <v-list-item
              v-for="participant in team"
              :key="participant.puuid"
              @click="() => { }"
            >
              <v-list-item-title>
                {{ participant.gameName }}

                <v-span class="text-subtitle-2 ml-1 text-gray">
                  #{{ participant.tagLine }}
                </v-span>
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
