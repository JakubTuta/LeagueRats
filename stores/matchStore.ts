import { mapActiveGame } from '~/models/activeGame'
import { mapMatchData } from '~/models/matchData'

export const useMatchStore = defineStore('match', () => {
  const apiStore = useApiStore()

  const getMatchHistory = async (puuid: string, optionalKeys: object) => {
    const baseUrl = `/v2/match/history/${puuid}`

    const queryParams = new URLSearchParams()

    Object.entries(optionalKeys).forEach(([key, value]) => {
      queryParams.append(key, value)
    })

    const url = `${baseUrl}?${queryParams.toString()}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data as string[]
    }

    return []
  }

  const getMatchData = async (matchId: string) => {
    const url = `/v2/match/history/match-data/${matchId}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return mapMatchData(response!.data)
    }

    return null
  }

  const getActiveMatch = async (puuid: string) => {
    const url = `/v2/match/active/${puuid}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return mapActiveGame(response!.data)
    }

    return null
  }

  return {
    getMatchHistory,
    getMatchData,
    getActiveMatch,
  }
})
