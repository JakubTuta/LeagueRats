export function generateAccountKey(region: string, gameName: string, tagLine: string): string {
  return `${region.toUpperCase()}-${gameName}-${tagLine}`
}

export function parseAccountKey(accountKey: string): { region: string, gameName: string, tagLine: string } | null {
  const parts = accountKey.split('-')

  if (parts.length < 3) {
    return null
  }

  const region = parts[0]
  const tagLine = parts[parts.length - 1]
  const gameName = parts.slice(1, -1).join('-')

  return { region, gameName, tagLine }
}
