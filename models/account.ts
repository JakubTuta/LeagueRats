export interface IAccount {
  gameName: string
  tagLine: string
  puuid: string
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
