import { type DocumentData, type DocumentReference, Timestamp } from 'firebase/firestore'

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

export class ActiveGameModel implements IActiveGame {
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

  reference: DocumentReference | null

  constructor(data: IActiveGame, reference: DocumentReference | null) {
    this.gameId = data.gameId
    this.gameType = data.gameType
    //   @ts-expect-error gameStartTime is a number
    this.gameStartTime = new Timestamp(data.gameStartTime, 0)
    this.mapId = data.mapId
    this.gameLength = data.gameLength
    this.platformId = data.platformId
    this.gameMode = data.gameMode
    this.bannedChampions = data.bannedChampions
    this.gameQueueConfigId = data.gameQueueConfigId
    this.observers = data.observers
    this.participants = data.participants

    this.reference = reference
  }

  toMap(): IActiveGame {
    return {
      gameId: this.gameId,
      gameType: this.gameType,
      gameStartTime: this.gameStartTime,
      mapId: this.mapId,
      gameLength: this.gameLength,
      platformId: this.platformId,
      gameMode: this.gameMode,
      bannedChampions: this.bannedChampions,
      gameQueueConfigId: this.gameQueueConfigId,
      observers: this.observers,
      participants: this.participants,
    }
  }
}

export function mapActiveGame(document: DocumentData) {
  return new ActiveGameModel(document.data(), document.ref)
}
