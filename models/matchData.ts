interface IMatchMetadata {
  matchId: string
  participants: string[]
}

interface IMatchInfo {
  endOfGameResult: string
}

export interface IMatchData {
  metadata: IMatchMetadata
  info: IMatchInfo
}
