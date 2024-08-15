import { doc, getDoc } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IPerks } from '~/models/activeGame'
import type { IRuneInfo } from '~/models/runeInfo'

export const useRuneStore = defineStore('rune', () => {
  const { firestore } = useFirebase()
  const { locale } = useI18n()

  const storageStore = useStorageStore()

  const runeInfo = ref<IRuneInfo | null>(null)

  const getRuneInfo = async () => {
    try {
      const runeDoc = await getDoc(doc(firestore, 'help', 'runes'))

      const runeData = runeDoc.data() as IRuneInfo

      runeInfo.value = runeData
    }
    catch (error) {
      console.error(error)
    }
  }

  const getRuneIcons = async (runes: IPerks) => {
    if (!runeInfo.value)
      await getRuneInfo()

    if (!runeInfo.value)
      return

    const primaryRuneTree = runeInfo.value[locale.value].find(rune => rune.id === runes.perkStyle) || null
    const secondaryRuneTree = runeInfo.value[locale.value].find(rune => rune.id === runes.perkSubStyle) || null

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
