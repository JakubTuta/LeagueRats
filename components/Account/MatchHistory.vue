<script setup lang="ts">
const props = defineProps<{
  matchIds: string[]
}>()

const { matchIds } = toRefs(props)
</script>

<template>
  {{ matchIds }}
</template>
