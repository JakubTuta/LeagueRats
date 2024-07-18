import type { DocumentData } from 'firebase/firestore'

export interface IAccount {
  gameName: string
  tagLine: string
  puuid: string
}

export class AccountModel implements IAccount {
  gameName: string
  tagLine: string
  puuid: string

  constructor(data: IAccount) {
    this.gameName = data.gameName
    this.tagLine = data.tagLine
    this.puuid = data.puuid
  }

  toMap(): IAccount {
    return {
      gameName: this.gameName,
      tagLine: this.tagLine,
      puuid: this.puuid,
    }
  }
}

export function mapAccount(data: DocumentData) {
  return new AccountModel(data as IAccount)
}
