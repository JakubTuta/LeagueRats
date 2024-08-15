<script setup lang="ts">
import type { IPerks } from '~/models/activeGame';
import type { IRuneData, IRuneTree } from '~/models/runeInfo';

const props = defineProps<{
  runes: IPerks
}>()

const { runes } = toRefs(props)

const storageStore = useStorageStore()
const { runeIcons } = storeToRefs(storageStore)

const runeStore = useRuneStore()
const { runeInfo } = storeToRefs(runeStore)

const { locale } = useI18n()

const primaryRuneTree = ref<IRuneTree | null>(null)
const secondaryRuneTree = ref<IRuneTree | null>(null)
const keyRune = ref<IRuneData | null>(null)
const primaryRunes = ref<IRuneData[]>([])
const secondaryRunes = ref<IRuneData[]>([])

watch(runes, async (newRunes) => {
  if (!newRunes)
    return

  if (!runeInfo.value)
    await runeStore.getRuneInfo()

  if (!runeInfo.value)
    return

  primaryRuneTree.value = runeInfo.value[locale.value].find(rune => rune.id === newRunes.perkStyle) || null
  secondaryRuneTree.value = runeInfo.value[locale.value].find(rune => rune.id === newRunes.perkSubStyle) || null

  primaryRunes.value = primaryRuneTree.value?.slots.flatMap(slot => slot.runes).filter(rune => newRunes.perkIds.includes(rune.id)) || []
  secondaryRunes.value = secondaryRuneTree.value?.slots.flatMap(slot => slot.runes).filter(rune => newRunes.perkIds.includes(rune.id)) || []

  keyRune.value = primaryRunes.value[0]
  primaryRunes.value = primaryRunes.value.slice(1)

  runeStore.getRuneIcons(newRunes)
}, { immediate: true })
</script>

<template>
  <v-card class="pa-4">
    <v-row align="center">
      <v-col
        cols="12"
        text-align-center
      >
        <v-avatar
          size="70"
        >
          <v-img :src="runeIcons[keyRune?.id || -1]" />

          <v-tooltip
            activator="parent"
            location="bottom"
          >
            <AccountRuneTooltip :rune="keyRune" />
          </v-tooltip>
        </v-avatar>
      </v-col>
    </v-row>

    <v-row
      align="center"
      class="my-2"
    >
      <v-col
        v-for="rune in primaryRunes"
        :key="rune.id"
        text-align-center
        cols="4"
      >
        <v-avatar size="40">
          <v-img :src="runeIcons[rune.id]" />

          <v-tooltip
            activator="parent"
            location="bottom"
          >
            <AccountRuneTooltip :rune="rune" />
          </v-tooltip>
        </v-avatar>
      </v-col>
    </v-row>

    <v-row align="center">
      <v-col
        v-for="rune in secondaryRunes"
        :key="rune.id"
        text-align-center
        cols="6"
      >
        <v-avatar size="40">
          <v-img :src="runeIcons[rune.id]" />

          <v-tooltip
            activator="parent"
            location="bottom"
          >
            <AccountRuneTooltip :rune="rune" />
          </v-tooltip>
        </v-avatar>
      </v-col>
    </v-row>
  </v-card>
</template>

<style>
.v-overlay__content {
  --v-theme-surface-variant: 127, 127, 127;
}
</style>
