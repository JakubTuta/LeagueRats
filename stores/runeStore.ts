import { doc, getDoc } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IRuneInfo } from '~/models/runeInfo'

export const useRuneStore = defineStore('rune', () => {
  const { firestore } = useFirebase()

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

  return {
    runeInfo,
    getRuneInfo,
  }
})
