import { getDownloadURL, ref as storageRef } from 'firebase/storage'
import { teamPerRegion } from '~/helpers/regions'
import { useFirebase } from '~/helpers/useFirebase'
import type { IProPlayer } from '~/models/proPlayer'

export const useStorageStore = defineStore('storage', () => {
  const { storage } = useFirebase()

  const regionIcons = ref<Record<string, string>>({})
  const runeIcons = ref<Record<number, string>>({})
  const itemIcons = ref<Record<number, string>>({})
  const championIcons = ref<Record<number, string>>({})
  const rankIcons = ref<Record<string, string>>({})
  const teamLogos = ref<Record<string, string>>({})
  const teamImages = ref<Record<string, string>>({})

  const fetchChampionIcon = async (championId: number, championName?: string) => {
    if (championIcons.value[championId]) {
      return championIcons.value[championId]
    }

    if (!championName) {
      const championStore = useChampionStore()
      championName = championStore.getChampionName(championId) || undefined
    }

    if (!championName) {
      return null
    }

    try {
      const championsRef = storageRef(storage, `champions/icons/${championName}.png`)
      const url = await getDownloadURL(championsRef)
      championIcons.value[championId] = url

      return url
    }
    catch (error) { }

    return null
  }

  const fetchAllChampionIcons = async (championIds: number[]) => {
    const promises = championIds.map(async championId => await fetchChampionIcon(Number(championId)))
    await Promise.all(promises)
  }

  const fetchRankIcon = async (rank: string) => {
    const rankName = rank.toLowerCase()

    if (rankIcons.value[rankName]) {
      return
    }

    try {
      const rankRef = storageRef(storage, `ranks/icons/${rankName}.png`)
      const url = await getDownloadURL(rankRef)
      rankIcons.value[rankName] = url
    }
    catch (error) { }
  }

  const fetchAllRankIcons = async () => {
    const ranks = [
      'IRON',
      'BRONZE',
      'SILVER',
      'GOLD',
      'PLATINUM',
      'EMERALD',
      'DIAMOND',
      'MASTER',
      'GRANDMASTER',
      'CHALLENGER',
    ]

    const promises = ranks.map(async rank => await fetchRankIcon(rank))
    await Promise.all(promises)
  }

  const getRegionIcon = async (region: string) => {
    if (regionIcons.value[region]) {
      return regionIcons.value[region]
    }

    try {
      const regionRef = storageRef(storage, `regions/icons/${region.toLowerCase()}.png`)
      const url = await getDownloadURL(regionRef)
      regionIcons.value[region] = url

      return url
    }
    catch (error) { }

    return null
  }

  const getRuneIcons = async (runePathPerId: Record<number, string>) => {
    const promises = Object.entries(runePathPerId).map(async ([id, runePath]) => {
      const numId = Number(id)

      if (runeIcons.value[numId]) {
        return
      }

      try {
        const runeRef = storageRef(storage, runePath)
        const url = await getDownloadURL(runeRef)
        runeIcons.value[numId] = url
      }
      catch (error) {}
    })

    await Promise.all(promises)
  }

  const getItemIcons = async (itemIds: number[]) => {
    const promises = itemIds.map(async (id) => {
      if (id === 0 || itemIcons.value[id]) {
        return
      }

      try {
        const itemRef = storageRef(storage, `items/${id}.png`)
        const url = await getDownloadURL(itemRef)
        itemIcons.value[id] = url
      }
      catch (error) {}
    })

    await Promise.all(promises)
  }

  const fetchPlayerImage = async (player: string) => {
    const playerName = player?.toLowerCase().replace(' ', '_') || ''

    if (teamImages.value[playerName]) {
      return
    }

    try {
      const playerRef = storageRef(storage, `players/${playerName}.png`)
      const url = await getDownloadURL(playerRef)
      teamImages.value[playerName] = url
    }
    catch (error) { }
  }

  const fetchAllPlayerImages = async (players: IProPlayer[]) => {
    await Promise.all(players.map(async (player) => {
      await fetchPlayerImage(player.player)
    }))
  }

  const fetchTeamLogo = async (team: string) => {
    const teamName = team?.toUpperCase() || ''

    if (teamLogos.value[teamName]) {
      return
    }

    try {
      const teamRef = storageRef(storage, `teams/${teamName}.png`)
      const url = await getDownloadURL(teamRef)
      teamLogos.value[teamName] = url
    }
    catch (error) { }
  }

  const fetchAllTeamLogos = async () => {
    const allTeams = Object.values(teamPerRegion).flat()
    await Promise.all(allTeams.map(team => fetchTeamLogo(team)))
  }

  const getPlayerImage = (player: string) => {
    const playerName = player?.toLowerCase().replace(' ', '_') || ''

    if (teamImages.value[playerName]) {
      return teamImages.value[playerName]
    }

    return null
  }

  const getTeamLogo = (team: string) => {
    const teamName = team?.toUpperCase() || ''

    if (teamLogos.value[teamName]) {
      return teamLogos.value[teamName]
    }

    return null
  }

  const getRankIcon = (rank: string) => {
    const rankName = rank.toLowerCase()

    if (rankIcons.value[rankName]) {
      return rankIcons.value[rankName]
    }

    return null
  }

  const getChampionIcon = (championId: number | string) => {
    championId = Number(championId)

    if (championIcons.value[championId]) {
      return championIcons.value[championId]
    }

    return null
  }

  return {
    regionIcons,
    runeIcons,
    itemIcons,
    getRegionIcon,
    getRuneIcons,
    getItemIcons,
    fetchAllPlayerImages,
    fetchAllTeamLogos,
    fetchAllRankIcons,
    fetchAllChampionIcons,
    getPlayerImage,
    getTeamLogo,
    getRankIcon,
    getChampionIcon,
  }
})
