<script setup lang="ts">
const route = useRoute()

onMounted(() => {
  try {
    const paramsData = route.params
    const [username, tag] = String(paramsData['search-account']).split('-')
  }
  catch (e) {
    console.error(e)
  }
})
</script>

<template>
  xdd
</template>
