<script setup lang="ts">
// @ts-expect-error działa
import icon from '../public/favicon.ico';

const router = useRouter()

const appIcon = ref(icon)

function goHome() {
  router.push('/')
}
</script>

<template>
  <v-app-bar>
    <v-tooltip
      :text="$t('navbar.home')"
      location="bottom"
    >
      <template #activator="{props}">
        <v-img
          :src="appIcon"
          max-height="40"
          max-width="40"
          class="ml-4"
          rounded="circle"
          style="cursor: pointer"
          v-bind="props"
          @click="goHome"
        />
      </template>
    </v-tooltip>

    <v-app-bar-title>
      <v-tooltip
        :text="$t('navbar.home')"
        location="bottom"
      >
        <template #activator="{props}">
          <span
            style="cursor: pointer"
            v-bind="props"
            @click="goHome"
          >
            {{ $t('universal.title') }}
          </span>
        </template>
      </v-tooltip>
    </v-app-bar-title>
  </v-app-bar>
</template>
