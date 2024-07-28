import axios from 'axios'
import type { IAccountDetails, ISummoner } from '~/models/account'
import { type IActiveGame, mapActiveGame } from '~/models/activeGame'
import { type ILeagueEntry, mapLeagueEntry } from '~/models/leagueEntry'

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

      // eslint-disable-next-line no-console
      console.log(response)
    }
    catch (error: any) {
      console.error(error)
    }
  }

  const getAccountDetailsByRiotId = async (username: string, tag: string): Promise<IAccountDetails | null> => {
    try {
      const response = await callFirebaseFunction('account_details_by_riot_id', { username, tag })

      return response as IAccountDetails
    }
    catch (error: any) {
      console.error(error)

      return null
    }
  }

  const getSummonerDetailsByPuuid = async (puuid: string): Promise<ISummoner | null> => {
    try {
      const response = await callFirebaseFunction('summoner_details_by_puuid', { puuid })

      return response as ISummoner
    }
    catch (error: any) {
      console.error(error)

      return null
    }
  }

  const getCurrentGameByPuuid = async (puuid: string): Promise<IActiveGame | null> => {
    try {
      const response = await callFirebaseFunction('active_game_by_puuid', { puuid })

      const activeGame = mapActiveGame(response)

      if (activeGame.gameType !== 'MATCHED' || (activeGame.gameMode !== 'CLASSIC' && activeGame.gameMode !== 'ARAM')) {
        return null
      }

      return activeGame
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

  const getFeaturedGames = async (): Promise<IActiveGame[]> => {
    try {
      const response = await callFirebaseFunction('featured_games', {})

      const acceptableGameModes = ['CLASSIC', 'ARAM']

      const games = response.gameList.map(mapActiveGame)
        .filter((game: IActiveGame) => game.gameType === 'MATCHED' && acceptableGameModes.includes(game.gameMode))

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

  const getLeagueEntryBySummonerId = async (summonerId: string): Promise<ILeagueEntry[]> => {
    try {
      const response = await callFirebaseFunction('league_entry_by_summoner_id', { summonerId })
      const leagueEntry = response.map(mapLeagueEntry)

      return leagueEntry
    }
    catch (error: any) {
      console.error(error)

      return []
    }
  }

  return {
    testConnection,
    getAccountDetailsByRiotId,
    getSummonerDetailsByPuuid,
    getCurrentGameByPuuid,
    findChampionsPositions,
    getFeaturedGames,
    getLeagueEntryBySummonerId,
  }
})
