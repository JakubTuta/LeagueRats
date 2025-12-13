import { generateAccountKey } from '~/helpers/accountKey'
import { type IAccount, mapAccount } from '~/models/account'

interface AccountState {
  data: IAccount | null
  loading: boolean
  error: string | null
  lastFetched: number | null
}

export const useAccountStore = defineStore('account', () => {
  const apiStore = useApiStore()

  const accounts = ref<Record<string, AccountState>>({})
  const fetchingAccounts = ref<Set<string>>(new Set())

  const getAccountState = (accountKey: string): AccountState => {
    if (!accounts.value[accountKey]) {
      accounts.value[accountKey] = {
        data: null,
        loading: false,
        error: null,
        lastFetched: null,
      }
    }

    return accounts.value[accountKey]
  }

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

  const fetchAccount = async (region: string, gameName: string, tagLine: string): Promise<IAccount | null> => {
    const accountKey = generateAccountKey(region, gameName, tagLine)
    const state = getAccountState(accountKey)

    if (fetchingAccounts.value.has(accountKey)) {
      return state.data
    }

    if (state.data && state.lastFetched && Date.now() - state.lastFetched < 60000) {
      return state.data
    }

    fetchingAccounts.value.add(accountKey)
    state.loading = true
    state.error = null

    try {
      const account = await getAccount({ username: gameName, tag: tagLine, region })

      if (account) {
        state.data = account
        state.lastFetched = Date.now()
      }
      else {
        state.error = 'Account not found'
      }

      return account
    }
    catch (error: any) {
      state.error = error.message || 'Failed to fetch account'

      return null
    }
    finally {
      state.loading = false
      fetchingAccounts.value.delete(accountKey)
    }
  }

  const getAccountData = (region: string, gameName: string, tagLine: string): IAccount | null => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return accounts.value[accountKey]?.data || null
  }

  const isAccountLoading = (region: string, gameName: string, tagLine: string): boolean => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return accounts.value[accountKey]?.loading || false
  }

  const getAccountError = (region: string, gameName: string, tagLine: string): string | null => {
    const accountKey = generateAccountKey(region, gameName, tagLine)

    return accounts.value[accountKey]?.error || null
  }

  const getAccountsInAllRegions = async (username: string, tag: string): Promise<Record<string, IAccount | null>> => {
    const url = `/v2/account/all-regions/${username}/${tag}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response))
      return response!.data as Record<string, IAccount | null>

    return {}
  }

  return {
    accounts,
    getAccount,
    fetchAccount,
    getAccountData,
    isAccountLoading,
    getAccountError,
    getAccountsInAllRegions,
  }
})
