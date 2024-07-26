import { ArcElement, Chart, Legend, Tooltip } from 'chart.js'

export default defineNuxtPlugin(() => {
  Chart.register(ArcElement, Tooltip, Legend)
})
