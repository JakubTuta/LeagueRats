<script setup lang="ts">
import { useDisplay } from 'vuetify'
import { mapKDAToColor } from '~/helpers/kdaColors'
import { mouseButton } from '~/helpers/mouse'
import { queueIdToType } from '~/helpers/queueTypes'
import type { TApiRegions2 } from '~/helpers/regions'
import { mapApiRegion2ToSelect } from '~/helpers/regions'
import type { IAccount } from '~/models/account'
import type { IMatchData, IParticipantStats } from '~/models/matchData'

const props = defineProps<{
  account: IAccount | null
  game: IMatchData
}>()

const { account, game } = toRefs(props)

const { t, locale } = useI18n()
const router = useRouter()
const { xs } = useDisplay()

const storageStore = useStorageStore()
const { championIcons, runeIcons, itemIcons } = storeToRefs(storageStore)

const runeStore = useRuneStore()
const { runeInfo } = storeToRefs(runeStore)

const summonerSpellStore = useSummonerSpellsStore()
const { summonerSpellIcons } = storeToRefs(summonerSpellStore)

const accountStore = useAccountStore()

const team1 = ref<IParticipantStats[]>([])
const team2 = ref<IParticipantStats[]>([])
const secondaryRuneTreeId = ref(0)

const gamer = computed(() => game.value.info.participants.find(participant => participant.puuid === account.value!.puuid)!)
const isWin = computed(() => gamer.value.win)
const keyRuneId = computed(() => (gamer.value.perks.styles.find(style => style.description === 'primaryStyle')!.selections[0].perk))
const items = computed(() => [gamer.value.item0, gamer.value.item1, gamer.value.item2, gamer.value.item3, gamer.value.item4, gamer.value.item5].filter(item => item !== 0))
const minions = computed(() => gamer.value.neutralMinionsKilled + gamer.value.totalMinionsKilled)
const multikill = computed(() => {
  if (gamer.value.pentaKills)
    return 5
  else if (gamer.value.quadraKills)
    return 4
  else if (gamer.value.tripleKills)
    return 3
  else if (gamer.value.doubleKills)
    return 2
  else
    return 1
})
const teamIds = computed(() => {
  if (!game.value)
    return []

  return Array.from(new Set(game.value.info.participants.map(participant => participant.teamId)))
})
const kda = computed(() => (gamer.value.kills + gamer.value.assists) / gamer.value.deaths)
// const teamDamageDealt = computed(() => game.value.info.participants.reduce((acc, participant) => acc + participant.physicalDamageDealtToChampions + participant.magicDamageDealtToChampions + participant.trueDamageDealtToChampions, 0))
// const teamDamageTaken = computed(() => game.value.info.participants.reduce((acc, participant) => acc + participant.physicalDamageTaken + participant.magicDamageTaken + participant.trueDamageTaken, 0))
// const playerDamageDealt = computed(() => gamer.value.physicalDamageDealtToChampions + gamer.value.magicDamageDealtToChampions + gamer.value.trueDamageDealtToChampions)
// const playerDamageTaken = computed(() => gamer.value.physicalDamageTaken + gamer.value.magicDamageTaken + gamer.value.trueDamageTaken)

const mapPositions: { [key: string]: number } = {
  TOP: 1,
  JUNGLE: 2,
  MIDDLE: 3,
  BOTTOM: 4,
  UTILITY: 5,
}

watch(game, (newGame) => {
  if (!newGame)
    return

  if (teamIds.value.length === 2) {
    team1.value = newGame.info.participants.filter(participant => participant.teamId === teamIds.value[0])
    team2.value = newGame.info.participants.filter(participant => participant.teamId === teamIds.value[1])

    team1.value = team1.value.sort((a, b) => mapPositions[a.teamPosition] - mapPositions[b.teamPosition])
    team2.value = team2.value.sort((a, b) => mapPositions[a.teamPosition] - mapPositions[b.teamPosition])
  }

  game.value.info.participants.forEach((participant) => {
    storageStore.getChampionIcon(participant.championId)
  })

  storageStore.getItemIcons(items.value)

  const keyRunePath = runeInfo.value.flatMap(rune => rune.slots.flatMap(slot => slot.runes)).find(rune => rune.id === keyRuneId.value)?.icon || null

  if (keyRunePath)
    storageStore.getRuneIcons({ [keyRuneId.value]: keyRunePath })

  findSecondaryRuneTree()
}, { immediate: true })

function mapGameTime() {
  const minutes = Math.floor(game.value.info.gameDuration / 60)
  const seconds = game.value.info.gameDuration % 60

  return `${minutes}:${seconds < 10
? `0${seconds}`
: seconds}`
}

