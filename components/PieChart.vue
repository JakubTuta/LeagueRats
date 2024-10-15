<script setup lang="ts">
import { ArcElement, Chart as ChartJS } from 'chart.js';
import { Doughnut } from 'vue-chartjs';

const props = defineProps<{
  wins: number
  losses: number
  size: number
}>()

ChartJS.register(ArcElement)

const { wins, losses, size } = toRefs(props)

const { t } = useI18n()

// league-blue
// league-red
const chartData = computed(() => ({
  labels: [t('profile.rank.wins'), t('profile.rank.losses')],
  datasets: [
    {
      data: [wins.value, losses.value],
      backgroundColor: ['rgb(35, 167, 250)', 'rgb(252, 38, 38)'],
    },
  ],
}))

const chartOptions = ref({
  responsive: true,
})
</script>

<template>
  <Doughnut
    :style="`width: ${size}px; height: ${size}px;`"
    :options="chartOptions"
    :data="chartData"
  />
</template>
