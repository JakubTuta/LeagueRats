<script setup lang="ts">
import { ArcElement, Chart as ChartJS } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

const props = defineProps<{
  wins: number
  losses: number
}>()

ChartJS.register(ArcElement)

const { wins, losses } = toRefs(props)

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
    style="width: 100px; height: 100px;"
    :options="chartOptions"
    :data="chartData"
  />
</template>
