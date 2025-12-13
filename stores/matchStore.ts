import { generateAccountKey } from '~/helpers/accountKey'
import type { IAccount } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'
import { mapActiveGame } from '~/models/activeGame'
import { mapMatchData } from '~/models/matchData'

interface ActiveGameState {
  data: IActiveGame | null
  loading: boolean
  error: string | null
  lastFetched: number | null
}

export const useMatchStore = defineStore('match', () => {
  const apiStore = useApiStore()

  const activeGames = ref<Record<string, ActiveGameState>>({})
  const fetchingActiveGames = ref<Set<string>>(new Set())

  const getActiveGameState = (accountKey: string): ActiveGameState => {
    if (!activeGames.value[accountKey]) {
      activeGames.value[accountKey] = {
        data: null,
        loading: false,
        error: null,
        lastFetched: null,
      }
    }

    return activeGames.value[accountKey]
  }

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

  const getActiveMatch = async (puuid: string, region: string) => {
    const url = `/v2/match/active/${puuid}?region=${region}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return mapActiveGame(response!.data)
    }

    return null
  }

  const fetchActiveMatch = async (account: IAccount): Promise<IActiveGame | null> => {
    const accountKey = generateAccountKey(account.region, account.gameName, account.tagLine)
    const state = getActiveGameState(accountKey)

    if (fetchingActiveGames.value.has(accountKey)) {
      return state.data
    }

    if (state.lastFetched && Date.now() - state.lastFetched < 30000) {
      return state.data
    }

    fetchingActiveGames.value.add(accountKey)
    state.loading = true
    state.error = null

    try {
      const game = await getActiveMatch(account.puuid, account.region)
      state.data = game
      state.lastFetched = Date.now()

      return game
    }
    catch (error: any) {
      state.error = error.message || 'Failed to fetch active match'

      return null
    }
    finally {
      state.loading = false
      fetchingActiveGames.value.delete(accountKey)
    }
  }

  const getActiveGameData = (region: string, gameName: string, tagLine: string): IActiveGame | null => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return activeGames.value[accountKey]?.data || null
  }

  const isActiveGameLoading = (region: string, gameName: string, tagLine: string): boolean => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return activeGames.value[accountKey]?.loading || false
  }

  const getActiveGameError = (region: string, gameName: string, tagLine: string): string | null => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return activeGames.value[accountKey]?.error || null
  }

  const getMatchHistoryBatch = async (puuid: string, region: string, optionalKeys: object) => {
    const baseUrl = `/v2/match/history/batch/${puuid}`

    const queryParams = new URLSearchParams()

    queryParams.append('region', region)

    Object.entries(optionalKeys).forEach(([key, value]) => {
      queryParams.append(key, value)
    })

    const url = `${baseUrl}?${queryParams.toString()}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data.map(mapMatchData)
    }

    return []
  }

  return {
    activeGames,
    getMatchHistory,
    getMatchData,
    getActiveMatch,
    fetchActiveMatch,
    getActiveGameData,
    isActiveGameLoading,
    getActiveGameError,
    getMatchHistoryBatch,
  }
})
