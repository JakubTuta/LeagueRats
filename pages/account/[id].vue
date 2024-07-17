<script setup lang="ts">
import type { IAccount } from '~/models/accountModel';
import { useAccountStore } from '~/stores/accountStore';

const route = useRoute()

const accountStore = useAccountStore()

const userDetails = String(route.params.id)
const gameName = userDetails.split('-')[0]
const tagLine = userDetails.split('-')[1]

const account = ref<IAccount | null>(null)

onMounted(async () => {
  account.value = await accountStore.getAccountDetails(gameName, tagLine)
})
</script>

<template>
  Soon...
</template>
