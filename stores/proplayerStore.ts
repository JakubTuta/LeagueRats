import type { DocumentData, QuerySnapshot, Unsubscribe } from 'firebase/firestore'
import { collection, doc, onSnapshot, query } from 'firebase/firestore'
import { teamPerRegion } from '~/helpers/regions'
import { useFirebase } from '~/helpers/useFirebase'
import type { IActiveGame } from '~/models/activeGame'
import type { IBootcampAccount } from '~/models/bootcampAccount'
import type { IProActiveGame } from '~/models/proActiveGame'
import { mapProActiveGame } from '~/models/proActiveGame'
import type { IProPlayer } from '~/models/proPlayer'
import { mapIProPlayer } from '~/models/proPlayer'

interface IProAccountNames {
  [puuid: string]: {
    player: string
    team: string
    region: string
  }
}

export interface IStream {
  player: string
  team: string
  region: string
  twitch: string
  isLive: boolean
}

export const useProPlayerStore = defineStore('proPlayer', () => {
  const savedPlayers = ref<Record<string, Record<string, IProPlayer[]>>>({})
  const players = ref<IProPlayer[]>([])
  const activeGames = ref<IProActiveGame[]>([])
  const proAccountNames = ref<IProAccountNames | null>(null)
  const bootcampAccounts = ref<IBootcampAccount[]>([])

  const liveStreams = ref<Record<string, IStream>>({})
  const notLiveStreams = ref<Record<string, IStream>>({})

  const activeGamesUnsubscribe = ref<Unsubscribe | null>(null)
  const liveStreamsUnsubscribe = ref<Unsubscribe | null>(null)
  const notLiveStreamsUnsubscribe = ref<Unsubscribe | null>(null)

  const { firestore } = useFirebase()
  const apiStore = useApiStore()

  const resetState = () => {
    savedPlayers.value = {}
    players.value = []
    activeGames.value = []
    proAccountNames.value = null
    bootcampAccounts.value = []

    liveStreams.value = {}
    notLiveStreams.value = {}

    if (liveStreamsUnsubscribe.value) {
      liveStreamsUnsubscribe.value()
      liveStreamsUnsubscribe.value = null
    }

    if (notLiveStreamsUnsubscribe.value) {
      notLiveStreamsUnsubscribe.value()
      notLiveStreamsUnsubscribe.value = null
    }

    if (activeGamesUnsubscribe.value) {
      activeGamesUnsubscribe.value()
      activeGamesUnsubscribe.value = null
    }
  }

  const resetPlayers = () => {
    players.value = []
  }

  const getAllProPlayers = async (): Promise<IProPlayer[]> => {
    const url = '/v2/pro-players/players'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const data = response!.data as Record<string, Record<string, IProPlayer[]>>
      savedPlayers.value = data
      players.value = Object.values(data).flatMap(region => Object.values(region).flat())

      return Object.values(data).flatMap(region => Object.values(region).flat())
    }

    return []
  }

  const findRegionForTeam = (team: string): string | null => {
    for (const [region, teams] of Object.entries(teamPerRegion)) {
      if (teams.includes(team))
        return region
    }

    return null
  }

  const getProPlayersFromTeam = (team: string): IProPlayer[] => {
    const region = findRegionForTeam(team)

    if (!region) {
      return []
    }

    if (savedPlayers.value[region] && savedPlayers.value[region][team]) {
      const data = savedPlayers.value[region][team]
      players.value.push(...data)

      return data
    }

    return []
  }

  const getPlayer = async (region: string, team: string, name: string): Promise<IProPlayer | null> => {
    const upperRegion = region.toUpperCase()
    const upperTeam = team.toUpperCase()
    const upperName = name.toUpperCase()

    const url = `/v2/pro-players/players`

    const queryParams = new URLSearchParams()

    queryParams.append('region', upperRegion)
    queryParams.append('team', upperTeam)
    queryParams.append('player', upperName)

    const fullUrl = `${url}?${queryParams.toString()}`

    const response = await apiStore.sendRequest({ url: fullUrl, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const playerData = response!.data[upperRegion][upperTeam][0]

      return mapIProPlayer(playerData)
    }

    return null
  }

  const getActiveProGamesFromDatabase = () => {
    if (activeGamesUnsubscribe.value) {
      activeGamesUnsubscribe.value()
    }

    const q = query(collection(firestore, 'active_pro_games'))

    const onSuccess = (snapshot: QuerySnapshot) => {
      const games = snapshot.docs.map(docData => mapProActiveGame(docData.data() as { player: IProPlayer, game: IActiveGame }))
        .filter(game => game !== null)

      activeGames.value = games
    }

    activeGamesUnsubscribe.value = onSnapshot(q, onSuccess)
  }

  const getProAccountNames = async (): Promise<IProAccountNames> => {
    const url = '/v2/pro-players/account-names'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      proAccountNames.value = response!.data as IProAccountNames
    }

    return {}
  }

  const getLiveStreams = () => {
    if (liveStreamsUnsubscribe.value) {
      liveStreamsUnsubscribe.value()
    }

    const onSuccess = (snapshot: DocumentData) => {
      const data = snapshot.data()
      for (const key in data) {
        data[key].isLive = true
      }
      liveStreams.value = data as Record<string, IStream>
    }

    liveStreamsUnsubscribe.value = onSnapshot(
      doc(collection(firestore, 'live_streams'), 'live'),
      onSuccess,
    )
  }

  const getNotLiveStreams = () => {
    if (notLiveStreamsUnsubscribe.value) {
      notLiveStreamsUnsubscribe.value()
    }

    const onSuccess = (snapshot: DocumentData) => {
      const data = snapshot.data()
      for (const key in data) {
        data[key].isLive = false
      }
      notLiveStreams.value = data as Record<string, IStream>
    }

    const onError = (error: Error) => {
      console.error(error)
    }

    notLiveStreamsUnsubscribe.value = onSnapshot(
      doc(collection(firestore, 'live_streams'), 'not_live'),
      onSuccess,
      onError,
    )
  }

  const createProPlayer = async (player: IProPlayer, account: { username: string, tag: string, region: string }): Promise<boolean> => {
    const baseUrl = '/v2/pro-players/players'

    const queryParams = new URLSearchParams()

    queryParams.append('username', account.username)
    queryParams.append('tag', account.tag)
    queryParams.append('region', account.region)

    const url = `${baseUrl}?${queryParams.toString()}`

    const response = await apiStore.sendRequest({ url, method: 'POST', data: player })

    if (apiStore.isResponseOk(response)) {
      return true
    }

    return false
  }

  const getPlayerHistoryStats = async (team: string, player: string, amount: number = 20) => {
    const url = `/v2/pro-players/history-stats/${team}/${player}?amount=${amount}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return response!.data
    }

    return null
  }

  const transferProPlayer = async (player: string, fromTeam: string, toTeam: string) => {
    const url = `/v2/pro-players/transfer/${player}/from/${fromTeam}/to/${toTeam}`

    const response = await apiStore.sendRequest({ url, method: 'PUT' })

    if (apiStore.isResponseOk(response)) {
      return true
    }

    return false
  }

  return {
    savedPlayers,
    players,
    activeGames,
    proAccountNames,
    bootcampAccounts,
    liveStreams,
    notLiveStreams,
    resetState,
    resetPlayers,
    getAllProPlayers,
    getProPlayersFromTeam,
    getPlayer,
    getActiveProGamesFromDatabase,
    getProAccountNames,
    getLiveStreams,
    getNotLiveStreams,
    createProPlayer,
    getPlayerHistoryStats,
    transferProPlayer,
  }
})
