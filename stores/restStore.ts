import type { IAccount } from '~/models/accountModel'

export const useRestStore = defineStore('rest', () => {
  const baseURL = 'https://europe-central2-league-rats.cloudfunctions.net'
  const HEADERS_FIREBASE = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Origin': '*',
  }

  const callFirebaseFunction = async (functionName: string, data: any) => {
    const url = `${baseURL}/${functionName}`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: HEADERS_FIREBASE,
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        console.error(response)

        return null
      }

      const responseData = await response.json()

      return responseData
    }
    catch (error) {
      console.error(error)
    }
  }

  const testConnection = async () => {
    const response = await callFirebaseFunction('test_connection', {})

    console.log(response)
  }

  const getAccountDetailsByRiotId = async (username: string, tag: string) => {
    const response = await callFirebaseFunction('get_account_details_by_riot_id', { username, tag })

    return response as IAccount | null
  }

  return {
    testConnection,
    getAccountDetailsByRiotId,
  }
})
