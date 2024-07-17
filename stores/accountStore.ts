import { addDoc, collection, getDocs, query, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IAccount } from '~/models/accountModel'

export const useAccountStore = defineStore('account', () => {
  const { firestore } = useFirebase()
  const collectionAccounts = collection(firestore, 'accounts')

  const getAccountDetails = async (gameName: string, tagLine: string) => {
    const q = query(collectionAccounts, where('gameName', '==', gameName), where('tagLine', '==', tagLine))

    try {
      const response = await getDocs(q)

      if (response.empty) {
        return null
      }

      const data = response.docs[0].data() as IAccount

      return data
    }
    catch (error) {
      console.error(error)

      return null
    }
  }

  const saveAccount = async (account: IAccount) => {
    try {
      await addDoc(collectionAccounts, account)
    }
    catch (error) {
      console.error(error)
    }
  }

  return {
    getAccountDetails,
    saveAccount,
  }
})
