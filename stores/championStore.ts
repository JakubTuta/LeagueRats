import type { DocumentData, Query, QueryDocumentSnapshot } from 'firebase/firestore'
import { collection, doc, getDoc, getDocs, limit, orderBy, query, startAfter } from 'firebase/firestore'

import { useFirebase } from '~/helpers/useFirebase'
import type { IMatchData } from '~/models/matchData'
import { mapMatchData } from '~/models/matchData'
import type { IProPlayer } from '~/models/proPlayer'
import { mapIProPlayer } from '~/models/proPlayer'

export const useChampionStore = defineStore('championStore', () => {
  const champions = ref<Record<number, { title: string, value: string }>>({})
  const championStats = ref<Record<number, { games: number, wins: number, losses: number }>>({})
  const championMatches = ref<Record<number, { player: IProPlayer, match: IMatchData }[]>>({})

  const lastLoadedMatchForChampion: Record<number, QueryDocumentSnapshot<DocumentData, DocumentData>> = {}

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

  const getChampionMatches = async (championId: number, amount: number) => {
    try {
      const collectionRef = collection(firestore, `champion_history/${championId}/matches`)

      let q: Query | null = null
      if (lastLoadedMatchForChampion[championId]) {
        q = query(collectionRef, orderBy('match.info.gameStartTimestamp', 'desc'), limit(amount), startAfter(lastLoadedMatchForChampion[championId]))
      }
      else {
        q = query(collectionRef, orderBy('match.info.gameStartTimestamp', 'desc'), limit(amount))
      }

      const snapshot = await getDocs(q)

      if (snapshot.empty) {
        return
      }

      lastLoadedMatchForChampion[championId] = snapshot.docs[snapshot.docs.length - 1]

      const docData = snapshot.docs.map(doc => ({ player: mapIProPlayer(doc.data().player), match: mapMatchData(doc.data().match) }))

      if (!championMatches.value[championId]) {
        championMatches.value[championId] = docData
      }
      else {
        championMatches.value[championId].push(...docData)
      }
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
