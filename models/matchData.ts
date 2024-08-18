import { Timestamp } from 'firebase/firestore'
import type { TApiRegions2 } from '~/helpers/regions'

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

export interface IMatchHistoryPerks {
  statPerks: {
    defense: number
    flex: number
    offense: number
  }
  styles: {
    description: string
    selections: {
      perk: number
      var1: number
      var2: number
      var3: number
    }[]
    style: number
  }[]
}

export interface IParticipantStats {
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
  perks: IMatchHistoryPerks
  puuid: string
  riotIdGameName: string
  riotIdTagline: string
  summoner1Id: number
  summoner2Id: number
  summonerId: string
  summonerName: string
  teamId: number
  teamPosition: 'TOP' | 'JUNGLE' | 'MIDDLE' | 'BOTTOM' | 'UTILITY'
  totalHealsOnTeammates: number
  visionScore: number
  win: boolean
  gameEndedInEarlySurrender: boolean
}

interface IMatchInfo {
  gameDuration: number // in seconds
  gameId: number
  gameMode: string
  gameName: string
  gameStartTimestamp: Timestamp
  gameType: string
  gameVersion: string
  mapId: number
  participants: IParticipantStats[]
  platformId: TApiRegions2
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
      matchId: data.metadata?.matchId || '',
      participants: data.metadata?.participants || [],
    },
    info: {
      gameDuration: data.info?.gameDuration || 0,
      gameId: data.info?.gameId || 0,
      gameMode: data.info?.gameMode || '',
      gameName: data.info?.gameName || '',
      gameStartTimestamp: new Timestamp(data.info?.gameStartTimestamp / 1000 || 0, 0),
      gameType: data.info?.gameType || '',
      gameVersion: data.info?.gameVersion || '',
      mapId: data.info?.mapId || 0,
      participants: data.info?.participants?.map((participant: any) => ({
        kills: participant?.kills || 0,
        assists: participant?.assists || 0,
        deaths: participant?.deaths || 0,
        champLevel: participant?.champLevel || 0,
        championId: participant?.championId || 0,
        championName: participant?.championName || '',
        goldEarned: participant?.goldEarned || 0,
        damageDealtToBuildings: participant?.damageDealtToBuildings || 0,
        item0: participant?.item0 || 0,
        item1: participant?.item1 || 0,
        item2: participant?.item2 || 0,
        item3: participant?.item3 || 0,
        item4: participant?.item4 || 0,
        item5: participant?.item5 || 0,
        item6: participant?.item6 || 0,
        physicalDamageDealtToChampions: participant?.physicalDamageDealtToChampions || 0,
        physicalDamageTaken: participant?.physicalDamageTaken || 0,
        magicDamageDealtToChampions: participant?.magicDamageDealtToChampions || 0,
        magicDamageTaken: participant?.magicDamageTaken || 0,
        trueDamageDealtToChampions: participant?.trueDamageDealtToChampions || 0,
        trueDamageTaken: participant?.trueDamageTaken || 0,
        neutralMinionsKilled: participant?.neutralMinionsKilled || 0,
        totalMinionsKilled: participant?.totalMinionsKilled || 0,
        participantId: participant?.participantId || 0,
        perks: participant?.perks || {},
        puuid: participant?.puuid || '',
        riotIdGameName: participant?.riotIdGameName || '',
        riotIdTagline: participant?.riotIdTagline || '',
        summoner1Id: participant?.summoner1Id || 0,
        summoner2Id: participant?.summoner2Id || 0,
        summonerId: participant?.summonerId || '',
        summonerName: participant?.summonerName || '',
        teamId: participant?.teamId || 0,
        teamPosition: participant?.teamPosition || '',
        totalHealsOnTeammates: participant?.totalHealsOnTeammates || 0,
        visionScore: participant?.visionScore || 0,
        win: participant?.win || false,
        gameEndedInEarlySurrender: participant?.gameEndedInEarlySurrender || false,
      })) || [],
      platformId: data.info?.platformId || '',
      queueId: data.info?.queueId || 0,
      teams: data.info?.teams?.map((team: any) => ({
        bans: team?.bans?.map((ban: any) => ({
          championId: ban?.championId || 0,
          pickTurn: ban?.pickTurn || 0,
        })) || [],
        objectives: {
          baron: {
            first: team?.objectives?.baron?.first || false,
            kills: team?.objectives?.baron?.kills || 0,
          },
          champion: {
            first: team?.objectives?.champion?.first || false,
            kills: team?.objectives?.champion?.kills || 0,
          },
          dragon: {
            first: team?.objectives?.dragon?.first || false,
            kills: team?.objectives?.dragon?.kills || 0,
          },
          horde: {
            first: team?.objectives?.horde?.first || false,
            kills: team?.objectives?.horde?.kills || 0,
          },
          inhibitor: {
            first: team?.objectives?.inhibitor?.first || false,
            kills: team?.objectives?.inhibitor?.kills || 0,
          },
          riftHerald: {
            first: team?.objectives?.riftHerald?.first || false,
            kills: team?.objectives?.riftHerald?.kills || 0,
          },
          tower: {
            first: team?.objectives?.tower?.first || false,
            kills: team?.objectives?.tower?.kills || 0,
          },
        },
        teamId: team?.teamId || 0,
        win: team?.win || false,
      })) || [],
    },
  }
}
