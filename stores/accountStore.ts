import { type IAccount, mapAccount } from '~/models/account'

export const useAccountStore = defineStore('account', () => {
  const apiStore = useApiStore()

  const getAccount = async (
    { puuid, username, tag, region }:
    { puuid?: string, username?: string, tag?: string, region?: string },
  ): Promise<IAccount | null> => {
    const baseUrl = '/v2/account/'
    const method = 'GET'

    const queryParams = new URLSearchParams()

    if (puuid)
      queryParams.append('puuid', puuid)
    if (username)
      queryParams.append('username', username)
    if (tag)
      queryParams.append('tag', tag)
    if (region)
      queryParams.append('region', region)

    const fullUrl = `${baseUrl}?${queryParams.toString()}`

    const response = await apiStore.sendRequest({ url: fullUrl, method })

    if (apiStore.isResponseOk(response))
      return mapAccount(response!.data)

    return null
  }

  const getAccountsInAllRegions = async (username: string, tag: string): Promise<Record<string, IAccount | null>> => {
    const url = `/v2/account/all-regions/${username}/${tag}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response))
      return response!.data as Record<string, IAccount | null>

    return {}
  }

  return {
    getAccount,
    getAccountsInAllRegions,
  }
})
