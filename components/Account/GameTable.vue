<script setup lang="ts">
import { championIds } from '~/helpers/championIds';
import type { IAccount } from '~/models/accountModel';
import type { ActiveGameModel, IParticipant } from '~/models/activeGame';

const props = withDefaults(defineProps<{
  game: ActiveGameModel | null
  account?: IAccount | null
}>(), {
  account: null,
})

const { game, account } = toRefs(props)

const router = useRouter()

const storageStore = useStorageStore()
const restStore = useRestStore()

const championIcons = ref<Record<number, string>>({})
const team1 = ref<IParticipant[]>([])
const team2 = ref<IParticipant[]>([])

const opened = ref<string[]>([])

const teamColors = ['blue', 'red']

const championLanesMap: { [key: string]: number } = {
  TOP: 1,
  JUNGLE: 2,
  MIDDLE: 3,
  BOTTOM: 4,
  UTILITY: 5,
}

const teamIds = computed(() => {
  if (!game.value)
    return []

  return Array.from(new Set(game.value.participants.map(participant => participant.teamId)))
})

async function sortTeam(participants: IParticipant[]) {
  const participantIds = participants.map(participant => participant.championId)
  const teamLanes = await restStore.findChampionsPositions(participantIds)

  if (!teamLanes)
    return participants

  return participants.map((participant) => {
    const lane = teamLanes[participant.championId]

    return {
      ...participant,
      lane,
    }
  }).sort((a, b) => championLanesMap[a.lane] - championLanesMap[b.lane])
}

watch(game, async (newGame) => {
  if (!newGame)
    return

  let tmpTeam1 = newGame.participants.filter(participant => participant.teamId === teamIds.value[0])
  let tmpTeam2 = newGame.participants.filter(participant => participant.teamId === teamIds.value[1])

  if (game.value?.gameMode === 'CLASSIC') {
    tmpTeam1 = await sortTeam(tmpTeam1)
    tmpTeam2 = await sortTeam(tmpTeam2)
  }

  team1.value = tmpTeam1
  team2.value = tmpTeam2
}, { immediate: true })

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
