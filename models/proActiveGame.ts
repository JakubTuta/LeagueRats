import type { IParticipant } from './activeGame'
import type { IProPlayer } from './proPlayer'
import type { TApiRegions1 } from '~/helpers/regions'

export interface IProActiveGame {
  player: IProPlayer
  participant: IParticipant
  region: TApiRegions1
}

export function mapProActiveGame(data: any): IProActiveGame | null {
  return {
    player: data.player,
    participant: data.participant,
    region: data.region,
  } as IProActiveGame
}
