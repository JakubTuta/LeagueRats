// 400 - normal draft
// 420 - soloq
// 430 - normal blind
// 440 - flexq
// 450 - aram

export const queueTypes: { [key: string]: { id: number, name: string } } = {
  NORMAL: {
    id: 400,
    name: 'normal',
  },
  SOLOQ: {
    id: 420,
    name: 'ranked',
  },
  FLEXQ: {
    id: 440,
    name: 'ranked',
  },
  ARAM: {
    id: 450,
    name: 'normal',
  },
}

export const queueIdToType: { [key: number]: string } = {
  400: 'NORMAL',
  420: 'SOLOQ',
  430: 'NORMAL',
  440: 'FLEXQ',
  450: 'ARAM',
}
