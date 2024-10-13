import { doc, getDoc } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'

export const useChampionStore = defineStore('championStore', () => {
  const champions = ref<Record<number, { title: string, value: string }>>({})

  const { firestore } = useFirebase()

  const getChampions = async () => {
    try {
      const document = doc(firestore, 'help', 'champions')
      const snapshot = await getDoc(document)

      if (!snapshot.exists()) {
        return
      }

      champions.value = snapshot.data() || null
    }
    catch (error) {
      console.error(error)
    }
  }

  return {
    champions,
    getChampions,
  }
})
