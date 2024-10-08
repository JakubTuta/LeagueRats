import type { Timestamp } from 'firebase/firestore'
import type { IParticipant } from './activeGame'
import type { IProPlayer } from './proPlayer'
import type { TApiRegions1 } from '~/helpers/regions'

export interface IProActiveGame {
  player: IProPlayer
  participant: IParticipant
  region: TApiRegions1
  gameStartTime: Timestamp
}

export function mapProActiveGame(data: any): IProActiveGame | null {
  return {
    player: data.player,
    participant: data.participant,
    region: data.region,
    gameStartTime: data.gameStartTime,
  } as IProActiveGame
}
