<script setup lang="ts">
import { useRestStore } from '~/stores/restStore';

const route = useRoute()

const restStore = useRestStore()

const userDetails = String(route.params.id)
const username = userDetails.split('-')[0]
const tag = userDetails.split('-')[1]

restStore.testConnection()
</script>

<template>
  {{ userDetails }}
</template>
