<script setup lang="ts">
import type { ChartOptions } from 'chart.js';
import { Pie } from 'vue-chartjs';
import { useDisplay } from 'vuetify';

const props = defineProps<{
  labels: string[]
  data: number[]
  backgroundColors: string[]
}>()

const { labels, data, backgroundColors } = toRefs(props)

const { mobile } = useDisplay()

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      data: data.value,
      backgroundColor: backgroundColors.value,
    },
  ],
}))

// @ts-expect-error correct
const chartOptions: ChartOptions = computed(() => ({
  responsive: true,
  plugins: {
    legend: {
      display: true,
      position: 'right',
      onClick: () => { },
      onHover: () => { },
      onLeave: () => { },
      labels: {
        color: 'white',
        padding: 20,
        usePointStyle: true,
        font: {
          size: mobile.value
            ? 10
            : 15,
        },
      },
    },
    title: {
      display: true,
      padding: 20,
      font: {
        size: mobile.value
          ? 20
          : 30,
      },
      text: 'Win rate',
    },
  },
  layout: {
    padding: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
    },
  },
}))
</script>

<template>
  <Pie
    :data="chartData"
    :options="chartOptions"
  />
</template>
