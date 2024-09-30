import type { IAccount } from './account'
import type { ILeagueEntry } from './leagueEntry'

export interface IBootcampAccount extends IAccount, ILeagueEntry {
  player: string
  team: string
  role: 'TOP' | 'JNG' | 'MID' | 'ADC' | 'SUP'
}
