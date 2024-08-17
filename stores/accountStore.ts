import { addDoc, collection, getDocs, query, where } from 'firebase/firestore'
import { useFirebase } from '~/helpers/useFirebase'
import type { IAccount, IAccountDetails, ISummoner } from '~/models/account'
import { mapAccount } from '~/models/account'

export const useAccountStore = defineStore('account', () => {
  const { firestore } = useFirebase()

  const restStore = useRestStore()

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

  function findAccountInDatabase(puuid: string): Promise<IAccount | null>
  function findAccountInDatabase(gameName: string, tagLine: string, region: string): Promise<IAccount | null>
  async function findAccountInDatabase(...args: any[]): Promise<IAccount | null> {
    if (args.length === 1) {
      const puuid = args[0] as string

      const q = query(collectionAccounts, where('puuid', '==', puuid))

      const querySnapshot = await getDocs(q)

      if (querySnapshot.empty)
        return null

      const doc = mapAccount(querySnapshot.docs[0])

      return doc
    }
    else if (args.length === 3) {
      const gameName = args[0] as string
      const tagLine = args[1] as string
      const region = args[2] as string

      const q = query(collectionAccounts, where('gameName', '==', gameName), where('tagLine', '==', tagLine), where('region', '==', region))

      const querySnapshot = await getDocs(q)

      if (querySnapshot.empty)
        return null

      const doc = mapAccount(querySnapshot.docs[0])

      return doc
    }

    return null
  }

  function getAccount(puuid: string, region: string, isSaveAccount: boolean): Promise<IAccount | null>
  function getAccount(gameName: string, tagLine: string, region: string, isSaveAccount: boolean): Promise<IAccount | null>
  async function getAccount(...args: any[]): Promise<IAccount | null> {
    const isSaveAccount = args.pop() as boolean
    const region = args.pop() as string

    if (args.length === 1) {
      const puuid = args[0] as string

      let account = await findAccountInDatabase(puuid)

      if (account)
        return account

      const accountDetails = await restStore.getAccountDetails(puuid)

      if (!accountDetails)
        return null

      const summonerDetails = await restStore.getSummonerDetailsByPuuid(puuid, region)

      if (!summonerDetails)
        return null

      if (isSaveAccount)
        saveAccount(accountDetails, summonerDetails, region)

      account = mapAccount(accountDetails, summonerDetails, region)

      return account
    }
    else if (args.length === 2) {
      const gameName = args[0] as string
      const tagLine = args[1] as string

      let account = await findAccountInDatabase(gameName, tagLine, region)

      if (account)
        return account

      const accountDetails = await restStore.getAccountDetails(gameName, tagLine)

      if (!accountDetails)
        return null

      const summonerDetails = await restStore.getSummonerDetailsByPuuid(accountDetails.puuid, region)

      if (!summonerDetails)
        return null

      if (isSaveAccount)
        saveAccount(accountDetails, summonerDetails, region)

      account = mapAccount(accountDetails, summonerDetails, region)

      return account
    }

    return null
  }

  return {
    saveAccount,
    findAccountInDatabase,
    getAccount,
  }
})
