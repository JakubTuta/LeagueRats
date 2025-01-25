import type { DocumentData, QuerySnapshot, Unsubscribe } from 'firebase/firestore'
import { collection, doc, onSnapshot, query } from 'firebase/firestore'
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

  const getProPlayersForRegion = async (region: string): Promise<IProPlayer[]> => {
    if (savedPlayers.value[region]) {
      const data = Object.values(savedPlayers.value[region]).flat()
      players.value = data

      return data
    }

    const url = `/v2/pro-players/accounts/${region}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const data = response!.data as Record<string, IProPlayer[]>

      const mappedData = Object.fromEntries(
        Object.entries(data).map(([key, value]) => [key, value.map(mapIProPlayer)]),
      )

      savedPlayers.value[region] = mappedData
      players.value = Object.values(mappedData).flat()

      return Object.values(mappedData).flat()
    }

    return []
  }

  const getProPlayersFromTeam = async (region: string, team: string): Promise<IProPlayer[]> => {
    if (savedPlayers.value[region] && savedPlayers.value[region][team]) {
      const data = savedPlayers.value[region][team]
      players.value = Object.values(savedPlayers.value[region]).flat()

      return data
    }

    const url = `/v2/pro-players/accounts/${region}/${team}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const data = response!.data.map(mapIProPlayer)

      if (!savedPlayers.value[region]) {
        savedPlayers.value[region] = {}
      }

      savedPlayers.value[region][team] = data
      players.value = Object.values(savedPlayers.value[region]).flat()

      return data
    }

    return []
  }

  const getPlayer = async (region: string, team: string, name: string): Promise<IProPlayer | null> => {
    const url = `/v2/pro-players/accounts/${region}/${team}/${name}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      return mapIProPlayer(response!.data)
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

    const onError = (error: Error) => {
      console.error(error)
    }

    activeGamesUnsubscribe.value = onSnapshot(q, onSuccess, onError)
  }

  const getProAccountNames = async (): Promise<IProAccountNames> => {
    const url = '/v2/pro-players/account-names'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      proAccountNames.value = response!.data as IProAccountNames
    }

    return {}
  }

  const getBootcampAccounts = async (): Promise<IBootcampAccount[]> => {
    const url = '/v2/pro-players/bootcamp/leaderboard'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      bootcampAccounts.value = response!.data as IBootcampAccount[]
    }

    return []
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

    const onError = (error: Error) => {
      console.error(error)
    }

    liveStreamsUnsubscribe.value = onSnapshot(
      doc(collection(firestore, 'live_streams'), 'live'),
      onSuccess,
      onError,
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
    const baseUrl = '/v2/pro-players/accounts'

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

  return {
    players,
    activeGames,
    proAccountNames,
    bootcampAccounts,
    liveStreams,
    notLiveStreams,
    resetState,
    resetPlayers,
    getProPlayersForRegion,
    getProPlayersFromTeam,
    getPlayer,
    getActiveProGamesFromDatabase,
    getProAccountNames,
    getBootcampAccounts,
    getLiveStreams,
    getNotLiveStreams,
    createProPlayer,
  }
})
