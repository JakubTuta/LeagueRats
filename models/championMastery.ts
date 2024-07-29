import { Timestamp } from 'firebase/firestore'

interface IRewardConfig {
  rewardValue: string
  rewardType: string
  maximumReward: number
}

interface INextSeasonMilestones {
  requireGradeCounts: object
  rewardMarks: number
  bonus: boolean
  rewardConfig: IRewardConfig
}

export interface IChampionMastery {
  puuid: string
  championId: number
  championLevel: number
  championPoints: number
  lastPlayTime: Timestamp
  championPointsSinceLastLevel: number
  championPointsUntilNextLevel: number
  chestGranted: boolean
  tokensEarned: number
  markRequiredForNextLevel: number
  championSeasonMilestone: number
  milestoneGrades: string[]
  nextSeasonMilestone: INextSeasonMilestones
}

export function mapChampionMastery(data: IChampionMastery): IChampionMastery {
  // @ts-expect-error data.lastPlayTime is a number
  data.lastPlayTime = new Timestamp(data.lastPlayTime / 1000, 0)

  return data
}
