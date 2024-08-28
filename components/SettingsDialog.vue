<script setup lang="ts">
const props = defineProps<{
  isShow: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { isShow } = toRefs(props)

const themeStore = useThemeStore()
const languageStore = useLanguageStore()

const currentLang = localStorage.getItem('current-lang')
const currentTheme = localStorage.getItem('current-theme')

const theme = ref(currentTheme || 'dark')
const language = ref(currentLang || 'en')

function onClose() {
  emit('close')
}

watch(theme, (newTheme) => {
  themeStore.setTheme(newTheme)
})

watch(language, (newLang) => {
  languageStore.setLanguage(newLang)
})
</script>

<template>
  <v-dialog
    :model-value="isShow"
    max-width="800px"
    @update:model-value="onClose"
  >
    <v-card>
      <v-card-title>
        {{ $t('settings.title') }}
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12">
            {{ $t('settings.language') }}
          </v-col>

          <v-col cols="12">
            <v-btn-toggle
              v-model="language"
              color="primary"
              divided
              mandatory
            >
              <v-btn
                value="pl"
                min-width="150px"
              >
                <v-avatar
                  size="25"
                  class="mx-1"
                >
                  <v-img src="~/assets/flags/pl.png" />
                </v-avatar>

                {{ $t('universal.polish') }}
              </v-btn>

              <v-btn
                value="en"
                min-width="150px"
              >
                <v-avatar
                  size="25"
                  class="mx-1"
                >
                  <v-img src="~/assets/flags/uk.png" />
                </v-avatar>

                {{ $t('universal.english') }}
              </v-btn>
            </v-btn-toggle>
          </v-col>
        </v-row>

        <v-divider class="my-6" />

        <v-row>
          <v-col cols="12">
            {{ $t('settings.theme') }}
          </v-col>

          <v-col cols="12">
            <v-btn-toggle
              v-model="theme"
              color="primary"
              divided
              mandatory
            >
              <v-btn
                value="light"
                min-width="100px"
              >
                {{ $t('universal.light') }}
              </v-btn>

              <v-btn
                value="dark"
                min-width="100px"
              >
                {{ $t('universal.dark') }}
              </v-btn>
            </v-btn-toggle>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions class="justify-end">
        <v-btn
          color="error"
          @click="onClose"
        >
          {{ $t('universal.form.close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
