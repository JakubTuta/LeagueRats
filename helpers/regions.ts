export const selectRegions = ['EUW', 'EUNE', 'NA', 'KR', 'CN', 'BR', 'JP', 'LAN', 'LAS', 'OCE', 'PH', 'RU', 'SG', 'TH', 'TR', 'TW', 'VN']
export type TApiRegions1 = 'AMERICAS' | 'ASIA' | 'EUROPE' | 'ESPORTS'
export type TApiRegions2 = 'EUW1' | 'EUN1' | 'NA1' | 'KR' | 'CN' | 'BR1' | 'JP1' | 'LA1' | 'LA2' | 'ME1' | 'OC1' | 'PH2' | 'RU' | 'SG2' | 'TH2' | 'TR1' | 'TW2' | 'VN2'

export function mapSelectRegionToApiRegion1(region: string) {
  switch (region) {
    case 'EUW':
    case 'EUNE':
    case 'RU':
    case 'TR':
    case 'ME1':
      return 'EUROPE'
    case 'KR':
    case 'CN':
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
      return ''
  }
}

export function mapSelectRegionToApiRegion2(region: string) {
  switch (region) {
    case 'EUW':
      return 'EUW1'
    case 'EUNE':
      return 'EUN1'
    case 'NA':
      return 'NA1'
    case 'KR':
      return 'KR'
    case 'CN':
      return 'CN'
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
    default:
      return ''
  }
}
