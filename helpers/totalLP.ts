import type { ILeagueEntry } from '~/models/leagueEntry'

const mappedRanks: { [key: string]: number } = {
  BRONZE: 1,
  SILVER: 2,
  GOLD: 3,
  PLATINUM: 4,
  DIAMOND: 5,
  MASTER: 6,
  GRANDMASTER: 7,
  CHALLENGER: 8,
}

const romanToNumber: { [key: string]: number } = {
  I: 1,
  II: 2,
  III: 3,
  IV: 4,
}

function reverseRank(rank: number) {
  return 5 - rank
}

export function calculateTotalLP(leagueEntry: ILeagueEntry | null): number {
  if (!leagueEntry)
    return 0

  const { tier, rank, leaguePoints } = leagueEntry

  return (mappedRanks[tier] - 1) * 1000 + reverseRank(romanToNumber[rank]) * 100 + leaguePoints
}
