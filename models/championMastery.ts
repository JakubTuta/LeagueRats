import { Timestamp } from 'firebase/firestore'

export interface IChampionMastery {
  chestGranted: boolean
  championId: number
  championLevel: number
  championPoints: number
  lastPlayTime: Timestamp
}

export function mapChampionMastery(data: IChampionMastery): IChampionMastery {
  // @ts-expect-error data.lastPlayTime is a number
  data.lastPlayTime = new Timestamp(data.lastPlayTime / 1000, 0)

  return data
}
