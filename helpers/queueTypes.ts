export const queueTypes: { [key: string]: { id: number, name: string } } = {
  NORMAL_DRAFT: {
    id: 400,
    name: 'normal',
  },
  SOLOQ: {
    id: 420,
    name: 'ranked',
  },
  NORMAL_BLIND: {
    id: 430,
    name: 'normal',
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
  400: 'NORMAL_DRAFT',
  420: 'SOLOQ',
  430: 'NORMAL_BLIND',
  440: 'FLEXQ',
  450: 'ARAM',
}
