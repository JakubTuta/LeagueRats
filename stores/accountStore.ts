import { addDoc, collection, getDocs, query, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IAccount, IAccountDetails, ISummoner } from '~/models/account'
import { mapAccount } from '~/models/account'

export const useAccountStore = defineStore('account', () => {
  const { firestore } = useFirebase()

  const collectionAccounts = collection(firestore, 'accounts')

  function saveAccount(account: IAccount): Promise<void>
  function saveAccount(accountDetails: IAccountDetails, summonerDetails: ISummoner, region: string): Promise<void>
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
    else if (args.length === 3) {
      const accountDetails = args[0] as IAccount
      const summonerDetails = args[1] as ISummoner
      const region = args[2] as string

      const account = mapAccount(accountDetails, summonerDetails, region)

      try {
        await addDoc(collectionAccounts, account)
      }
      catch (error) {
        console.error(error)
      }
    }
  }

  const findAccount = async (gameName: string, tagLine: string, region: string): Promise<IAccount | null> => {
    const q = query(collectionAccounts, where('gameName', '==', gameName), where('tagLine', '==', tagLine), where('region', '==', region))

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
