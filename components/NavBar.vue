<template>
  <v-app-bar>
    <v-img
      src="~/assets/default.png"
      max-height="40"
      max-width="40"
      class="ml-4"
      rounded="circle"
    />

    <v-app-bar-title>
      <v-tooltip
        :text="$t('navbar.home')"
        location="bottom"
      >
        <template #activator="{props}">
          <NuxtLink
            style="cursor: pointer; text-decoration: none; color: inherit;"
            v-bind="props"
            to="/"
          >
            {{ $t('universal.title') }}
          </NuxtLink>
        </template>
      </v-tooltip>
    </v-app-bar-title>
  </v-app-bar>
</template>
