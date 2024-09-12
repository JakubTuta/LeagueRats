/* eslint-disable unused-imports/no-unused-vars */
import axios from 'axios'
import type { IAccount, IAccountDetails, ISummoner } from '~/models/account'
import type { IActiveGame } from '~/models/activeGame'
import { mapActiveGame } from '~/models/activeGame'
import type { IChampionMastery } from '~/models/championMastery'
import { mapChampionMastery } from '~/models/championMastery'
import type { ILeagueEntry } from '~/models/leagueEntry'
import { mapLeagueEntry } from '~/models/leagueEntry'
import type { IMatchData } from '~/models/matchData'
import { mapMatchData } from '~/models/matchData'
import { type IProActiveGame, mapProActiveGame } from '~/models/proActiveGame'

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
    let response: any

    try {
      response = await getAxios().post(`/${functionName}`, data)
    }
    catch (error: any) {
      console.error(error)
    }

    if (response.status !== 200) {
      throw new Error(response.data)
    }

    return response.data
  }

  const getFirebaseFunction = async (functionName: string): Promise<any> => {
    let response: any = null

    try {
      response = (await getAxios().get(`/${functionName}`))
    }
    catch (error: any) {
      console.error(error)
    }

    return response
  }

  const testConnection = async (): Promise<void> => {
    const response = await getFirebaseFunction('test_connection')

    // eslint-disable-next-line no-console
    console.log(response)
  }

  function getAccountDetails(puuid: string): Promise<IAccountDetails | null>
  function getAccountDetails(username: string, tag: string): Promise<IAccountDetails | null>
  async function getAccountDetails(...args: any[]): Promise<IAccountDetails | null> {
    if (args.length === 1) {
      const puuid = args[0] as string

      const response = await getFirebaseFunction(`account_details?puuid=${puuid}`)

      if (!response || response.status !== 200)
        return null

      return response.data as IAccountDetails
    }
    else if (args.length === 2) {
      const username = args[0] as string
      const tag = args[1] as string

      const response = await getFirebaseFunction(`account_details?username=${username}&tag=${tag}`)

      if (!response || response.status !== 200)
        return null

      return response.data as IAccountDetails
    }

    return null
  }

  const getSummonerDetailsByPuuid = async (puuid: string, region: string): Promise<ISummoner | null> => {
    const response = await getFirebaseFunction(`summoner_details/${region}/${puuid}`)

    if (!response || response.status !== 200)
      return null

    return response.data as ISummoner
  }

  const getCurrentGameByPuuid = async (puuid: string, region: string): Promise<IActiveGame | null> => {
    const response = await getFirebaseFunction(`active_game/${region}/${puuid}`)

    if (!response || response.status !== 200)
      return null

    const activeGame = mapActiveGame(response.data)

    if (activeGame.gameType !== 'MATCHED' || (activeGame.gameMode !== 'CLASSIC' && activeGame.gameMode !== 'ARAM')) {
      return null
    }

    return activeGame
  }

  const findChampionsPositions = async (championIds: number[]): Promise<Record<number, string> | null> => {
    const stringChampionIds = championIds.join('.')
    const response = await getFirebaseFunction(`champion_positions/${stringChampionIds}`)

    if (!response || response.status !== 200)
      return {}

    return response.data
  }

  const getFeaturedGames = async (): Promise<IActiveGame[]> => {
    const response = await getFirebaseFunction('featured_games')

    if (!response || response.status !== 200)
      return []

    const acceptableGameModes = ['CLASSIC', 'ARAM']

    const games = (response.data.map(mapActiveGame) as IActiveGame[])
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

  const getLeagueEntryBySummonerId = async (summonerId: string, region: string): Promise<ILeagueEntry[]> => {
    const response = await getFirebaseFunction(`league_entry/${region}/${summonerId}`)

    if (!response || response.status !== 200)
      return []

    const leagueEntry = response.data.map(mapLeagueEntry)

    return leagueEntry
  }

  const getChampionMasteryByPuuid = async (puuid: string, region: string): Promise<IChampionMastery[]> => {
    const response = await getFirebaseFunction(`champion_mastery/${region}/${puuid}`)

    if (!response || response.status !== 200)
      return []

    return response.data.map(mapChampionMastery)
  }

  const getAccountMatchHistory = async (account: IAccount, optionalKeys: object): Promise<string[]> => {
    let response: any = null

    if (Object.keys(optionalKeys).length) {
      const urlVariables = Object.entries(optionalKeys).map(([key, value]) => `${key}=${value}`).join('&')
      response = await getFirebaseFunction(`match_history/${account.region}/${account.puuid}?${urlVariables}`)
    }
    else {
      response = await getFirebaseFunction(`match_history/${account.region}/${account.puuid}`)
    }

    if (!response || response.status !== 200)
      return []

    return response.data
  }

  const findAccountsInAllRegions = async (gameName: string, tagLine: string): Promise<Record<string, IAccount | null>> => {
    const response = await getFirebaseFunction(`accounts_in_all_regions/${gameName}/${tagLine}`)

    if (!response || response.status !== 200)
      return {}

    return response.data
  }

  const getMatchData = async (gameId: string): Promise<IMatchData | null> => {
    const response = await getFirebaseFunction(`match_data/${gameId}`)

    if (!response || response.status !== 200)
      return null

    return mapMatchData(response.data)
  }

  const getActiveProGames = async (): Promise<IProActiveGame[]> => {
    const response = await getFirebaseFunction('active_pro_games')

    if (!response || response.status !== 200)
      return []

    const promises = response.data.map((data: any[]) => mapProActiveGame({ player: data[0], game: data[1] }))
    const proActiveGames = (await Promise.all(promises)).filter((game: IProActiveGame | null) => game !== null)

    return proActiveGames
  }

  return {
    testConnection,
    getAccountDetails,
    getSummonerDetailsByPuuid,
    getCurrentGameByPuuid,
    findChampionsPositions,
    getFeaturedGames,
    getLeagueEntryBySummonerId,
    getChampionMasteryByPuuid,
    getAccountMatchHistory,
    findAccountsInAllRegions,
    getMatchData,
    getActiveProGames,
  }
})
