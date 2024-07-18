import type { IAccount } from '~/models/accountModel'
import { ActiveGameModel } from '~/models/activeGame'

export const useRestStore = defineStore('rest', () => {
  const baseURL = 'https://europe-central2-league-rats.cloudfunctions.net'
  const HEADERS_FIREBASE = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Origin': '*',
  }

  const callFirebaseFunction = async (functionName: string, data: any): Promise<any> => {
    const url = `${baseURL}/${functionName}`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: HEADERS_FIREBASE,
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Error fetching data from server')
      }

      const responseData = await response.json()

      return responseData
    }
    catch (error: any) {
      throw new Error(String(error))
    }
  }

  const testConnection = async (): Promise<void> => {
    try {
      const response = await callFirebaseFunction('test_connection', {})

      console.log(response)
    }
    catch (error: any) {
      console.error(error)
    }
  }

  const getAccountDetailsByRiotId = async (username: string, tag: string): Promise<IAccount | null> => {
    try {
      const response = await callFirebaseFunction('get_account_details_by_riot_id', { username, tag })

      return response as IAccount
    }
    catch (error: any) {
      console.error(error)

      return null
    }
  }

  const getCurrentGameByPuuid = async (puuid: string): Promise<ActiveGameModel | null> => {
    try {
      const response = await callFirebaseFunction('get_active_game_by_puuid', { puuid })

      const model = new ActiveGameModel(response, null)

      return model
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
    catch (error: any) {
      return null
    }
  }

  return {
    testConnection,
    getAccountDetailsByRiotId,
    getCurrentGameByPuuid,
  }
})
