<script setup lang="ts">
import { champions, searchChampion } from '~/const/champions';
import { lengthRule } from '~/helpers/rules';

const { t } = useI18n()

const router = useRouter()

const search = ref<string | null>(null)
const username = ref<string | null>(null)
const tag = ref<string | null>(null)
const usernameError = ref('')
const tagError = ref('')

const errorMessage = t('rules.requiredField')

function showError() {
  if (!username.value) {
    usernameError.value = errorMessage
  }

  else if (!tag.value) {
    tagError.value = errorMessage
  }
}

function clearError() {
  usernameError.value = ''
  tagError.value = ''
}

function clearValues() {
  search.value = ''
  username.value = ''
  tag.value = ''
  usernameError.value = ''
  tagError.value = ''
}

function sendToUserView() {
  if (!username.value || !tag.value || tag.value.length > 3) {
    showError()

    return
  }

  const userDetails = `${username.value}-${tag.value}`

  router.push(`/user/${userDetails}`)
}

watch(username, (newUsername, oldUsername) => {
  if (newUsername && !oldUsername)
    clearError()
})

watch(tag, (newTag, oldTag) => {
  if (newTag && !oldTag)
    clearError()
})

onUnmounted(() => {
  clearValues()
})
</script>

<template>
  <v-container>
    <v-autocomplete
      v-model="search"
      prepend-inner-icon="mdi-magnify"
      clearable
      :label="$t('index.champion')"
      :items="champions"
      :custom-filter="searchChampion"
    />

    <v-row align-content="center">
      <v-col
        cols="12"
        md="8"
      >
        <v-text-field
          v-model="username"
          :label="$t('index.username')"
          prepend-inner-icon="mdi-account-outline"
          variant="outlined"
          :error-messages="usernameError"
          @keydown.enter="sendToUserView"
        />
      </v-col>

      <v-col
        cols="6"
        md="4"
      >
        <v-text-field
          v-model="tag"
          :label="$t('index.tag')"
          prepend-inner-icon="mdi-pound"
          append-icon="mdi-arrow-right"
          :rules="[lengthRule($t, 3)]"
          :error-messages="tagError"
          @click:append="sendToUserView"
          @keydown.enter="sendToUserView"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
