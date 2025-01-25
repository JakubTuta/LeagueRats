import { mapLeagueEntry } from '~/models/leagueEntry'

export const useLeagueStore = defineStore('league', () => {
  const apiStore = useApiStore()

  const getLeagueEntry = async (puuid: string) => {
    const url = `/v2/league/${puuid}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data.map(mapLeagueEntry)
    }

    return []
  }

  return {
    getLeagueEntry,
  }
})
