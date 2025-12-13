import type { ILeaderboard } from '~/models/leaderboard'

export const useSoloqStore = defineStore('soloq', () => {
  const leaderboardPerRegion = ref<Record<string, ILeaderboard[]>>({})

  const apiStore = useApiStore()

  const getLeaderboardForRegion = async (region: string, limit: number, page: number) => {
    const url = `/v2/league/leaderboard/${region.toLowerCase()}?limit=${limit}&page=${page}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      if (leaderboardPerRegion.value[region]) {
        leaderboardPerRegion.value[region].push(...response!.data)
      }
      else {
        leaderboardPerRegion.value[region] = response!.data
      }
    }
  }

  return {
    leaderboardPerRegion,
    getLeaderboardForRegion,
  }
})
