import type { IPerks } from '~/models/activeGame'
import type { IRuneTree } from '~/models/runeInfo'

export const useRuneStore = defineStore('rune', () => {
  const storageStore = useStorageStore()
  const apiStore = useApiStore()

  const runeInfo = ref<IRuneTree[]>([])

  const getRuneInfo = async () => {
    const url = '/v2/runes'

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      runeInfo.value = response!.data
    }
  }

  const getRuneIcons = async (runes: IPerks) => {
    if (!runeInfo.value.length)
      await getRuneInfo()

    const primaryRuneTree = runeInfo.value.find(rune => rune.id === runes.perkStyle) || null
    const secondaryRuneTree = runeInfo.value.find(rune => rune.id === runes.perkSubStyle) || null

    let primaryRunes = primaryRuneTree?.slots.flatMap(slot => slot.runes).filter(rune => runes.perkIds.includes(rune.id)) || []
    const secondaryRunes = secondaryRuneTree?.slots.flatMap(slot => slot.runes).filter(rune => runes.perkIds.includes(rune.id)) || []

    const keyRune = primaryRunes[0]
    primaryRunes = primaryRunes.slice(1)

    const mappedRunes: Record<number, string> = {}

    mappedRunes[primaryRuneTree?.id || -1] = primaryRuneTree?.icon || ''
    mappedRunes[secondaryRuneTree?.id || -1] = secondaryRuneTree?.icon || ''

    mappedRunes[keyRune?.id || -1] = keyRune?.icon || ''

    primaryRunes.forEach((rune) => {
      mappedRunes[rune.id] = rune.icon
    })
    secondaryRunes.forEach((rune) => {
      mappedRunes[rune.id] = rune.icon
    })

    if (mappedRunes[-1])
      delete mappedRunes[-1]

    storageStore.getRuneIcons(mappedRunes)
  }

  return {
    runeInfo,
    getRuneInfo,
    getRuneIcons,
  }
})
