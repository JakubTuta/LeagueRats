export interface IProAccount {
  player: string
  gameName: string | null
  tagLine: string | null
  puuid: string | null
  region: 'LEC' | 'LCS' | 'LCK' | 'LPL'
  role: 'Top' | 'JNG' | 'MID' | 'ADC' | 'SUP'
  team: string
}

export function mapIProAccount(data: any): IProAccount {
  return {
    player: data.player || '',
    gameName: data.gameName || null,
    tagLine: data.tagLine || null,
    puuid: data.puuid || null,
    region: data.region,
    role: data.role,
    team: data.team,
  }
}
