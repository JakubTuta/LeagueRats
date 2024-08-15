<script setup lang="ts">
import { queueIdToType } from '~/helpers/queueTypes';
import type { IAccount } from '~/models/account';
import type { IMatchData } from '~/models/matchData';

const props = defineProps<{
  account: IAccount | null
  game: IMatchData
}>()

const { account, game } = toRefs(props)

const { t, locale } = useI18n()

const storageStore = useStorageStore()
const { championIcons, summonerSpellIcons, runeIcons } = storeToRefs(storageStore)

const runeStore = useRuneStore()
const { runeInfo } = storeToRefs(runeStore)

const gamer = computed(() => game.value.info.participants.find(participant => participant.puuid === account.value!.puuid)!)
const isWin = computed(() => gamer.value.win)
const keyRuneId = computed(() => (gamer.value.perks.perkIds?.length
  ? gamer.value.perks.perkIds[0]
  : -1))

watch(game, async (newGame) => {
  if (!newGame)
    return

  // console.log(gamer.value.perks)

  storageStore.getChampionIcon(gamer.value.championId)

  storageStore.getSummonerSpellIcon(gamer.value.summoner1Id)
  storageStore.getSummonerSpellIcon(gamer.value.summoner2Id)

  if (!runeInfo.value)
    await runeStore.getRuneInfo()

  if (!runeInfo.value)
    return

  const keyRunePath = runeInfo.value?.[locale.value]?.flatMap(rune => rune.slots.flatMap(slot => slot.runes)).find(rune => rune.id === keyRuneId.value)?.icon || null

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
</script>

<template>
  <v-card
    :color="isWin
      ? 'league-blue'
      : 'league-red'"
  >
    <v-card-text>
      <v-row>
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
          <v-row>
            <v-col
              cols="auto"
            >
              <v-avatar
                size="60"
              >
                <v-img
                  :src="championIcons[gamer.championId]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </v-col>

            <v-col
              cols="auto"
            >
              <p>
                <v-avatar
                  size="30"
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
                  size="30"
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
                size="30"
              >
                <v-img
                  :src="runeIcons[keyRuneId]"
                  lazy-src="~/assets/default.png"
                />
              </v-avatar>
            </v-col>
          </v-row>

          <v-row>
            items
          </v-row>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
