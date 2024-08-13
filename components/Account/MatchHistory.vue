<script setup lang="ts">
import type { IMatchData } from '~/models/matchData';

const props = defineProps<{
  matchIds: string[]
  loading: boolean
}>()

const { matchIds, loading } = toRefs(props)

const restStore = useRestStore()

const matchData = ref<IMatchData | null>(null)

watch(matchIds, async (newValue) => {
  if (newValue.length)
    matchData.value = await restStore.getMatchData(newValue[0])
}, { deep: true, immediate: true })
</script>

<template>
  Coming soon...

  <br>

  {{ matchData }}
</template>
