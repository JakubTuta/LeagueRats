import { getDownloadURL, ref } from 'firebase/storage'
import { useFirebase } from '~/helpers/useFirebase'

export const useStorageStore = defineStore('storage', () => {
  const { storage } = useFirebase()

  const getChampionIcon = async (championName: string) => {
    const storageRef = ref(storage, `champions/icons/${championName}.png`)

    const url = await getDownloadURL(storageRef)

    return url
  }

  return {
    getChampionIcon,
  }
})
