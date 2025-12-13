import { generateAccountKey } from '~/helpers/accountKey'
import type { IAccount } from '~/models/account'
import type { ILeagueEntry } from '~/models/leagueEntry'
import { mapLeagueEntry } from '~/models/leagueEntry'

interface LeagueState {
  data: ILeagueEntry[]
  loading: boolean
  error: string | null
  lastFetched: number | null
}

export const useLeagueStore = defineStore('league', () => {
  const apiStore = useApiStore()

  const leagueEntries = ref<Record<string, LeagueState>>({})
  const fetchingLeagues = ref<Set<string>>(new Set())

  const getLeagueState = (accountKey: string): LeagueState => {
    if (!leagueEntries.value[accountKey]) {
      leagueEntries.value[accountKey] = {
        data: [],
        loading: false,
        error: null,
        lastFetched: null,
      }
    }

    return leagueEntries.value[accountKey]
  }

  const getLeagueEntry = async (puuid: string, region: string) => {
    const url = `/v2/league/${puuid}?region=${region}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data.map(mapLeagueEntry)
    }

    return []
  }

  const fetchLeagueEntry = async (account: IAccount): Promise<ILeagueEntry[]> => {
    const accountKey = generateAccountKey(account.region, account.gameName, account.tagLine)
    const state = getLeagueState(accountKey)

    if (fetchingLeagues.value.has(accountKey)) {
      return state.data
    }

    if (state.data.length && state.lastFetched && Date.now() - state.lastFetched < 300000) {
      return state.data
    }

    fetchingLeagues.value.add(accountKey)
    state.loading = true
    state.error = null

    try {
      const entries = await getLeagueEntry(account.puuid, account.region.toUpperCase())
      state.data = entries
      state.lastFetched = Date.now()

      return entries
    }
    catch (error: any) {
      state.error = error.message || 'Failed to fetch league entries'

      return []
    }
    finally {
      state.loading = false
      fetchingLeagues.value.delete(accountKey)
    }
  }

  const getLeagueData = (region: string, gameName: string, tagLine: string): ILeagueEntry[] => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return leagueEntries.value[accountKey]?.data || []
  }

  const isLeagueLoading = (region: string, gameName: string, tagLine: string): boolean => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return leagueEntries.value[accountKey]?.loading || false
  }

  const getLeagueError = (region: string, gameName: string, tagLine: string): string | null => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return leagueEntries.value[accountKey]?.error || null
  }

  return {
    leagueEntries,
    getLeagueEntry,
    fetchLeagueEntry,
    getLeagueData,
    isLeagueLoading,
    getLeagueError,
  }
})
