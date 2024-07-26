import { type DocumentData, Timestamp } from 'firebase/firestore'

export interface IGameCustomizationObject {
  category: string
  content: string
}

export interface IPerks {
  perkIds: number[]
  perkStyle: number
  perkSubStyle: number
}

export interface IParticipant {
  championId: number
  perks: IPerks[]
  profileIconId: number
  bot: boolean
  teamId: number
  summonerId: string
  riotId: string
  gameName: string
  tagLine: string
  puuid: string
  spell1Id: number
  spell2Id: number
  gameCustomizationObjects: IGameCustomizationObject[]
}

export interface IObserver {
  encryptionKey: string
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
  platformId: string
  gameMode: string
  bannedChampions: IBannedChampion[]
  gameQueueConfigId: number
  observers: IObserver
  participants: IParticipant[]
}

export function mapActiveGame(document: DocumentData): IActiveGame {
  const documentData = document.data() as IActiveGame
  // @ts-expect-error gameStartTime is a number
  documentData.gameStartTime = new Timestamp(documentData.gameStartTime / 1000, 0)
  documentData.participants = documentData.participants.map(mapParticipant)

  return documentData
}

function mapParticipant(participant: IParticipant): IParticipant {
  return {
    ...participant,
    gameName: participant.riotId.split('#')[0],
    tagLine: participant.riotId.split('#')[1],
  } as IParticipant
}
