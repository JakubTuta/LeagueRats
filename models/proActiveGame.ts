import type { IActiveGame } from './activeGame'
import type { IProPlayer } from './proPlayer'

export interface IProActiveGame {
  player: IProPlayer
  game: IActiveGame
}

export function mapProActiveGame(data: { player: IProPlayer, game: IActiveGame }): IProActiveGame | null {
  return {
    player: data.player,
    game: data.game,
  } as IProActiveGame
}
