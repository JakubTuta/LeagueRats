/* eslint-disable unused-imports/no-unused-vars */
import { getDownloadURL, ref as storageRef } from 'firebase/storage'
import { teamPerRegion } from '~/helpers/regions'
import { useFirebase } from '~/helpers/useFirebase'
import type { IProPlayer } from '~/models/proPlayer'

export const useStorageStore = defineStore('storage', () => {
  const { storage } = useFirebase()

  const championStore = useChampionStore()

  const regionIcons = ref<Record<string, string>>({})
  const runeIcons = ref<Record<number, string>>({})
  const itemIcons = ref<Record<number, string>>({})

  const championIcons: Record<number, string> = {}
  const rankIcons: Record<string, string> = {}
  const teamLogos: Record<string, string> = {}
  const teamImages: Record<string, string> = {}

  const fetchChampionIcon = async (championId: number) => {
    if (championIcons[championId]) {
      return championIcons[championId]
    }

    const championName = championStore.getChampionName(championId)

    if (!championName) {
      return null
    }

    try {
      const championsRef = storageRef(storage, `champions/icons/${championName}.png`)
      const url = await getDownloadURL(championsRef)
      championIcons[championId] = url

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

    if (rankIcons[rankName]) {
      return
    }

    try {
      const rankRef = storageRef(storage, `ranks/icons/${rankName}.png`)
      const url = await getDownloadURL(rankRef)
      rankIcons[rankName] = url
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
    for (const id in runePathPerId) {
      if (runeIcons.value[id]) {
        continue
      }

      const runePath = runePathPerId[id]

      try {
        const runeRef = storageRef(storage, runePath)
        // eslint-disable-next-line no-await-in-loop
        const url = await getDownloadURL(runeRef)
        runeIcons.value[id] = url
      }
      catch (error) {}
    }
  }

  const getItemIcons = async (itemIds: number[]) => {
    for (const id of itemIds) {
      if (id === 0 || itemIcons.value[id]) {
        continue
      }

      try {
        const itemRef = storageRef(storage, `items/${id}.png`)

        // eslint-disable-next-line no-await-in-loop
        const url = await getDownloadURL(itemRef)

        itemIcons.value[id] = url
      }
      catch (error) {}
    }
  }

  const fetchPlayerImage = async (player: string) => {
    const playerName = player?.toLowerCase().replace(' ', '_') || ''

    if (teamImages[playerName]) {
      return
    }

    try {
      const playerRef = storageRef(storage, `players/${playerName}.png`)
      const url = await getDownloadURL(playerRef)
      teamImages[playerName] = url
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

    if (teamLogos[teamName]) {
      return
    }

    try {
      const teamRef = storageRef(storage, `teams/${teamName}.png`)

      const url = await getDownloadURL(teamRef)

      teamLogos[teamName] = url
    }
    catch (error) { }
  }

  const fetchAllTeamLogos = async () => {
    await Promise.all(Object.values(teamPerRegion).map(async (teams) => {
      await Promise.all(teams.map(async (team) => {
        await fetchTeamLogo(team)
      }))
    }))
  }

  const getPlayerImage = (player: string) => {
    const playerName = player?.toLowerCase().replace(' ', '_') || ''

    if (teamImages[playerName]) {
      return teamImages[playerName]
    }

    return null
  }

  const getTeamLogo = (team: string) => {
    const teamName = team?.toUpperCase() || ''

    if (teamLogos[teamName]) {
      return teamLogos[teamName]
    }

    return null
  }

  const getRankIcon = (rank: string) => {
    const rankName = rank.toLowerCase()

    if (rankIcons[rankName]) {
      return rankIcons[rankName]
    }

    return null
  }

  const getChampionIcon = (championId: number | string) => {
    championId = Number(championId)

    if (championIcons[championId]) {
      return championIcons[championId]
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
