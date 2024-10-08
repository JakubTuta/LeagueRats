import type { Timestamp } from 'firebase/firestore'
import type { IAccount } from './account'
import type { IParticipant } from './activeGame'
import type { IProPlayer } from './proPlayer'

export interface IProActiveGame {
  account: IAccount
  player: IProPlayer
  participant: IParticipant
  gameStartTime: Timestamp
}

export function mapProActiveGame(data: any): IProActiveGame | null {
  return {
    account: data.account,
    player: data.player,
    participant: data.participant,
    gameStartTime: data.gameStartTime,
  } as IProActiveGame
}
