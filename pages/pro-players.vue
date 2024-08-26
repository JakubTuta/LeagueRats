<script setup lang="ts">
import imgLec from '~/assets/regions/lec.png'
import imgLcs from '~/assets/regions/lcs.png'
import imgLck from '~/assets/regions/lck.png'
import imgLpl from '~/assets/regions/lpl.png'

const selectedRegion = ref('lec')

const regions = [
  {
    title: 'LEC',
    value: 'lec',
    image: imgLec,
  },
  {
    title: 'LCS',
    value: 'lcs',
    image: imgLcs,
  },
  {
    title: 'LCK',
    value: 'lck',
    image: imgLck,
  },
  {
    title: 'LPL',
    value: 'lpl',
    image: imgLpl,
  },
]
</script>

<template>
  <v-container>
    <v-card>
      <v-card-title class="my-2">
        <v-row>
          <v-col
            v-for="region in regions"
            :key="region.value"
            align="center"
            cols="12"
            sm="6"
            md="3"
          >
            <v-card
              elevation="0"
              style="cursor: pointer;"
              :color="region.value === selectedRegion
                ? 'rgba(168, 118, 118, 0.25)'
                : ''"
              @click.stop="() => selectedRegion = region.value"
            >
              <v-img
                :src="region.image"
                max-width="100"
                max-height="100"
                aspect-ratio="1"
                cover
                class="mb-5"
              />

              {{ region.title }}
            </v-card>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text>
        soon...
      </v-card-text>
    </v-card>
  </v-container>
</template>
