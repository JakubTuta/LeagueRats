<script setup lang="ts">
import { championIds } from '~/helpers/championIds';
import type { IAccount } from '~/models/accountModel';
import type { ActiveGameModel } from '~/models/activeGame';

const props = withDefaults(defineProps<{
  game: ActiveGameModel | null
  account?: IAccount | null
}>(), {
  account: null,
})

const { game, account } = toRefs(props)

const router = useRouter()

const storageStore = useStorageStore()
const championIcons = ref<Record<number, string>>({})

const opened = ref<string[]>([])

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

watch(game, (newGame) => {
  if (!newGame)
    return

  const championId = newGame.participants.map(participant => participant.championId)

  championId.forEach(async (championId) => {
    if (!championIcons.value[championId]) {
      const championName = championIds[championId]
      championIcons.value[championId] = await storageStore.getChampionIcon(championName)
    }
  })
}, { immediate: true })

function sendToProfile(gameName: string, tagLine: string) {
  router.push(`/account/${gameName}-${tagLine}`)
}
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
          <v-list v-model:opened="opened">
            <v-list-item
              v-for="participant in team"
              :key="participant.puuid"
              @click="() => sendToProfile(participant.gameName, participant.tagLine)"
            >
              <template #prepend>
                <v-img
                  class="mr-4"
                  :src="championIcons[participant.championId]"
                  lazy-src="~/assets/default.png"
                  width="40"
                  height="40"
                />
              </template>

              <v-list-item-title
                :class="participant.puuid === account?.puuid
                  ? 'font-weight-bold'
                  : ''"
              >
                {{ participant.gameName }}

                <span class="text-subtitle-2 ml-1 text-gray">
                  #{{ participant.tagLine }}
                </span>
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
