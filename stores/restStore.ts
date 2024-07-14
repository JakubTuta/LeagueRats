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
        throw new Error(`HTTP error! Error: ${response}`)
      }

      const responseData = await response.json()

      return responseData
    }
    catch (error) {
      throw new Error(`Error calling Firebase function ${functionName}: ${error}`)
    }
  }

  const testConnection = async () => {
    try {
      const response = await callFirebaseFunction('test_connection', {})

      console.log(response)
    }
    catch (error) {
      console.error(error)

      throw error
    }
  }

  const getAccountDetailsByRiotId = async (username: string, tag: string) => {
    try {
      const response = await callFirebaseFunction('account_details_by_riot_id', {
        username,
        tag,
      })

      console.log(response)

      return response
    }
    catch (error) {
      console.error(error)

      throw error
    }
  }

  return {
    testConnection,
    getAccountDetailsByRiotId,
  }
})
