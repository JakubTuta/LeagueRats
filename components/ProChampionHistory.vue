<script setup lang="ts">
import { useDisplay } from 'vuetify'
import type { IMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'
// @ts-expect-error correct path
import topIcon from '~/assets/roles/top.png'
// @ts-expect-error correct path
import jngIcon from '~/assets/roles/jng.png'
// @ts-expect-error correct path
import midIcon from '~/assets/roles/mid.png'
// @ts-expect-error correct path
import adcIcon from '~/assets/roles/adc.png'
// @ts-expect-error correct path
import supIcon from '~/assets/roles/sup.png'

const props = defineProps<{
  player: IProPlayer
  match: IMatchData
}>()

const { player, match } = toRefs(props)

const { t, locale } = useI18n()
const { smAndDown } = useDisplay()

const storageStore = useStorageStore()
const { championIcons, teamImages, summonerSpellIcons, runeIcons, itemIcons } = storeToRefs(storageStore)

const runeStore = useRuneStore()
const { runeInfo } = storeToRefs(runeStore)

const championStore = useChampionStore()
const { champions } = storeToRefs(championStore)

const secondaryRuneTreeId = ref(0)

const gamer = computed(() => match.value.info.participants.find(participant => player.value.puuid.includes(participant.puuid))!)
const isWin = computed(() => gamer.value.win)
const keyRuneId = computed(() => (gamer.value.perks.styles.find(style => style.description === 'primaryStyle')!.selections[0].perk))
const items = computed(() => [gamer.value.item0, gamer.value.item1, gamer.value.item2, gamer.value.item3, gamer.value.item4, gamer.value.item5].filter(item => item !== 0))
const enemy = computed(() => match.value.info.participants.find(participant => participant.teamPosition === gamer.value.teamPosition && participant.puuid !== gamer.value.puuid)!)

onMounted(() => {
  if (player.value) {
    storageStore.getTeamImages(player.value.region, player.value.team)
  }
})

const mappedChampions = computed(() => {
  return Object.entries(champions.value).map(([id, value]) => ({
    id: Number.parseInt(id),
    title: value.title,
    value: value.value,
  }))
})

watch(gamer, async (newGamer) => {
  if (!newGamer)
    return

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

  findSecondaryRuneTree()
}, { immediate: true })

watch(enemy, (newEnemy) => {
  if (!newEnemy)
    return

  storageStore.getChampionIcon(enemy.value.championId)
}, { immediate: true })

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

function getPlayerRoleIcon() {
  switch (gamer.value.teamPosition) {
    case 'TOP':
      return topIcon
    case 'JUNGLE':
      return jngIcon
    case 'MIDDLE':
      return midIcon
    case 'BOTTOM':
      return adcIcon
    case 'UTILITY':
      return supIcon
    default:
      return ''
  }
}

function findSecondaryRuneTree() {
  if (!runeInfo.value)
    return

  const subStylePerks = gamer.value.perks.styles.find(e => e.description === 'subStyle')?.style || 0

  const secondaryRuneTree = runeInfo.value[locale.value]?.find(rune => rune.id === subStylePerks) || null
  const secondaryRuneTreeImagePath = secondaryRuneTree?.icon || null
  secondaryRuneTreeId.value = secondaryRuneTree?.id || 0

  if (secondaryRuneTreeImagePath)
    storageStore.getRuneIcons({ [subStylePerks]: secondaryRuneTreeImagePath })
}

function findChampionFromId(championId: number) {
  return mappedChampions.value.find(champion => champion.id === championId)?.value || ''
}
</script>

<!-- eslint-disable vue/no-bare-strings-in-template -->
<template>
  <v-card
    :class="isWin
      ? 'fading-background-win'
      : 'fading-background-lose'"
    class="pa-1"
    min-height="120px"
  >
    <v-row
      no-gutters
      align="center"
      class="mx-3"
    >
      <v-col
        cols="3"
        sm="1"
      >
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
        cols="3"
        sm="2"
      >
        <v-col
          cols="12"
          align="center"
        >
          <NuxtLink
            :to="`/player/${player.team}/${player.player}`"
            style="cursor: pointer; text-decoration: none; color: inherit;"
          >
            <v-avatar
              size="70"
              class="mx-auto"
            >
              <v-img
                :src="teamImages[player.team]?.[player.player.toLowerCase()]"
                lazy-src="~/assets/default.png"
              />
            </v-avatar>

            <p>
              {{ `${player.team} ${player.player}` }}
            </p>
          </NuxtLink>
        </v-col>
      </v-col>

      <v-col
        cols="2"
        sm="1"
        align="center"
      >
        <v-avatar
          size="30"
          rounded="0"
          :image="getPlayerRoleIcon()"
        />

        <p class="mt-2">
          {{ $t(`positions.${gamer.teamPosition}`) }}
        </p>
      </v-col>

      <v-col
        cols="2"
        sm="1"
        align="center"
      >
        <v-avatar
          size="30"
          rounded="0"
          :image="summonerSpellIcons[gamer.summoner1Id]"
          class="mr-2"
        />

        <v-avatar
          size="30"
          rounded="0"
          :image="summonerSpellIcons[gamer.summoner2Id]"
        />
      </v-col>

      <v-col
        cols="2"
        sm="1"
        align="center"
      >
        <div style="cursor: pointer;">
          <v-menu
            activator="parent"
            :close-on-content-click="false"
            location="start"
          >
            <AccountRuneTable :extended-runes="gamer.perks" />
          </v-menu>

          <v-avatar
            size="60"
          >
            <v-img
              :src="runeIcons[keyRuneId]"
              lazy-src="~/assets/default.png"
            />
          </v-avatar>

          <v-avatar
            v-if="secondaryRuneTreeId"
            size="25"
            :class="smAndDown
              ? ''
              : 'mt-3'"
          >
            <v-img
              :src="runeIcons[secondaryRuneTreeId]"
              lazy-src="~/assets/default.png"
            />
          </v-avatar>
        </div>
      </v-col>

      <v-col
        cols="0"
        sm="1"
      />

      <v-col
        cols="6"
        sm="2"
        class="d-flex justify-center"
      >
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
      </v-col>

      <v-col
        cols="6"
        sm="2"
        align="end"
      >
        <v-avatar size="50">
          <v-img
            :src="championIcons[gamer.championId]"
            lazy-src="~/assets/default.png"
          />
        </v-avatar>

        <span class="mx-2">
          vs
        </span>

        <NuxtLink
          :to="findChampionFromId(enemy.championId)
            ? `/champion/${findChampionFromId(enemy.championId)}`
            : ''"
        >
          <v-avatar size="50">
            <v-img
              :src="championIcons[enemy.championId]"
              lazy-src="~/assets/default.png"
            />
          </v-avatar>
        </NuxtLink>
      </v-col>
    </v-row>
  </v-card>
</template>
