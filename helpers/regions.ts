export const selectRegions = ['EUW', 'EUNE', 'NA', 'KR', 'BR', 'JP', 'LAN', 'LAS', 'OCE', 'PH', 'RU', 'SG', 'TH', 'TR', 'TW', 'VN', 'ME']
export const importantSelectRegions = ['EUW', 'NA', 'KR']
export type TSelectRegions = 'EUW' | 'EUNE' | 'NA' | 'KR' | 'BR' | 'JP' | 'LAN' | 'LAS' | 'OCE' | 'PH' | 'RU' | 'SG' | 'TH' | 'TR' | 'TW' | 'VN' | 'ME'
export type TApiRegions1 = 'AMERICAS' | 'ASIA' | 'EUROPE' | 'ESPORTS'
export type TApiRegions2 = 'EUW1' | 'EUN1' | 'NA1' | 'KR' | 'BR1' | 'JP1' | 'LA1' | 'LA2' | 'ME1' | 'OC1' | 'PH2' | 'RU' | 'SG2' | 'TH2' | 'TR1' | 'TW2' | 'VN2' | 'ME1'

export function mapSelectRegionToApiRegion1(region: TSelectRegions): TApiRegions1 {
  switch (region) {
    case 'EUW':
    case 'EUNE':
    case 'RU':
    case 'TR':
    case 'ME':
      return 'EUROPE'
    case 'KR':
    case 'JP':
    case 'OCE':
    case 'PH':
    case 'SG':
    case 'TH':
    case 'TW':
    case 'VN':
      return 'ASIA'
    case 'NA':
    case 'LAN':
    case 'LAS':
    case 'BR':
      return 'AMERICAS'
    default:
      throw new Error(`Invalid region: ${region}`)
  }
}

export function mapSelectRegionToApiRegion2(region: string): TApiRegions2 {
  switch (region) {
    case 'EUW':
      return 'EUW1'
    case 'EUNE':
      return 'EUN1'
    case 'NA':
      return 'NA1'
    case 'KR':
      return 'KR'
    case 'BR':
      return 'BR1'
    case 'JP':
      return 'JP1'
    case 'LAN':
      return 'LA1'
    case 'LAS':
      return 'LA2'
    case 'OCE':
      return 'OC1'
    case 'PH':
      return 'PH2'
    case 'RU':
      return 'RU'
    case 'SG':
      return 'SG2'
    case 'TH':
      return 'TH2'
    case 'TR':
      return 'TR1'
    case 'TW':
      return 'TW2'
    case 'VN':
      return 'VN2'
    case 'ME':
      return 'ME1'
    default:
      throw new Error(`Invalid region: ${region}`)
  }
}

export function mapApiRegion2ToSelect(region: TApiRegions2): TSelectRegions {
  switch (region) {
    case 'EUW1':
      return 'EUW'
    case 'EUN1':
      return 'EUNE'
    case 'NA1':
      return 'NA'
    case 'KR':
      return 'KR'
    case 'BR1':
      return 'BR'
    case 'JP1':
      return 'JP'
    case 'LA1':
      return 'LAN'
    case 'LA2':
      return 'LAS'
    case 'OC1':
      return 'OCE'
    case 'PH2':
      return 'PH'
    case 'RU':
      return 'RU'
    case 'SG2':
      return 'SG'
    case 'TH2':
      return 'TH'
    case 'TR1':
      return 'TR'
    case 'TW2':
      return 'TW'
    case 'VN2':
      return 'VN'
    case 'ME1':
      return 'ME'
    default:
      throw new Error(`Invalid region: ${region}`)
  }
}

export const proRegions = ['LCK', 'LPL', 'LCS', 'LEC']

export const proRegionToSelectRegion: { [key: string]: string } = {
  LCK: 'KR',
  LCS: 'NA',
  LEC: 'EUW',
  LPL: 'CN',
}

export const selectRegionToProRegion: { [key: string]: string } = {
  KR: 'LCK',
  NA: 'LCS',
  EUW: 'LEC',
  CN: 'LPL',
}

export const teamPerRegion: { [key: string]: string[] } = {
  LCK: ['T1', 'GENG', 'DK', 'DRX', 'HLE', 'DNF', 'KT', 'FOX', 'BRO', 'NS'],
  LPL: ['AL', 'BLG', 'EDG', 'FPX', 'IG', 'JDG', 'LGD', 'LNG', 'NIP', 'OMG', 'RA', 'RNG', 'WE', 'TES', 'TT', 'UP', 'WBG'],
  LCS: ['TL', 'C9', 'FLY', 'DIG', '100', 'SR', 'DSG', 'LYN'],
  LEC: ['FNC', 'G2', 'GX', 'KC', 'MKOI', 'RGE', 'SK', 'BDS', 'TH', 'VIT'],
}

export const teamFullName: { [key: string]: string } = {
  T1: 'T1',
  GENG: 'Gen.G',
  DK: 'Dplus KIA',
  DRX: 'DRX',
  HLE: 'Hanwha Life Esports',
  DNF: 'DN Freecs',
  KT: 'kt Rolster',
  FOX: 'BNK FearX',
  BRO: 'OKSavingsBank BRION',
  NS: 'NongShim REDFORCE',
  AL: 'Anyone\'s Legend',
  BLG: 'Bilibili Gaming',
  EDG: 'Edward Gaming',
  FPX: 'FunPlus Phoenix',
  IG: 'Invictus Gaming',
  JDG: 'JD Gaming',
  LGD: 'LGD Gaming',
  LNG: 'LNG Esports',
  NIP: 'Ninjas in Pyjamas',
  OMG: 'Oh My God',
  RA: 'Rare Atom',
  RNG: 'Royal Never Give Up',
  WE: 'Team WE',
  TES: 'Top Esports',
  TT: 'TT Gaming',
  UP: 'Ultra Prime',
  WBG: 'Weibo Gaming',
  TL: 'Team Liquid',
  C9: 'Cloud9',
  FLY: 'FlyQuest',
  DIG: 'Dignitas',
  100: '100 Thieves',
  SR: 'Evil Geniuses',
  DSG: 'Disguised',
  LYN: 'Lyon Gaming',
  FNC: 'Fnatic',
  G2: 'G2 Esports',
  GX: 'Excel Esports',
  KC: 'Karmine Corp',
  MKOI: 'Movistar KOI',
  RGE: 'Rogue',
  SK: 'SK Gaming',
  BDS: 'Team BDS',
  TH: 'Team Heretics',
  VIT: 'Team Vitality',
}

export function mapTeamToFullName(teams: string[]): string[] {
  return teams.map(team => teamFullName[team])
}
