import axios from 'axios'
import type { IAccount } from '~/models/accountModel'
import { ActiveGameModel } from '~/models/activeGame'

export const useRestStore = defineStore('rest', () => {
  const baseURL = 'https://europe-central2-league-rats.cloudfunctions.net'
  const HEADERS_FIREBASE = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Origin': '*',
  }

  function getAxios() {
    return axios.create({
      baseURL,
      headers: HEADERS_FIREBASE,
    })
  }

  const callFirebaseFunction = async (functionName: string, data: any): Promise<any> => {
    const response = await getAxios().post(`/${functionName}`, data)

    if (response.status !== 200) {
      throw new Error(response.data)
    }

    return response.data
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
      const response = await callFirebaseFunction('account_details_by_riot_id', { username, tag })

      return response as IAccount
    }
    catch (error: any) {
      console.error(error)

      return null
    }
  }

  const getCurrentGameByPuuid = async (puuid: string): Promise<ActiveGameModel | null> => {
    try {
      const response = await callFirebaseFunction('active_game_by_puuid', { puuid })

      const model = new ActiveGameModel(response, null)

      if (model.gameType !== 'MATCHED' || (model.gameMode !== 'CLASSIC' && model.gameMode !== 'ARAM')) {
        return null
      }

      return model
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
    catch (error: any) {
      return null
    }
  }

  const findChampionsPositions = async (championIds: number[]): Promise<Record<number, string> | null> => {
    try {
      const response = await callFirebaseFunction('champion_positions', { championIds })

      return response
    }
    catch (error: any) {
      console.error(error)

      return null
    }
  }

  const getFeaturedGames = async (): Promise<ActiveGameModel[]> => {
    try {
      const response = await callFirebaseFunction('featured_games', {})

      const acceptableGameModes = ['CLASSIC', 'ARAM']

      const games = response.gameList.map((game: any) => new ActiveGameModel(game, null))
        .filter((game: ActiveGameModel) => game.gameType === 'MATCHED')
        .filter((game: ActiveGameModel) => acceptableGameModes.includes(game.gameMode))

      if (games.length > 2) {
        return games.slice(0, 2)
      }

      return games
    }
    catch (error: any) {
      console.error(error)

      return []
    }
  }

  return {
    testConnection,
    getAccountDetailsByRiotId,
    getCurrentGameByPuuid,
    findChampionsPositions,
    getFeaturedGames,
  }
})
