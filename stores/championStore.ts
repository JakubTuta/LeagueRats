import { collection, doc, getDoc, getDocs } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import { type IMatchData, mapMatchData } from '~/models/matchData'
import { type IProPlayer, mapIProPlayer } from '~/models/proPlayer'

export const useChampionStore = defineStore('championStore', () => {
  const champions = ref<Record<number, { title: string, value: string }>>({})
  const championStats = ref<Record<number, { games: number, wins: number, losses: number }>>({})
  const championMatches = ref<Record<number, { player: IProPlayer, match: IMatchData }[]>>({})

  const { firestore } = useFirebase()

  const getChampions = async () => {
    try {
      const document = doc(firestore, 'help', 'champions')
      const snapshot = await getDoc(document)

      if (!snapshot.exists()) {
        return
      }

      champions.value = snapshot.data() || null
    }
    catch (error) {
      console.error(error)
    }
  }

  const getChampionStats = async (championId: number) => {
    try {
      const championStatsDoc = await getDoc(doc(firestore, 'champion_history', championId.toString()))
      const championStatsData = championStatsDoc.data()

      if (!championStatsData) {
        return
      }

      championStats.value[championId] = championStatsData as { games: number, wins: number, losses: number }
    }
    catch (error) {
      console.error(error)
    }
  }

  const getChampionMatches = async (championId: number) => {
    try {
      const collectionRef = collection(firestore, `champion_history/${championId}/matches`)
      const snapshot = await getDocs(collectionRef)

      const docData = snapshot.docs.map(doc => ({ player: mapIProPlayer(doc.data().player), match: mapMatchData(doc.data().match) }))
      championMatches.value[championId] = docData
    }
    catch (error) {
      console.error(error)
    }
  }

  return {
    champions,
    championStats,
    championMatches,
    getChampions,
    getChampionStats,
    getChampionMatches,
  }
})
