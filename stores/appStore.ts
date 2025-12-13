export const useAppStore = defineStore('app', () => {
  const loading = ref(false)

  const storageStore = useStorageStore()
  const summonersSpellStore = useSummonerSpellsStore()
  const runeStore = useRuneStore()
  const proPlayerStore = useProPlayerStore()
  const championStore = useChampionStore()

  const getInitialData = async () => {
    loading.value = true

    try {
      const [players, champions] = await Promise.all([
        proPlayerStore.getAllProPlayers(),
        championStore.getChampions(),
      ])

      await Promise.all([
        storageStore.fetchAllPlayerImages(players),
        storageStore.fetchAllTeamLogos(),
        proPlayerStore.getProAccountNames(),
        storageStore.fetchAllChampionIcons(champions),
        storageStore.fetchAllRankIcons(),
        runeStore.getRuneInfo(),
      ])

      summonersSpellStore.getAllSummonerSpellIcons()
      proPlayerStore.getLiveStreams()
      proPlayerStore.getNotLiveStreams()
    }
    catch (error) {
      console.error('Error loading initial data:', error)
    }
    finally {
      loading.value = false
    }
  }

  return {
    loading,
    getInitialData,
  }
})
