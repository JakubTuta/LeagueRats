import { addDoc, collection, getDocs, query, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IAccount, ISummoner } from '~/models/account'
import { AccountModel, mapAccount } from '~/models/account'

export const useAccountStore = defineStore('account', () => {
  const { firestore } = useFirebase()

  const collectionAccounts = collection(firestore, 'accounts')

  function saveAccount(account: AccountModel): Promise<void>
  function saveAccount(accountDetails: IAccount, summonerDetails: ISummoner): Promise<void>
  async function saveAccount(...args: any[]): Promise<void> {
    if (args.length === 1 && args[0] instanceof AccountModel) {
      const account = args[0]
      try {
        await addDoc(collectionAccounts, account.toMap())
      }
      catch (error) {
        console.error(error)
      }
    }
    else if (args.length === 2 && typeof args[0] === 'object' && typeof args[1] === 'object') {
      const accountDetails = args[0] as IAccount
      const summonerDetails = args[1] as ISummoner
      const account = new AccountModel({ ...accountDetails, ...summonerDetails })
      try {
        await addDoc(collectionAccounts, account.toMap())
      }
      catch (error) {
        console.error(error)
      }
    }
  }

  const findAccount = async (gameName: string, tagLine: string): Promise<AccountModel | null> => {
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
