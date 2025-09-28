export interface IAccountDetails {
  gameName: string
  tagLine: string
  puuid: string
}

export interface IAccount extends IAccountDetails {
  region: string
}

export function mapAccount(data: any): IAccount {
  const account: IAccount = {
    gameName: data.gameName || '',
    tagLine: data.tagLine || '',
    puuid: data.puuid || '',
    region: data.region || '',
  }

  return account
}
