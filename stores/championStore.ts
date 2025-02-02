import { mapChampionMastery } from '~/models/championMastery'
import type { IMatchData } from '~/models/matchData'
import { mapMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'
import { mapIProPlayer } from '~/models/proPlayer'

export const useChampionStore = defineStore('championStore', () => {
  const champions = ref<Record<string, { title: string, value: string }>>({})
  const championStats = ref<Record<string, { games: number, wins: number, losses: number }>>({})
  const championMatches = ref<Record<string, { player: IProPlayer, match: IMatchData }[]>>({})

  const lastLoadedMatchForChampion: Record<number, string> = {}

  const apiStore = useApiStore()

  const getChampions = async () => {
    const url = '/v2/champions/'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      champions.value = response!.data

      return Object.keys(champions.value).map(Number)
    }

    return []
  }

  const getChampionMastery = async (puuid: string) => {
    const url = `/v2/champions/mastery/${puuid}`

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

  const getChampionMatches = async (championId: number, amount: number) => {
    let url = `/v2/champions/${championId}/matches?amount=${amount}`

    if (lastLoadedMatchForChampion[championId]) {
      url += `&startAfter=${lastLoadedMatchForChampion[championId]}`
    }

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (!apiStore.isResponseOk(response)) {
      return
    }

    const docData = response!.data.map((doc: any) => ({ player: mapIProPlayer(doc.player), match: mapMatchData(doc.match) })) as { player: IProPlayer, match: IMatchData }[]

    if (!championMatches.value[championId]) {
      championMatches.value[championId] = docData
    }
    else {
      championMatches.value[championId].push(...docData)
    }

    if (docData.length) {
      lastLoadedMatchForChampion[championId] = docData[docData.length - 1].match.metadata.matchId
    }
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

  return {
    champions,
    championStats,
    championMatches,
    getChampions,
    getChampionMastery,
    getChampionStats,
    getChampionMatches,
    getChampionsPositions,
    getChampionName,
  }
})
