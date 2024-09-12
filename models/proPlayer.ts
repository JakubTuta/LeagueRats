export interface IProPlayer {
  gameName: string | null
  tagLine: string | null
  player: string
  puuid: string | null
  region: 'KR' | 'EUW' | 'NA' | 'CN'
  role: 'TOP' | 'JNG' | 'MID' | 'ADC' | 'SUP'
  team: string
}

export function mapIProPlayer(data: any): IProPlayer {
  return {
    gameName: data.gameName,
    tagLine: data.tagLine,
    player: data.player,
    puuid: data.puuid,
    region: data.region,
    role: data.role,
    team: data.team,
  } as IProPlayer
}
