import { collection, getDocs, query } from 'firebase/firestore'
import { teamPerRegion } from '~/helpers/regions'
import { useFirebase } from '~/helpers/useFirebase'
import { type IProAccount, mapIProAccount } from '~/models/pro_account'

export const useProPlayerStore = defineStore('proplayer', () => {
  const playersPerRegion: Record<string, IProAccount[]> = {}
  const playersPerTeam: Record<string, IProAccount[]> = {}
  const players = ref<IProAccount[]>([])

  const { firestore } = useFirebase()

  const resetPlayers = (region: string) => {
    players.value = playersPerRegion[region] || []
  }

  const getProPlayersForRegion = async (region: string): Promise<void> => {
    region = region.toUpperCase()

    if (playersPerRegion[region]) {
      players.value = playersPerRegion[region]

      return
    }

    const tmpPlayers = [] as IProAccount[]

    try {
      const promises = teamPerRegion[region].map(async (team) => {
        const q = query(collection(firestore, `pro_players/${region}/${team}`))
        const querySnapshot = await getDocs(q)

        querySnapshot.forEach((doc) => {
          tmpPlayers.push(doc.data() as IProAccount)
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
      return
    }

    try {
      const q = query(collection(firestore, `pro_players/${region}/${team}`))
      const querySnapshot = await getDocs(q)

      const playerData = querySnapshot.docs.map(docData => mapIProAccount(docData.data()))
      playersPerTeam[team] = playerData

      if (playersPerRegion[region]) {
        playersPerRegion[region].push(...playerData)
      }
      else {
        playersPerRegion[region] = playerData
      }

      players.value.push(...playerData)
    }
    catch (error) {
      console.error(error)
    }

    return []
  }

  return {
    players,
    resetPlayers,
    getProPlayersForRegion,
    getProPlayersFromTeam,
  }
})
