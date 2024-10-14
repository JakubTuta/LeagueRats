<script setup lang="ts">
import type { IMatchData } from '~/models/matchData';
import type { IProPlayer } from '~/models/proPlayer';

const props = defineProps<{
  player: IProPlayer
  match: IMatchData
}>()

const { player, match } = toRefs(props)

const { t, locale } = useI18n()

const gamer = computed(() => match.value.info.participants.find(participant => player.value.puuid.includes(participant.puuid))!)
const isWin = computed(() => gamer.value.win)

function whenWasGame() {
  const now = new Date()
  const gameDate = new Date(match.value.info.gameStartTimestamp.toDate())

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

function mapGameTime() {
  const minutes = String(Math.floor(match.value.info.gameDuration / 60)).padStart(2, '0')
  const seconds = String(match.value.info.gameDuration % 60).padStart(2, '0')

  return `${minutes}:${seconds}`
}
</script>

<template>
  <v-card
    :class="isWin
      ? 'fading-background-win'
      : 'fading-background-lose'"
    class="pa-1"
  >
    <v-row
      no-gutters
      align="center"
      class="mx-3"
    >
      <v-col
        cols="5"
        sm="2"
      >
        <p class="font-weight-bold">
          {{ isWin
            ? $t('gameHistory.win')
            : $t('gameHistory.loss') }}
        </p>

        <v-spacer class="my-2" />

        <p>
          {{ whenWasGame() }}
        </p>

        <p>
          {{ mapGameTime() }}
        </p>
      </v-col>

      <v-col
        cols="5"
        sm="2"
      >
        {{ `${player.team} ${player.player}` }}
      </v-col>

      <v-col
        cols="2"
        sm="1"
      >
        lane
      </v-col>

      <v-col
        cols="0"
        sm="1"
      />

      <v-col
        cols="6"
        sm="3"
      >
        items
      </v-col>

      <v-col
        cols="6"
        sm="3"
      >
        vs
      </v-col>
    </v-row>
  </v-card>
</template>
