import { ArcElement, Chart, Legend, Title, Tooltip } from 'chart.js'

export default defineNuxtPlugin(() => {
  Chart.register(ArcElement, Tooltip, Legend, Title)
})