function whenWasGame() {
  const now = new Date()
  const gameDate = new Date(game.value.info.gameStartTimestamp.toDate())

  const diff = now.getTime() - gameDate.getTime()

  const diffMinutes = Math.floor(diff / 60000)

  if (diffMinutes < 60) {
    if (locale.value === 'pl') {
      if (diffMinutes === 1) {
        return 'Minutę temu'
      }
      else if (diffMinutes % 10 >= 2 && diffMinutes % 10 <= 4) {
        return `${diffMinutes} minuty temu`
      }
    }

    return t('gameHistory.minutesAgo', { time: diffMinutes })
  }

  const diffHours = Math.floor(diffMinutes / 60)

  if (diffHours < 24) {
    if (locale.value === 'pl') {
      if (diffHours === 1) {
        return 'Godzinę temu'
      }
      else if (diffHours % 10 >= 2 && diffHours % 10 <= 4) {
        return `${diffHours} godziny temu`
      }
    }

    return t('gameHistory.hoursAgo', { time: diffHours })
  }

  const diffDays = Math.floor(diffHours / 24)

  if (diffDays < 7) {
    if (locale.value === 'pl') {
      if (diffDays === 1) {
        return 'Wczoraj'
      }
    }

    return t('gameHistory.daysAgo', { time: diffDays })
  }

  if (diffDays < 30) {
    const diffWeeks = Math.floor(diffDays / 7)

    if (locale.value === 'pl') {
      if (diffWeeks === 1) {
        return 'Tydzień temu'
      }
      else if (diffWeeks >= 2 && diffWeeks <= 4) {
        return `${diffWeeks} tygodnie temu`
      }
    }

    return t('gameHistory.weeksAgo', { time: diffWeeks })
  }

  const diffMonths = Math.floor(diffDays / 30)

  if (diffMonths < 12) {
    if (locale.value === 'pl') {
      if (diffMonths === 1) {
        return 'Miesiąc temu'
      }
      else if (diffMonths >= 2 && diffMonths <= 4) {
        return `${diffMonths} miesiące temu`
      }
    }

    return t('gameHistory.monthsAgo', { time: diffMonths })
  }

  return t('gameHistory.yearAgo')
}

async function sendToProfile(participant: IParticipantStats, event: MouseEvent) {
  const region = mapApiRegion2ToSelect(game.value.info.platformId as TApiRegions2)
  let summonerName = participant.riotIdGameName || participant.summonerName
  let tagLine = participant.riotIdTagline

  if (!tagLine || !summonerName) {
    const account = await accountStore.getAccount({ puuid: participant.puuid })

    if (!account)
      return

    summonerName = account.gameName
    tagLine = account.tagLine
  }

  const url = `/account/${region}/${summonerName}-${tagLine}`

  if (event.button === mouseButton.MIDDLE)
    window.open(url, '_blank', 'noopener,noreferrer')

  else if (event.button === mouseButton.LEFT)
    router.push(url)
}

function chipText() {
  switch (multikill.value) {
    case 5:
      return 'Penta Kill'
    case 4:
      return 'Quadra Kill'
    case 3:
      return 'Triple Kill'
    case 2:
      return 'Double Kill'
    default:
      return ''
  }
}

function chipColor() {
  switch (multikill.value) {
    case 5:
      return 'yellow-accent-4'
    case 4:
      return 'red-lighten-1'
    case 3:
      return 'green-lighten-1'
    case 2:
      return 'gray'
    default:
      return 'gray'
  }
}

function findSecondaryRuneTree() {
  if (!runeInfo.value.length)
    return

  const subStylePerks = gamer.value.perks.styles.find(e => e.description === 'subStyle')?.style || 0

  const secondaryRuneTree = runeInfo.value.find(rune => rune.id === subStylePerks) || null
  const secondaryRuneTreeImagePath = secondaryRuneTree?.icon || null
  secondaryRuneTreeId.value = secondaryRuneTree?.id || 0

  if (secondaryRuneTreeImagePath)
    storageStore.getRuneIcons({ [subStylePerks]: secondaryRuneTreeImagePath })
}
</script>

