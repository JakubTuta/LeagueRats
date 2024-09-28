export interface IProPlayer {
  player: string
  puuid: string[]
  region: 'LCK' | 'LEC' | 'LCS' | 'LPL'
  role: 'TOP' | 'JNG' | 'MID' | 'ADC' | 'SUP'
  team: string
}

export function mapIProPlayer(data: any): IProPlayer {
  return {
    player: data.player || '',
    puuid: data.puuid || [],
    region: data.region || '',
    role: data.role || '',
    team: data.team || '',
  }
}
