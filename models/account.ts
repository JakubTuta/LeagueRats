import type { DocumentData } from 'firebase/firestore'
import { Timestamp } from 'firebase/firestore'

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
  region: string
}

export function mapAccount(accountDetails: IAccountDetails, summoner: ISummoner, region: string): IAccount
export function mapAccount(data: DocumentData): IAccount
export function mapAccount(arg1: IAccountDetails | DocumentData, summoner?: ISummoner, region?: string): IAccount {
  if (summoner && region) {
    return {
      gameName: arg1.gameName,
      tagLine: arg1.tagLine,
      puuid: arg1.puuid,
      accountId: summoner.accountId,
      id: summoner.id,
      region,
      profileIconId: summoner.profileIconId,
      // @ts-expect-error summoner.revisionDate is a number
      revisionDate: new Timestamp(summoner.revisionDate / 1000, 0),
      summonerLevel: summoner.summonerLevel,
    }
  }
  else {
    const documentData = (arg1 as DocumentData).data()

    return documentData
  }
}
