<script setup lang="ts">
// @ts-expect-error correct path
import bannedDefault from '~/assets/banned_default.png'
import { type TApiRegions2, mapApiRegion2ToSelect } from '~/helpers/regions'
import type { IAccount } from '~/models/account'
import type { IActiveGame, IParticipant } from '~/models/activeGame'

const props = withDefaults(defineProps<{
  game: IActiveGame | null
  account?: IAccount | null
}>(), {
  account: null,
})

const { game, account } = toRefs(props)

const storageStore = useStorageStore()
const { championIcons, summonerSpellIcons, runeIcons } = storeToRefs(storageStore)

const restStore = useRestStore()
const runeStore = useRuneStore()

const team1 = ref<IParticipant[]>([])
const team2 = ref<IParticipant[]>([])

const opened = ref<string[]>([])

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

const region = computed(() => {
  if (!game.value)
    return null

  return mapApiRegion2ToSelect(game.value.platformId as TApiRegions2)
})

async function sortTeam(participants: IParticipant[]) {
  const participantIds = participants.map(participant => participant.championId)
  const teamLanes = await restStore.findChampionsPositions(participantIds)

  if (!teamLanes)
    return participants

  return participants.map((participant) => {
    let lane = teamLanes[participant.championId]

    // smite = 11
    if (participant.spell1Id === 11 || participant.spell2Id === 11)
      lane = 'JUNGLE'

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

  newGame.participants.forEach((participant) => {
    storageStore.getChampionIcon(participant.championId)
    storageStore.getSummonerSpellIcon(participant.spell1Id)
    storageStore.getSummonerSpellIcon(participant.spell2Id)
    runeStore.getRuneIcons(participant.perks)
  })

  newGame.bannedChampions.forEach((bannedChampion) => {
    if (bannedChampion.championId !== -1)
      storageStore.getChampionIcon(bannedChampion.championId)
  })
}, { immediate: true })
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
      <!-- league-blue-transparent -->
      <!-- league-red-transparent -->
      <v-card
        :color="teamIndex === 0
          ? 'rgba(35, 167, 250, 0.7)'
          : 'rgba(252, 38, 38, 0.7)'"
      >
        <v-card-title>
          {{ $t(`game.team${teamIndex + 1}`) }}
        </v-card-title>

        <v-card-text>
          <v-list
            v-model:opened="opened"
            lines="two"
            bg-color="rgba(0, 0, 0, 0)"
          >
            <v-list-item
              v-for="participant in team"
              :key="participant.puuid"
              :to="participant.puuid === account?.puuid
                ? ''
                : `/account/${region}/${participant.gameName}-${participant.tagLine}`"
            >
              <template #prepend>
                <v-img
                  class="mr-4"
                  :src="championIcons[participant.championId]"
                  lazy-src="~/assets/default.png"
                  width="45"
                />
              </template>

              <v-list-item-title
                :class="participant.puuid === account?.puuid
                  ? 'font-weight-bold ml-7'
                  : 'ml-7'"
                style="display: flex; align-items: center; justify-content: space-between"
              >
                <span>
                  {{ participant.gameName }}

                  <span
                    :class="teamIndex === 0
                      ? 'text-subtitle-2 text-grey-darken-3 ml-1'
                      : 'text-subtitle-2 text-grey-lighten-3 ml-1'"
                  >
                    #{{ participant.tagLine }}
                  </span>
                </span>

                <v-btn
                  icon
                  variant="text"
                  @click.prevent
                >
                  <v-img
                    :src="runeIcons[participant.perks.perkIds[0]]"
                    lazy-src="~/assets/default.png"
                    width="40"
                  />

                  <v-menu
                    activator="parent"
                    :close-on-content-click="false"
                    location="start"
                  >
                    <AccountRuneTable :runes="participant.perks" />
                  </v-menu>
                </v-btn>
              </v-list-item-title>

              <v-list-item-action>
                <v-img
                  :src="summonerSpellIcons[participant.spell1Id]"
                  style="position: absolute; left: 70px; top: 20%"
                  lazy-src="~/assets/default.png"
                  width="20"
                  height="20"
                />

                <v-img
                  :src="summonerSpellIcons[participant.spell2Id]"
                  style="position: absolute; left: 70px; bottom: 20%"
                  lazy-src="~/assets/default.png"
                  width="20"
                  height="20"
                />
              </v-list-item-action>
            </v-list-item>
          </v-list>

          <v-row
            v-if="game?.bannedChampions.length"
            class="text-h6 ma-2"
            align="center"
            justify-space-between
          >
            {{ $t('game.bannedChampions') }}
          </v-row>

          <v-row
            v-if="game?.bannedChampions.length"
            class="ma-2"
          >
            <v-avatar
              v-for="bannedChampion in game.bannedChampions.filter(bannedChampion => bannedChampion.teamId === teamIds[teamIndex])"
              :key="bannedChampion.championId"
              rounded="0"
              class="mr-4"
              width="30"
              height="30"
            >
              <v-img
                :src="bannedChampion.championId === -1
                  ? bannedDefault
                  : championIcons[bannedChampion.championId]"
                lazy-src="~/assets/default.png"
              />
            </v-avatar>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
