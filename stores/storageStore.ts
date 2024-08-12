import { getDownloadURL, ref as storageRef } from 'firebase/storage'
import { championIds } from '~/helpers/championIds'
import { summonerSpellsIds } from '~/helpers/summonerSpellsIds'
import { useFirebase } from '~/helpers/useFirebase'

export const useStorageStore = defineStore('storage', () => {
  const { storage } = useFirebase()

  const championIcons = ref<Record<number, string>>({})
  const summonerSpellIcons = ref<Record<number, string>>({})
  const rankIcons = ref<Record<string, string>>({})
  const regionIcons = ref<Record<string, string>>({})
  const runeIcons = ref<Record<number, string>>({})

  const getChampionIcon = async (championId: number) => {
    if (championIcons.value[championId]) {
      return
    }

    const championName = championIds[championId]

    const championsRef = storageRef(storage, `champions/icons/${championName}.png`)

    const url = await getDownloadURL(championsRef)

    championIcons.value[championId] = url
  }

  const getSummonerSpellIcon = async (summonerSpellId: number) => {
    if (summonerSpellIcons.value[summonerSpellId]) {
      return
    }

    const summonerSpellName = summonerSpellsIds[summonerSpellId]

    const summonerSpellRef = storageRef(storage, `summonerSpells/icons/${summonerSpellName}.png`)

    const url = await getDownloadURL(summonerSpellRef)

    summonerSpellIcons.value[summonerSpellId] = url
  }

  const getRankIcon = async (rank: string) => {
    if (rankIcons.value[rank]) {
      return
    }

    const rankRef = storageRef(storage, `ranks/icons/${rank}.png`)

    const url = await getDownloadURL(rankRef)

    rankIcons.value[rank] = url
  }

  const getRegionIcon = async (region: string) => {
    if (regionIcons.value[region]) {
      return
    }

    const regionRef = storageRef(storage, `regions/icons/${region.toLowerCase()}.png`)

    const url = await getDownloadURL(regionRef)

    regionIcons.value[region] = url
  }

  const getRuneIcons = async (runePathPerId: Record<number, string>) => {
    for (const id in runePathPerId) {
      if (runeIcons.value[id]) {
        continue
      }

      const runePath = runePathPerId[id]
      const runeRef = storageRef(storage, runePath)

      // eslint-disable-next-line no-await-in-loop
      const url = await getDownloadURL(runeRef)

      runeIcons.value[id] = url
    }
  }

  return {
    championIcons,
    summonerSpellIcons,
    rankIcons,
    regionIcons,
    runeIcons,
    getChampionIcon,
    getSummonerSpellIcon,
    getRankIcon,
    getRegionIcon,
    getRuneIcons,
  }
})
