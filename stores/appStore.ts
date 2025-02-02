export const useAppStore = defineStore('app', () => {
  const loading = ref(false)

  const storageStore = useStorageStore()
  const summonersSpellStore = useSummonerSpellsStore()
  const runeStore = useRuneStore()
  const proPlayerStore = useProPlayerStore()
  const championStore = useChampionStore()

  const getInitialData = async () => {
    loading.value = true

    const players = await proPlayerStore.getAllProPlayers()
    await storageStore.fetchAllPlayerImages(players)
    await storageStore.fetchAllTeamLogos()
    await proPlayerStore.getProAccountNames()

    const champions = await championStore.getChampions()
    await storageStore.fetchAllChampionIcons(champions)

    await storageStore.fetchAllRankIcons()
    await runeStore.getRuneInfo()
    summonersSpellStore.getAllSummonerSpellIcons()
    proPlayerStore.getLiveStreams()
    proPlayerStore.getNotLiveStreams()

    loading.value = false
  }

  return {
    loading,
    getInitialData,
  }
})
