<script setup lang="ts">
const route = useRoute()

const userDetails = String(route.params.id)
const username = userDetails.split('-')[0]
const tag = userDetails.split('-')[1]
</script>

<template>
  {{ userDetails }}
</template>
