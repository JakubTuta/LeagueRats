<script setup lang="ts">
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

const storageStore = useStorageStore()
const { championIcons, summonerSpellIcons, runeIcons, itemIcons } = storeToRefs(storageStore)

const runeStore = useRuneStore()
const { runeInfo } = storeToRefs(runeStore)

const team1 = ref<IParticipantStats[]>([])
const team2 = ref<IParticipantStats[]>([])

const gamer = computed(() => game.value.info.participants.find(participant => participant.puuid === account.value!.puuid)!)
const isWin = computed(() => gamer.value.win)
const keyRuneId = computed(() => (gamer.value.perks.styles.find(style => style.description === 'primaryStyle')!.selections[0].perk))
const items = computed(() => [gamer.value.item0, gamer.value.item1, gamer.value.item2, gamer.value.item3, gamer.value.item4, gamer.value.item5])
const minions = computed(() => gamer.value.neutralMinionsKilled + gamer.value.totalMinionsKilled)
const teamIds = computed(() => {
  if (!game.value)
    return []

  return Array.from(new Set(game.value.info.participants.map(participant => participant.teamId)))
})

const mapPositions: { [key: string]: number } = {
  TOP: 1,
  JUNGLE: 2,
  MIDDLE: 3,
  BOTTOM: 4,
  UTILITY: 5,
}

watch(game, async (newGame) => {
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

  storageStore.getSummonerSpellIcon(gamer.value.summoner1Id)
  storageStore.getSummonerSpellIcon(gamer.value.summoner2Id)

  storageStore.getItemIcons(items.value)

  if (!runeInfo.value)
    await runeStore.getRuneInfo()

  if (!runeInfo.value)
    return

  const keyRunePath = runeInfo.value[locale.value]?.flatMap(rune => rune.slots.flatMap(slot => slot.runes)).find(rune => rune.id === keyRuneId.value)?.icon || null

  if (keyRunePath)
    storageStore.getRuneIcons({ [keyRuneId.value]: keyRunePath })
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

function sendToProfile(participant: IParticipantStats, event: MouseEvent) {
  if (participant.puuid === gamer.value.puuid)
    return

  const region = mapApiRegion2ToSelect(game.value.info.platformId as TApiRegions2)
  const summonerName = participant.summonerName
  const tagLine = participant.riotIdTagline

  const url = `/account/${region.toLowerCase()}/${summonerName}-${tagLine}`

  if (event.button === mouseButton.MIDDLE)
    window.open(url, '_blank', 'noopener,noreferrer')

  else if (event.button === mouseButton.LEFT)
    router.push(url)
}
</script>

<template>
  <v-card
    :color="isWin
      ? 'rgba(35, 167, 250, 0.6)'
      : 'rgba(252, 38, 38, 0.6)'"
  >
    <v-row
      no-gutters
      align="center"
      class="mx-3"
    >
      <v-col
        cols="6"
        sm="2"
      >
        <p>
          {{ $t(`queueTypes.${queueIdToType[game.info.queueId]}`) }}
        </p>

        <p>
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
        cols="6"
        sm="4"
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
              style="cursor: pointer"
              size="50"
            >
              <v-img
                :src="runeIcons[keyRuneId]"
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
              lazy-src="~/assets/default.png"
            />
          </v-avatar>
        </v-row>
      </v-col>

      <v-col cols="2">
        <p class="text-h6">
          {{ `${gamer.kills} / ${gamer.deaths} / ${gamer.assists}` }}
        </p>

        <v-spacer class="my-2" />

        <p>
          {{ `KDA: ${((gamer.kills + gamer.assists) / gamer.deaths).toFixed(2)}` }}
        </p>

        <p>
          {{ `CS: ${minions} (${(minions / (game.info.gameDuration / 60)).toFixed(1)})` }}
        </p>
      </v-col>

      <v-col cols="4">
        <v-row no-gutters>
          <v-col
            v-for="(team, teamIndex) in [
              team1,
              team2,
            ]"
            :key="teamIndex"
            cols="6"
          >
            <v-list
              :bg-color="isWin
                ? 'rgba(0, 0, 0, 0)'
                : 'rgba(0, 0, 0, 0)'"
              density="compact"
              :lines="false"
            >
              <v-list-item
                v-for="(participant, index) in team"
                :key="index"
                style="cursor: pointer"
                @mousedown.prevent="(event: MouseEvent) => sendToProfile(participant, event)"
              >
                <v-avatar
                  size="25"
                  rounded="0"
                >
                  <v-img
                    :src="championIcons[participant.championId]"
                    lazy-src="~/assets/default.png"
                  />
                </v-avatar>

                {{ participant.riotIdGameName }}
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-card>
</template>
