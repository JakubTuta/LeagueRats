export interface IChampionMastery {
  championId: number
  championLevel: number
  championPoints: number
}

export function mapChampionMastery(data: IChampionMastery): IChampionMastery {
  return {
    championId: data.championId,
    championLevel: data.championLevel,
    championPoints: data.championPoints,
  }
}
