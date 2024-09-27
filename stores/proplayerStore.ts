import type { QuerySnapshot, Unsubscribe } from 'firebase/firestore'
import { collection, doc, getDoc, getDocs, onSnapshot, query } from 'firebase/firestore'
import { proRegions, teamPerRegion } from '~/helpers/regions'
import { useFirebase } from '~/helpers/useFirebase'
import type { IActiveGame } from '~/models/activeGame'
import type { IProActiveGame } from '~/models/proActiveGame'
import { mapProActiveGame } from '~/models/proActiveGame'
import { type IProPlayer, mapIProPlayer } from '~/models/proPlayer'

interface IProAccountNames {
  [puuid: string]: {
    player: string
    team: string
  }
}

export const useProPlayerStore = defineStore('proPlayer', () => {
  let playersPerRegion: Record<string, IProPlayer[]> = {}
  let playersPerTeam: Record<string, IProPlayer[]> = {}
  let playerPerName: Record<string, IProPlayer> = {}

  const players = ref<IProPlayer[]>([])
  const activeGames = ref<IProActiveGame[]>([])
  const activeGamesUnsubscribe = ref<Unsubscribe | null>(null)
  const proAccountNames = ref<IProAccountNames | null>(null)

  const { firestore } = useFirebase()

  const resetState = () => {
    playersPerRegion = {}
    playersPerTeam = {}
    playerPerName = {}
    players.value = []

    activeGames.value = []

    if (activeGamesUnsubscribe.value) {
      activeGamesUnsubscribe.value()
      activeGamesUnsubscribe.value = null
    }
  }

  const resetPlayers = () => {
    players.value = []
  }

  const getProPlayersForRegion = async (region: string): Promise<void> => {
    region = region.toUpperCase()

    if (playersPerRegion[region]) {
      players.value = playersPerRegion[region]

      return
    }

    const tmpPlayers = [] as IProPlayer[]

    try {
      const promises = teamPerRegion[region].map(async (team) => {
        const q = query(collection(firestore, `pro_players/${region}/${team}`))
        const querySnapshot = await getDocs(q)

        querySnapshot.forEach((doc) => {
          tmpPlayers.push(doc.data() as IProPlayer)
        })
      })

      await Promise.all(promises)
      players.value = tmpPlayers
      playersPerRegion[region] = tmpPlayers
    }
    catch (error) {
      console.error(error)
    }
  }

  const getProPlayersFromTeam = async (region: string, team: string) => {
    if (playersPerTeam[team]) {
      players.value.push(...playersPerTeam[team])

      return
    }

    try {
      const q = query(collection(firestore, `pro_players/${region}/${team}`))
      const querySnapshot = await getDocs(q)

      const playerData = querySnapshot.docs.map(docData => mapIProPlayer(docData.data()))
      playersPerTeam[team] = playerData

      players.value.push(...playerData)
    }
    catch (error) {
      console.error(error)
    }

    return []
  }

  const returnProPlayersFromTeam = async (region: string, team: string) => {
    if (playersPerTeam[team]) {
      return playersPerTeam[team]
    }

    try {
      const q = query(collection(firestore, `pro_players/${region}/${team}`))
      const querySnapshot = await getDocs(q)

      const playerData = querySnapshot.docs.map(docData => mapIProPlayer(docData.data()))
      playersPerTeam[team] = playerData

      return playerData
    }
    catch (error) {
      console.error(error)
    }

    return []
  }

  const returnPlayersFromTeam = async (region: string, team: string) => {
    if (playersPerTeam[team]) {
      return playersPerTeam[team]
    }

    try {
      const q = query(collection(firestore, `pro_players/${region}/${team}`))
      const querySnapshot = await getDocs(q)

      const playerData = querySnapshot.docs.map(docData => mapIProPlayer(docData.data()))
      playersPerTeam[team] = playerData

      return playerData
    }
    catch (error) {
      console.error(error)
    }

    return []
  }

  const getPlayerFromTeam = async (team: string, name: string) => {
    const playerName = name.toLowerCase()

    if (playersPerTeam[team]) {
      return playersPerTeam[team].find(player => player.player.toLowerCase() === playerName) || null
    }

    const region = proRegions.find(region => teamPerRegion[region].includes(team))

    if (!region)
      return null

    try {
      const q = query(collection(firestore, `pro_players/${region}/${team}`))
      const querySnapshot = await getDocs(q)

      const playerData = querySnapshot.docs.map(docData => mapIProPlayer(docData.data()))
      playersPerTeam[team] = playerData

      return playerData.find(player => player.player.toLowerCase() === playerName) || null
    }
    catch (error) {
      console.error(error)
    }

    return null
  }

  const getPlayerFromName = async (name: string): Promise<IProPlayer | null> => {
    if (playerPerName[name]) {
      return playerPerName[name]
    }

    for (const region of proRegions) {
      for (const team of teamPerRegion[region]) {
        const docRef = doc(firestore, `pro_players/${region}/${team}`, name)
        // eslint-disable-next-line no-await-in-loop
        const docSnap = await getDoc(docRef)

        if (docSnap.exists()) {
          const player = mapIProPlayer(docSnap.data())
          playerPerName[name] = player

          return player
        }
      }
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

  const getProAccountNames = async () => {
    try {
      const document = doc(firestore, 'pro_players', 'account_names')
      const docSnap = await getDoc(document)

      if (docSnap.exists()) {
        proAccountNames.value = docSnap.data() as IProAccountNames
      }
    }
    catch (error) {
      console.error(error)
    }
  }

  return {
    players,
    activeGames,
    proAccountNames,
    resetState,
    resetPlayers,
    getProPlayersForRegion,
    getProPlayersFromTeam,
    returnPlayersFromTeam,
    getPlayerFromTeam,
    returnProPlayersFromTeam,
    getPlayerFromName,
    getActiveProGamesFromDatabase,
    getProAccountNames,
  }
})
