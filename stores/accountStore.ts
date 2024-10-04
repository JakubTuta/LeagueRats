import { collection, getDocs, query, updateDoc, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IAccount, IAccountDetails } from '~/models/account'

export const useAccountStore = defineStore('account', () => {
  const { firestore } = useFirebase()

  const restStore = useRestStore()

  const collectionAccounts = collection(firestore, 'accounts')

  function getAccount(puuid: string, region: string, isSaveAccount: boolean): Promise<IAccount | null>
  function getAccount(gameName: string, tagLine: string, region: string, isSaveAccount: boolean): Promise<IAccount | null>
  async function getAccount(...args: any[]): Promise<IAccount | null> {
    const isSaveAccount = args.pop() as boolean
    const region = args.pop() as string

    if (args.length === 1) {
      const puuid = args[0] as string

      const account = await restStore.getAccountWithPuuid(region, puuid)

      if (isSaveAccount && account)
        restStore.saveAccount(region, puuid)

      return account
    }
    else if (args.length === 2) {
      const gameName = args[0] as string
      const tagLine = args[1] as string

      const account = await restStore.getAccountWithGameName(region, gameName, tagLine)

      if (isSaveAccount && account)
        restStore.saveAccount(region, null, gameName, tagLine)

      return account
    }

    return null
  }

  const updateAccount = async (account: IAccount, newAccount: IAccountDetails) => {
    const q = query(collectionAccounts, where('puuid', '==', account.puuid))

    const querySnapshot = await getDocs(q)
    if (querySnapshot.empty)
      return

    const doc = querySnapshot.docs[0]

    try {
      await updateDoc(doc.ref, { ...newAccount })
    }
    catch (error) {
      console.error(error)
    }
  }

  return {
    getAccount,
    updateAccount,
  }
})
