<script setup lang="ts">
import { mouseButton } from '~/helpers/mouse';

const router = useRouter()

function goHome(event: MouseEvent) {
  if (event.button === mouseButton.MIDDLE)
    window.open('/', '_blank', 'noopener,noreferrer')
  else if (event.button === mouseButton.LEFT)
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
          src="~/assets/default.png"
          max-height="40"
          max-width="40"
          class="ml-4"
          rounded="circle"
          style="cursor: pointer"
          v-bind="props"
          @mousedown.prevent="goHome"
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
            @mousedown.prevent="goHome"
          >
            {{ $t('universal.title') }}
          </span>
        </template>
      </v-tooltip>
    </v-app-bar-title>
  </v-app-bar>
</template>
