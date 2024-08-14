/* eslint-disable unused-imports/no-unused-vars */
import axios from 'axios'
import type { IAccount, IAccountDetails, ISummoner } from '~/models/account'
import { type IActiveGame, mapActiveGame } from '~/models/activeGame'
import { type IChampionMastery, mapChampionMastery } from '~/models/championMastery'
import { type ILeagueEntry, mapLeagueEntry } from '~/models/leagueEntry'
import { type IMatchData, mapMatchData } from '~/models/matchData'

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

  const postFirebaseFunction = async (functionName: string, data: any): Promise<any> => {
    const response = await getAxios().post(`/${functionName}`, data)

    if (response.status !== 200) {
      throw new Error(response.data)
    }

    return response.data
  }

  const getFirebaseFunction = async (functionName: string): Promise<any> => {
    const response = await getAxios().get(`/${functionName}`)

    if (response.status !== 200) {
      throw new Error(response.data)
    }

    return response.data
  }

  const testConnection = async (): Promise<void> => {
    try {
      const response = await postFirebaseFunction('test_connection', {})

      // eslint-disable-next-line no-console
      console.log(response)
    }
    catch (error: any) {
      console.error(error)
    }
  }

  const getAccountDetailsByRiotId = async (username: string, tag: string): Promise<IAccountDetails | null> => {
    try {
      const response = await postFirebaseFunction('account_details_by_riot_id', { username, tag })

      return response as IAccountDetails
    }
    catch (error: any) {
      // console.error(error)

      return null
    }
  }

  const getSummonerDetailsByPuuid = async (puuid: string, region: string): Promise<ISummoner | null> => {
    try {
      const response = await postFirebaseFunction('summoner_details_by_puuid', { puuid, region })

      return response as ISummoner
    }
    catch (error: any) {
      // console.error(error)

      return null
    }
  }

  const getCurrentGameByPuuid = async (puuid: string, region: string): Promise<IActiveGame | null> => {
    try {
      const response = await postFirebaseFunction('active_game_by_puuid', { puuid, region })

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
      const response = await postFirebaseFunction('champion_positions', { championIds })

      return response
    }
    catch (error: any) {
      // console.error(error)

      return null
    }
  }

  const getFeaturedGames = async (): Promise<IActiveGame[]> => {
    try {
      const response = await postFirebaseFunction('featured_games', {})

      const acceptableGameModes = ['CLASSIC', 'ARAM']

      const games = (response.map(mapActiveGame) as IActiveGame[])
        .filter(game => game.gameType === 'MATCHED' && acceptableGameModes.includes(game.gameMode))

      games.sort((a, b) => {
        if (a.gameMode === 'CLASSIC' && b.gameMode !== 'CLASSIC') {
          return -1
        }
        if (a.gameMode !== 'CLASSIC' && b.gameMode === 'CLASSIC') {
          return 1
        }

        return 0
      })

      if (games.length > 2)
        return games.slice(0, 2)

      return games
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const getLeagueEntryBySummonerId = async (summonerId: string, region: string): Promise<ILeagueEntry[]> => {
    try {
      const response = await postFirebaseFunction('league_entry_by_summoner_id', { summonerId, region })
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
      const response = await postFirebaseFunction('champion_mastery_by_puuid', { puuid, region })

      return response.map(mapChampionMastery)
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const getAccountMatchHistory = async (account: IAccount, optionalKeys: object): Promise<string[]> => {
    try {
      const response = await postFirebaseFunction('match_history_by_puuid', { puuid: account.puuid, region: account.region, ...optionalKeys })

      return response
    }
    catch (error: any) {
      // console.error(error)

      return []
    }
  }

  const findAccountsInAllRegions = async (gameName: string, tagLine: string): Promise<Record<string, IAccount | null>> => {
    try {
      const response = await postFirebaseFunction('accounts_in_all_regions', { gameName, tagLine })

      return response
    }
    catch (error: any) {
      console.error(error)

      return {}
    }
  }

  const getMatchData = async (gameId: string): Promise<IMatchData | null> => {
    try {
      const response = await getFirebaseFunction(`match_data/${gameId}`)

      console.log(response)

      return mapMatchData(response)
    }
    catch (error: any) {
      console.error(error)

      return null
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
    getAccountMatchHistory,
    findAccountsInAllRegions,
    getMatchData,
  }
})
