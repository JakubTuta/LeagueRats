import type { ILeagueEntry } from '~/models/leagueEntry'

const mappedRanks: { [key: string]: number } = {
  BRONZE: 1,
  SILVER: 2,
  GOLD: 3,
  PLATINUM: 4,
  EMERALD: 5,
  DIAMOND: 6,
  MASTER: 7,
  GRANDMASTER: 8,
  CHALLENGER: 9,
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
