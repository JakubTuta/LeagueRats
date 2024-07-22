import { getDownloadURL, ref } from 'firebase/storage'
import { useFirebase } from '~/helpers/useFirebase'

export const useStorageStore = defineStore('storage', () => {
  const { storage } = useFirebase()

  const championIconUrls: Record<string, string> = {}

  const getChampionIcon = async (championName: string) => {
    if (championIconUrls[championName]) {
      return championIconUrls[championName]
    }

    const storageRef = ref(storage, `champions/icons/${championName}.png`)

    const url = await getDownloadURL(storageRef)

    championIconUrls[championName] = url

    return url
  }

  return {
    getChampionIcon,
  }
})
