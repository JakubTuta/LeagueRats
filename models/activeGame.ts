import { Timestamp } from 'firebase/firestore'
import { queueIdToType } from '~/helpers/queueTypes'

type TGameConfig = 'NORMAL' | 'SOLOQ' | 'FLEXQ'

export interface IPerks {
  perkIds: number[]
  perkStyle: number
  perkSubStyle: number
}

export interface IParticipant {
  championId: number
  perks: IPerks
  teamId: number
  riotId: string
  gameName: string
  tagLine: string
  puuid: string
  spell1Id: number
  spell2Id: number
}

export interface IBannedChampion {
  pickTurn: number
  championId: number
  teamId: number
}

export interface IActiveGame {
  gameId: number
  gameType: string
  gameStartTime: Timestamp
  mapId: number
  gameLength: number
  gameMode: string
  bannedChampions: IBannedChampion[]
  participants: IParticipant[]
  platformId: string
  gameQueueConfigId: TGameConfig
}

export function mapActiveGame(data: IActiveGame): IActiveGame {
  data.gameStartTime = mapGameStartTime(data.gameStartTime)
  data.gameQueueConfigId = mapGameConfig(data.gameQueueConfigId)
  data.participants = data.participants.map(mapParticipant)

  return data
}

function mapGameStartTime(gameStartTime: number | Timestamp | string): Timestamp {
  if (gameStartTime instanceof Timestamp) {
    return gameStartTime
  }

  if (typeof gameStartTime === 'string') {
    return Timestamp.fromDate(new Date(gameStartTime))
  }

  return new Timestamp(gameStartTime / 1000, 0)
}

function mapParticipant(participant: IParticipant): IParticipant {
  return {
    ...participant,
    gameName: participant.riotId.split('#')[0],
    tagLine: participant.riotId.split('#')[1],
  } as IParticipant
}

function mapGameConfig(gameQueueConfigId: string | number): TGameConfig {
  if (typeof gameQueueConfigId === 'string') {
    return gameQueueConfigId as TGameConfig
  }

  try {
    return queueIdToType[gameQueueConfigId] as TGameConfig
  }

  catch (error: any) {
    return 'NORMAL'
  }
}
