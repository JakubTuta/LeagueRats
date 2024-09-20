<script setup lang="ts">
const isShow = ref(false)
const isAcceptedCookies = useCookie('is-accepted-cookies', {
  default: () => false,
  maxAge: 60 * 60 * 24 * 30,
})

onMounted(() => {
  if (!isAcceptedCookies.value) {
    isShow.value = true
  }
})

function acceptCookies() {
  isAcceptedCookies.value = true
  isShow.value = false
}

function denyCookies() {
  isAcceptedCookies.value = false
  isShow.value = false
}
</script>

<template>
  <v-snackbar
    v-model="isShow"
    absolute
    color="primary"
    :timeout="-1"
  >
    <v-row style="display: flex; align-items: center; justify-content: center">
      <v-col cols="3">
        <v-img src="~/assets/cookies.png" />
      </v-col>

      <v-col cols="9">
        <p class="text-h5 mb-2 ml-1">
          {{ $t('cookies.title') }}
        </p>

        <p class="text-subtitle-2">
          {{ $t('cookies.text') }}
        </p>

        <v-row
          justify="center"
          class="mt-1"
        >
          <v-col
            cols="12"
            sm="4"
            class="mx-1"
          >
            <v-btn
              variant="elevated"
              color="success"
              block
              @click="acceptCookies"
            >
              {{ $t('universal.form.accept') }}
            </v-btn>
          </v-col>

          <v-col
            cols="12"
            sm="4"
            class="mx-1"
          >
            <v-btn
              variant="elevated"
              color="error"
              width="100px"
              block
              @click="denyCookies"
            >
              {{ $t('universal.form.deny') }}
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-snackbar>
</template>
