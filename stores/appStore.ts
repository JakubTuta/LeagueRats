export const useAppStore = defineStore('app', () => {
  const storageStore = useStorageStore()
  const summonersSpellStore = useSummonerSpellsStore()
  const runeStore = useRuneStore()

  const getInitialData = () => {
    storageStore.asyncGetAllChampionIcons()
    storageStore.asyncGetAllRankIcons()
    storageStore.asyncGetAllPlayerImages()
    summonersSpellStore.getAllSummonerSpellIcons()
    runeStore.getRuneInfo()
  }

  return {
    getInitialData,
  }
})
