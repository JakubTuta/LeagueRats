export interface IAccountDetails {
  gameName: string
  tagLine: string
  puuid: string
}

export interface ISummoner {
  accountId: string
  profileIconId: number
  id: string
  summonerLevel: number
}

export interface IAccount extends IAccountDetails, ISummoner {
  region: string
}

export function mapAccount(data: any): IAccount {
  const account: IAccount = {
    gameName: data.gameName || '',
    tagLine: data.tagLine || '',
    puuid: data.puuid || '',
    accountId: data.accountId || '',
    profileIconId: data.profileIconId || '',
    id: data.id || '',
    summonerLevel: data.summonerLevel || '',
    region: data.region || '',
  }

  return account
}
