import { collection, doc, getDoc, getDocs, query } from 'firebase/firestore'
import { proRegions, teamPerRegion } from '~/helpers/regions'
import { useFirebase } from '~/helpers/useFirebase'
import type { IProActiveGame } from '~/models/proActiveGame'
import { type IProPlayer, mapIProPlayer } from '~/models/proPlayer'

export const useProPlayerStore = defineStore('proPlayer', () => {
  const playersPerRegion: Record<string, IProPlayer[]> = {}
  const playersPerTeam: Record<string, IProPlayer[]> = {}
  const players = ref<IProPlayer[]>([])

  const activeGames = ref<IProActiveGame[]>([])
  const playerPerName: Record<string, IProPlayer> = {}

  const { firestore } = useFirebase()
  const restStore = useRestStore()

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

  const getActiveProGames = async () => {
    if (!activeGames.value.length) {
      activeGames.value = await restStore.getActiveProGames()

      return
    }

    const maxGameTimeInSeconds = 60 * 45

    const now = new Date().getTime() / 1000

    activeGames.value = activeGames.value.filter((game) => {
      return now - game.game.gameStartTime.seconds < maxGameTimeInSeconds
    })
  }

  return {
    players,
    activeGames,
    resetPlayers,
    getProPlayersForRegion,
    getProPlayersFromTeam,
    getActiveProGames,
    getPlayerFromName,
  }
})
