import type { DocumentData } from 'firebase/firestore'

export interface ILeagueEntry {
  leagueId: string
  summonerId: string
  queueType: string
  tier: string
  rank: string
  leaguePoints: number
  wins: number
  losses: number
  hotStreak: boolean
  veteran: boolean
  freshBlood: boolean
  inactive: boolean
  miniSeries: {
    target: number
    wins: number
    losses: number
    progress: string
  }
}

export function mapLeagueEntry(data: ILeagueEntry | DocumentData): ILeagueEntry {
  return {
    leagueId: data.leagueId,
    summonerId: data.summonerId,
    queueType: data.queueType,
    tier: data.tier,
    rank: data.rank,
    leaguePoints: data.leaguePoints,
    wins: data.wins,
    losses: data.losses,
    hotStreak: data.hotStreak,
    veteran: data.veteran,
    freshBlood: data.freshBlood,
    inactive: data.inactive,
    miniSeries: data.miniSeries,
  }
}
