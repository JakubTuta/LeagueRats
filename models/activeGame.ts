import { Timestamp } from 'firebase/firestore'

export interface IPerks {
  perkIds: number[]
  perkStyle: number
  perkSubStyle: number
}

export interface IParticipant {
  championId: number
  perks: IPerks
  teamId: number
  summonerId: string
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
  gameQueueConfigId: 'NORMAL' | 'SOLOQ' | 'FLEXQ'
}

export function mapActiveGame(data: IActiveGame): IActiveGame {
  // @ts-expect-error gameStartTime is a number
  data.gameStartTime = new Timestamp(data.gameStartTime / 1000, 0)
  data.participants = data.participants.map(mapParticipant)
  // @ts-expect-error gameQueueConfigId is a number
  data.gameQueueConfigId = mapGameConfig(data.gameQueueConfigId)

  return data
}

function mapParticipant(participant: IParticipant): IParticipant {
  return {
    ...participant,
    gameName: participant.riotId.split('#')[0],
    tagLine: participant.riotId.split('#')[1],
  } as IParticipant
}

function mapGameConfig(gameQueueConfigId: number): 'NORMAL' | 'SOLOQ' | 'FLEXQ' {
  switch (gameQueueConfigId) {
    case 420:
      return 'SOLOQ'
    case 440:
      return 'FLEXQ'
    case 450:
    default:
      return 'NORMAL'
  }
}
