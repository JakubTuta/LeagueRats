/* eslint-disable unused-imports/no-unused-vars */
import axios from 'axios'
import type { IAccount, IAccountDetails, ISummoner } from '~/models/account'
import { type IActiveGame, mapActiveGame } from '~/models/activeGame'
import { type IChampionMastery, mapChampionMastery } from '~/models/championMastery'
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
      // console.error(error)

      return null
    }
  }

  const getSummonerDetailsByPuuid = async (puuid: string, region: string): Promise<ISummoner | null> => {
    try {
      const response = await callFirebaseFunction('summoner_details_by_puuid', { puuid, region })

      return response as ISummoner
    }
    catch (error: any) {
      // console.error(error)

      return null
    }
  }

  const getCurrentGameByPuuid = async (puuid: string, region: string): Promise<IActiveGame | null> => {
    try {
      const response = await callFirebaseFunction('active_game_by_puuid', { puuid, region })

      const activeGame = mapActiveGame(response)

      if (activeGame.gameType !== 'MATCHED' || (activeGame.gameMode !== 'CLASSIC' && activeGame.gameMode !== 'ARAM')) {
        return null
      }

      return activeGame
    }
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
      // console.error(error)

      return null
    }
  }

  const getFeaturedGames = async (): Promise<IActiveGame[]> => {
    try {
      const response = await callFirebaseFunction('featured_games', {})

      const acceptableGameModes = ['CLASSIC', 'ARAM']

      const games = response.map(mapActiveGame)
        .filter((game: IActiveGame) => game.gameType === 'MATCHED' && acceptableGameModes.includes(game.gameMode))

      if (games.length > 2) {
        return games.slice(0, 2)
      }

      return games
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const getLeagueEntryBySummonerId = async (summonerId: string, region: string): Promise<ILeagueEntry[]> => {
    try {
      const response = await callFirebaseFunction('league_entry_by_summoner_id', { summonerId, region })
      const leagueEntry = response.map(mapLeagueEntry)

      return leagueEntry
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const getChampionMasteryByPuuid = async (puuid: string, region: string): Promise<IChampionMastery[]> => {
    try {
      const response = await callFirebaseFunction('champion_mastery_by_puuid', { puuid, region })

      return response.map(mapChampionMastery)
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const getMatchHistoryByPuuid = async (puuid: string, optionalKeys: object, region: string): Promise<string[]> => {
    try {
      const response = await callFirebaseFunction('match_history_by_puuid', { puuid, ...optionalKeys, region })

      return response
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const findAccountsInAllRegions = async (gameName: string, tagLine: string): Promise<Record<string, IAccount | null>> => {
    try {
      const response = await callFirebaseFunction('accounts_in_all_regions', { gameName, tagLine })

      return response
    }
    catch (error: any) {
      console.error(error)

      return {}
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
    getChampionMasteryByPuuid,
    getMatchHistoryByPuuid,
    findAccountsInAllRegions,
  }
})
