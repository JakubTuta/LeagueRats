<script setup lang="ts">
import { useLanguageStore } from '~/helpers/language'
import { useThemeStore } from '~/helpers/theme'

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
            >
              <v-btn
                value="pl"
                min-width="150px"
              >
                <Icon
                  name="flag:pl-4x3"
                  class="mr-2"
                />

                {{ $t('universal.polish') }}
              </v-btn>

              <v-btn
                value="en"
                min-width="150px"
              >
                <Icon
                  name="flag:gb-4x3"
                  class="mr-2"
                />

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
