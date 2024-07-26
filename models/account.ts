import { type DocumentData, Timestamp } from 'firebase/firestore'

export interface IAccountDetails {
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

export interface IAccount extends IAccountDetails, ISummoner {
  gameName: string
  tagLine: string
  puuid: string
  accountId: string
  profileIconId: number
  revisionDate: Timestamp
  id: string
  summonerLevel: number
}

export function mapAccount(accountDetails: IAccountDetails, summoner: ISummoner): IAccount
export function mapAccount(data: DocumentData): IAccount
export function mapAccount(arg1: IAccount | DocumentData, arg2?: ISummoner): IAccount {
  if (arg2) {
    const summoner = arg2 as ISummoner
    // @ts-expect-error revisionDate is a number
    summoner.revisionDate = new Timestamp(summoner.revisionDate / 1000, 0)

    return { ...arg1 as IAccount, ...summoner } as IAccount
  }
  else {
    const documentData = (arg1 as DocumentData).data() as IAccount
    // @ts-expect-error revisionDate is a number
    documentData.revisionDate = new Timestamp(documentData.revisionDate / 1000, 0)

    return documentData
  }
}
