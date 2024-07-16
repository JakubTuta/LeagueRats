import { collection, getDocs, query, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'

export const useUserStore = defineStore('user', () => {
  const { firestore } = useFirebase()
  const collectionUsers = collection(firestore, 'users')

  const checkIfUserExists = async (username: string, tag: string) => {
    const q = query(collectionUsers, where('username', '==', username), where('tag', '==', tag))

    try {
      const response = await getDocs(q)

      return !response.empty
    }
    catch (error) {
      console.error(error)

      return false
    }
  }

  return {
    checkIfUserExists,
  }
})
