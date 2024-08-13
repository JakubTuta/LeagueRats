import { Timestamp } from 'firebase/firestore'
import type { IPerks } from './activeGame'

interface IMatchMetadata {
  matchId: string
  participants: string[]
}

interface ITeam {
  bans: {
    championId: number
    pickTurn: number
  }[]
  objectives: {
    baron: {
      first: boolean
      kills: number
    }
    champion: {
      first: boolean
      kills: number
    }
    dragon: {
      first: boolean
      kills: number
    }
    horde: {
      first: boolean
      kills: number
    }
    inhibitor: {
      first: boolean
      kills: number
    }
    riftHerald: {
      first: boolean
      kills: number
    }
    tower: {
      first: boolean
      kills: number
    }
  }
  teamId: number
  win: boolean
}

interface IParticipantStats {
  kills: number
  assists: number
  deaths: number
  champLevel: number
  championId: number
  championName: string
  goldEarned: number
  damageDealtToBuildings: number
  item0: number
  item1: number
  item2: number
  item3: number
  item4: number
  item5: number
  item6: number
  physicalDamageDealtToChampions: number
  physicalDamageTaken: number
  magicDamageDealtToChampions: number
  magicDamageTaken: number
  trueDamageDealtToChampions: number
  trueDamageTaken: number
  neutralMinionsKilled: number
  totalMinionsKilled: number
  participantId: number
  perks: IPerks
  puuid: string
  riotIdGameName: string
  riotIdTagLine: string
  summoner1Id: number
  summoner2Id: number
  summonerId: string
  summonerName: string
  teamId: number
  teamPosition: 'TOP' | 'JUNGLE' | 'MIDDLE' | 'BOTTOM' | 'UTILITY'
  totalHealsOnTeammates: number
  visionScore: number
  win: boolean
}

interface IMatchInfo {
  endOfGameResult: string
  gameDuration: number // in seconds
  gameId: number
  gameMode: string
  gameName: string
  gameStartTimestamp: Timestamp
  gameType: string
  gameVersion: string
  mapId: number
  participants: IParticipantStats[]
  platformId: string
  queueId: number
  teams: ITeam[]
}

export interface IMatchData {
  metadata: IMatchMetadata
  info: IMatchInfo
}

export function mapMatchData(data: any): IMatchData {
  return {
    metadata: {
      matchId: data.metadata.matchId,
      participants: data.metadata.participants,
    },
    info: {
      endOfGameResult: data.info.endOfGameResult,
      gameDuration: data.info.gameDuration,
      gameId: data.info.gameId,
      gameMode: data.info.gameMode,
      gameName: data.info.gameName,
      gameStartTimestamp: new Timestamp(data.info.gameStartTimestamp / 1000, 0),
      gameType: data.info.gameType,
      gameVersion: data.info.gameVersion,
      mapId: data.info.mapId,
      participants: data.info.participants.map((participant: any) => ({
        kills: participant.kills,
        assists: participant.assists,
        deaths: participant.deaths,
        champLevel: participant.champLevel,
        championId: participant.championId,
        championName: participant.championName,
        goldEarned: participant.goldEarned,
        damageDealtToBuildings: participant.damageDealtToBuildings,
        item0: participant.item0,
        item1: participant.item1,
        item2: participant.item2,
        item3: participant.item3,
        item4: participant.item4,
        item5: participant.item5,
        item6: participant.item6,
        physicalDamageDealtToChampions: participant.physicalDamageDealtToChampions,
        physicalDamageTaken: participant.physicalDamageTaken,
        magicDamageDealtToChampions: participant.magicDamageDealtToChampions,
        magicDamageTaken: participant.magicDamageTaken,
        trueDamageDealtToChampions: participant.trueDamageDealtToChampions,
        trueDamageTaken: participant.trueDamageTaken,
        neutralMinionsKilled: participant.neutralMinionsKilled,
      })),
      platformId: data.info.platformId,
      queueId: data.info.queueId,
      teams: data.info.teams.map((team: any) => ({
        bans: team.bans.map((ban: any) => ({
          championId: ban.championId,
          pickTurn: ban.pickTurn,
        })),
        objectives: {
          baron: {
            first: team.objectives.baron.first,
            kills: team.objectives.baron.kills,
          },
          champion: {
            first: team.objectives.champion.first,
            kills: team.objectives.champion.kills,
          },
          dragon: {
            first: team.objectives.dragon.first,
            kills: team.objectives.dragon.kills,
          },
          horde: {
            first: team.objectives.horde.first,
            kills: team.objectives.horde.kills,
          },
          inhibitor: {
            first: team.objectives.inhibitor.first,
            kills: team.objectives.inhibitor.kills,
          },
          riftHerald: {
            first: team.objectives.riftHerald.first,
            kills: team.objectives.riftHerald.kills,
          },
          tower: {
            first: team.objectives.tower.first,
            kills: team.objectives.tower.kills,
          },
        },
        teamId: team.teamId,
        win: team.win,
      })),
    },
  }
}