<!-- eslint-disable vue/no-bare-strings-in-template -->
<template>
  <v-card
    :style="isWin
      ? 'background: linear-gradient(to right, rgba(35, 167, 250, 0.75), rgba(35, 167, 250, 0.25));'
      : 'background: linear-gradient(to right, rgba(252, 38, 38, 0.75), rgba(252, 38, 38, 0.25))'"
    class="pa-1"
  >
    <v-row
      no-gutters
      align="center"
      class="mx-3"
    >
      <v-col
        cols="6"
        sm="2"
        order="1"
      >
        <p>
          {{ $t(`queueTypes.${queueIdToType[game.info.queueId]}`) }}
        </p>

        <p class="font-weight-bold">
          {{ isWin
            ? $t('gameHistory.win')
            : $t('gameHistory.loss') }}
        </p>

        <v-spacer class="my-4" />

        <p>
          {{ whenWasGame() }}
        </p>

        <p>
          {{ mapGameTime() }}
        </p>
      </v-col>

      <v-col
        class="mb-5 mt-1"
        cols="12"
        sm="3"
        :order="xs
          ? 3
          : 2"
      >
        <v-row
          align="center"
          no-gutters
        >
          <v-col
            cols="auto"
          >
            <v-badge
              :content="gamer.champLevel"
              location="bottom end"
              offset-x="5"
              offset-y="5"
            >
              <v-avatar
                size="60"
              >
                <v-img
                  :src="championIcons[gamer.championId]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </v-badge>
          </v-col>

          <v-col
            cols="auto"
            class="ml-3 mr-5"
          >
            <p>
              <v-avatar
                size="25"
                rounded="0"
              >
                <v-img
                  :src="summonerSpellIcons[gamer.summoner1Id]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </p>

            <p>
              <v-avatar
                size="25"
                rounded="0"
              >
                <v-img
                  :src="summonerSpellIcons[gamer.summoner2Id]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </p>
          </v-col>

          <v-col cols="auto">
            <v-avatar
              size="60"
              style="cursor: pointer"
            >
              <v-img
                :src="runeIcons[keyRuneId]"
                lazy-src="~/assets/default.png"
              />

              <v-img
                v-if="secondaryRuneTreeId"
                :width="20"
                :height="20"
                style="position: absolute; bottom: 10px; right: 5px;"
                :src="runeIcons[secondaryRuneTreeId]"
                lazy-src="~/assets/default.png"
              />

              <v-menu
                activator="parent"
                :close-on-content-click="false"
                location="start"
              >
                <AccountRuneTable :extended-runes="gamer.perks" />
              </v-menu>
            </v-avatar>
          </v-col>
        </v-row>

        <v-row>
          <v-avatar
            v-for="item in items"
            :key="item"
            size="30"
            class="mx-1"
            rounded="0"
          >
            <v-img
              :src="itemIcons[item]"
            />
          </v-avatar>
        </v-row>
      </v-col>

      <v-col
        cols="6"
        sm="2"
        :order="xs
          ? 2
          : 3"
      >
        <p class="text-h6">
          <span class="font-weight-bold">
            {{ gamer.kills }}
          </span>

          /

          <span class="font-weight-bold text-red-darken-1">
            {{ gamer.deaths }}
          </span>

          /

          <span class="font-weight-bold">
            {{ gamer.assists }}
          </span>
        </p>

        <v-spacer class="my-2" />

        <p>
          KDA:
          <span
            v-if="gamer.deaths === 0 && gamer.kills + gamer.assists !== 0"
            class="font-weight-bold text-subtitle-1 text-yellow-accent-4"
          >
            {{ $t('gameHistory.perfect') }}
          </span>

          <span
            v-else-if="gamer.deaths === 0"
            class="font-weight-bold text-subtitle-1 text-gray"
          >
            0
          </span>

          <span
            v-else
            :class="`font-weight-bold text-${mapKDAToColor(kda)} text-subtitle-1`"
          >
            {{ kda.toFixed(2) }}
          </span>
        </p>

        <p>
          CS:
          <span class="text-subtitle-1 font-weight-medium">
            {{ `${minions} (${(minions / (game.info.gameDuration / 60)).toFixed(1)})` }}
          </span>
        </p>

        <p class="my-1">
          <v-chip
            v-if="multikill > 1"
            :color="chipColor()"
            density="compact"
            variant="tonal"
          >
            {{ chipText() }}
          </v-chip>
        </p>
      </v-col>

      <v-col
        cols="0"
        sm="1"
        order="4"
      />

      <v-col
        cols="12"
        sm="4"
        order="5"
      >
        <v-row>
          <v-col
            v-for="(team, teamIndex) in [
              team1,
              team2,
            ]"
            :key="teamIndex"
            cols="6"
          >
            <table>
              <tbody>
                <tr
                  v-for="(participant, index) in team"
                  :key="index"
                  style="cursor: pointer"
                  @mousedown.prevent="(event: MouseEvent) => sendToProfile(participant, event)"
                >
                  <td>
                    <v-avatar
                      size="20"
                      rounded="0"
                      class="mr-1"
                    >
                      <v-img
                        :src="championIcons[participant.championId]"
                        lazy-src="~/assets/default.png"
                      />
                    </v-avatar>
                  </td>

                  <td
                    :class="participant.puuid === gamer.puuid
                      ? 'font-weight-bold'
                      : ''"
                    style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;"
                  >
                    {{ participant.riotIdGameName || participant.summonerName }}
                  </td>
                </tr>
              </tbody>
            </table>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-card>
</template>
