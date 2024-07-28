import { getDownloadURL, ref } from 'firebase/storage'
import { useFirebase } from '~/helpers/useFirebase'

export const useStorageStore = defineStore('storage', () => {
  const { storage } = useFirebase()

  const championIconUrls: Record<string, string> = {}
  const summonerSpellIconUrls: Record<string, string> = {}
  const rankIcons: Record<string, string> = {}

  const getChampionIcon = async (championName: string) => {
    if (championIconUrls[championName]) {
      return championIconUrls[championName]
    }

    const storageRef = ref(storage, `champions/icons/${championName}.png`)

    const url = await getDownloadURL(storageRef)

    championIconUrls[championName] = url

    return url
  }

  const getSummonerSpellIcon = async (summonerSpellName: string) => {
    if (summonerSpellIconUrls[summonerSpellName]) {
      return summonerSpellIconUrls[summonerSpellName]
    }

    const storageRef = ref(storage, `summonerSpells/icons/${summonerSpellName}.png`)

    const url = await getDownloadURL(storageRef)

    summonerSpellIconUrls[summonerSpellName] = url

    return url
  }

  const getRankIcon = async (rank: string) => {
    if (rankIcons[rank]) {
      return rankIcons[rank]
    }

    const storageRef = ref(storage, `ranks/icons/${rank}.png`)

    const url = await getDownloadURL(storageRef)

    rankIcons[rank] = url

    return url
  }

  return {
    getChampionIcon,
    getSummonerSpellIcon,
    getRankIcon,
  }
})
