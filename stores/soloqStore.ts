import type { DocumentData, QueryDocumentSnapshot } from 'firebase/firestore'
import { collection, getDocs, limit, orderBy, query, startAfter } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { ILeaderboard } from '~/models/leaderboard'

export const useSoloqStore = defineStore('soloq', () => {
  const leaderboardPerRegion = ref<Record<string, ILeaderboard[]>>({})

  const lastLoadedPlayerPerRegion: Record<string, QueryDocumentSnapshot<DocumentData, DocumentData>> = {}

  const { firestore } = useFirebase()

  const getFirstLeaderboardForRegion = async (region: string, league: string, limitPlayers: number) => {
    if (lastLoadedPlayerPerRegion[region]) {
      return
    }

    const collectionRef = collection(firestore, 'leaderboard', region, league)
    const q = query(collectionRef, orderBy('rank'), limit(limitPlayers))

    const querySnapshot = await getDocs(q)
    const leaderboard = querySnapshot.docs.map(doc => doc.data() as ILeaderboard)

    leaderboardPerRegion.value[region] = leaderboard
    lastLoadedPlayerPerRegion[region] = querySnapshot.docs[querySnapshot.docs.length - 1]
  }

  const getOtherLeaderboardForRegion = async (region: string, league: string) => {
    const collectionRef = collection(firestore, 'leaderboard', region, league)
    const q = query(collectionRef, orderBy('rank'), startAfter(lastLoadedPlayerPerRegion[region]))

    const querySnapshot = await getDocs(q)
    const leaderboard = querySnapshot.docs.map(doc => doc.data() as ILeaderboard)

    leaderboardPerRegion.value[region].push(...leaderboard)
    lastLoadedPlayerPerRegion[region] = querySnapshot.docs[querySnapshot.docs.length - 1]
  }

  return {
    leaderboardPerRegion,
    getFirstLeaderboardForRegion,
    getOtherLeaderboardForRegion,
  }
})
