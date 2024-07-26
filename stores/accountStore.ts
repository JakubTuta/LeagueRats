import { addDoc, collection, getDocs, query, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IAccount, IAccountDetails, ISummoner } from '~/models/account'
import { mapAccount } from '~/models/account'

export const useAccountStore = defineStore('account', () => {
  const { firestore } = useFirebase()

  const collectionAccounts = collection(firestore, 'accounts')

  function saveAccount(account: IAccount): Promise<void>
  function saveAccount(accountDetails: IAccountDetails, summonerDetails: ISummoner): Promise<void>
  async function saveAccount(...args: any[]): Promise<void> {
    if (args.length === 1) {
      const account = args[0]

      try {
        await addDoc(collectionAccounts, account)
      }
      catch (error) {
        console.error(error)
      }
    }
    else if (args.length === 2) {
      const accountDetails = args[0] as IAccount
      const summonerDetails = args[1] as ISummoner
      const account = mapAccount(accountDetails, summonerDetails)

      try {
        await addDoc(collectionAccounts, account)
      }
      catch (error) {
        console.error(error)
      }
    }
  }

  const findAccount = async (gameName: string, tagLine: string): Promise<IAccount | null> => {
    const q = query(collectionAccounts, where('gameName', '==', gameName), where('tagLine', '==', tagLine))

    const querySnapshot = await getDocs(q)

    if (querySnapshot.empty)
      return null

    const doc = mapAccount(querySnapshot.docs[0])

    return doc
  }

  return {
    saveAccount,
    findAccount,
  }
})
