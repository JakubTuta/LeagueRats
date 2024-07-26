import { type DocumentData, Timestamp } from 'firebase/firestore'

export interface IAccount {
  gameName: string
  tagLine: string
  puuid: string
}

export interface ISummoner {
  accountId: string
  profileIconId: number
  revisionDate: Timestamp
  id: string
  summonerLevel: number
}

export class AccountModel implements IAccount, ISummoner {
  gameName: string
  tagLine: string
  puuid: string

  accountId: string
  profileIconId: number
  revisionDate: Timestamp
  id: string
  summonerLevel: number

  constructor(data: IAccount & ISummoner) {
    this.gameName = data.gameName || ''
    this.tagLine = data.tagLine || ''
    this.puuid = data.puuid || ''
    this.accountId = data.accountId || ''
    this.profileIconId = data.profileIconId || 0
    // @ts-expect-error data.revisionDate is a number
    this.revisionDate = new Timestamp(data.revisionDate / 1000, 0) || Timestamp.now()
    this.id = data.id || ''
    this.summonerLevel = data.summonerLevel || 0
  }

  toMap(): IAccount & ISummoner {
    return {
      gameName: this.gameName,
      tagLine: this.tagLine,
      puuid: this.puuid,
      accountId: this.accountId,
      profileIconId: this.profileIconId,
      revisionDate: this.revisionDate,
      id: this.id,
      summonerLevel: this.summonerLevel,
    }
  }
}

export function mapAccount(account: IAccount, summoner: ISummoner): AccountModel
export function mapAccount(data: DocumentData): AccountModel
export function mapAccount(arg1: IAccount | DocumentData, arg2?: ISummoner): AccountModel {
  if (arg2) {
    return new AccountModel({ ...arg1 as IAccount, ...arg2 as ISummoner })
  }
  else {
    return new AccountModel((arg1 as DocumentData).data())
  }
}
