export interface IRuneData {
  id: number
  key: string
  icon: string
  name: string
  shortDesc: string
  longDesc: string
}

export interface IRuneTree {
  id: number
  key: string
  icon: string
  name: string
  slots: {
    runes: IRuneData[]
  }[]
}
