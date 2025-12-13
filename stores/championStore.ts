import { generateAccountKey } from '~/helpers/accountKey'
import type { IAccount } from '~/models/account'
import type { IChampionMastery } from '~/models/championMastery'
import { mapChampionMastery } from '~/models/championMastery'
import type { IMatchData } from '~/models/matchData'
import { mapMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'
import { mapIProPlayer } from '~/models/proPlayer'

interface ChampionMasteryState {
  data: IChampionMastery[]
  loading: boolean
  error: string | null
  lastFetched: number | null
}

export const useChampionStore = defineStore('championStore', () => {
  const champions = ref<Record<string, { title: string, value: string }>>({})
  const championStats = ref<Record<string, { games: number, wins: number, losses: number }>>({})
  const championMatches = ref<Record<string, { player: IProPlayer, match: IMatchData }[]>>({})
  const lastLoadedMatchForChampion = ref<Record<number, string>>({})

  const championMasteries = ref<Record<string, ChampionMasteryState>>({})
  const fetchingMasteries = ref<Set<string>>(new Set())

  const apiStore = useApiStore()

  const getChampionMasteryState = (accountKey: string): ChampionMasteryState => {
    if (!championMasteries.value[accountKey]) {
      championMasteries.value[accountKey] = {
        data: [],
        loading: false,
        error: null,
        lastFetched: null,
      }
    }

    return championMasteries.value[accountKey]
  }

  const clearChampionMatches = (championId: number) => {
    championMatches.value[championId] = []
    delete lastLoadedMatchForChampion.value[championId]
  }

  const getChampions = async () => {
    const url = '/v2/champions/list'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      champions.value = response!.data

      return Object.keys(champions.value).map(Number)
    }

    return []
  }

  const getChampionMastery = async (puuid: string, region: string) => {
    const url = `/v2/champions/mastery/${puuid}?region=${region}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data.map(mapChampionMastery)
    }

    return []
  }

  const getChampionStats = async (championId: number) => {
    const url = `/v2/champions/${championId}/stats`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      championStats.value[championId] = response!.data
    }
  }

  const getChampionMatches = async (championId: number, amount: number, lane: string | null = null, versus: string | null = null) => {
    let url = `/v2/champions/${championId}/matches?amount=${amount}`

    if (lastLoadedMatchForChampion.value[championId]) {
      url += `&startAfter=${lastLoadedMatchForChampion.value[championId]}`
    }

    if (lane) {
      url += `&lane=${lane}`
    }

    if (versus) {
      url += `&versus=${versus}`
    }

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (!apiStore.isResponseOk(response)) {
      return []
    }

    const docData = response!.data.map((doc: any) => ({ player: mapIProPlayer(doc.player), match: mapMatchData(doc.match) })) as { player: IProPlayer, match: IMatchData }[]

    if (!championMatches.value[championId]) {
      championMatches.value[championId] = docData
    }
    else {
      championMatches.value[championId].push(...docData)
    }

    if (docData.length) {
      lastLoadedMatchForChampion.value[championId] = docData[docData.length - 1].match.metadata.matchId
    }

    return docData
  }

  const getChampionsPositions = async (champions: number[]) => {
    const stringChampions = champions.join('.')
    const url = `/v2/champions/positions/${stringChampions}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data as Record<string, string>
    }

    return {}
  }

  const getChampionName = (championId: number) => {
    if (champions.value[championId]) {
      return champions.value[championId].value
    }

    return null
  }

  const fetchChampionMastery = async (account: IAccount): Promise<IChampionMastery[]> => {
    const accountKey = generateAccountKey(account.region, account.gameName, account.tagLine)
    const state = getChampionMasteryState(accountKey)

    if (fetchingMasteries.value.has(accountKey)) {
      return state.data
    }

    if (state.data.length && state.lastFetched && Date.now() - state.lastFetched < 300000) {
      return state.data
    }

    fetchingMasteries.value.add(accountKey)
    state.loading = true
    state.error = null

    try {
      const masteries = await getChampionMastery(account.puuid, account.region.toLowerCase())
      state.data = masteries
      state.lastFetched = Date.now()

      return masteries
    }
    catch (error: any) {
      state.error = error.message || 'Failed to fetch champion mastery'

      return []
    }
    finally {
      state.loading = false
      fetchingMasteries.value.delete(accountKey)
    }
  }

  const getChampionMasteryData = (region: string, gameName: string, tagLine: string): IChampionMastery[] => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return championMasteries.value[accountKey]?.data || []
  }

  const isChampionMasteryLoading = (region: string, gameName: string, tagLine: string): boolean => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return championMasteries.value[accountKey]?.loading || false
  }

  const getChampionMasteryError = (region: string, gameName: string, tagLine: string): string | null => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return championMasteries.value[accountKey]?.error || null
  }

  return {
    champions,
    championStats,
    championMatches,
    championMasteries,
    clearChampionMatches,
    getChampions,
    getChampionMastery,
    fetchChampionMastery,
    getChampionMasteryData,
    isChampionMasteryLoading,
    getChampionMasteryError,
    getChampionStats,
    getChampionMatches,
    getChampionsPositions,
    getChampionName,
  }
})
