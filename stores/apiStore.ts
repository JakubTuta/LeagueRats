import axios, { type AxiosResponse } from 'axios'

export const useApiStore = defineStore('api', () => {
  const baseUrl = 'http://localhost:8000'

  function getAxios() {
    return axios.create({
      baseURL: baseUrl,
    })
  }

  const isResponseOk = (response: AxiosResponse | null): boolean => {
    return response !== null && (response.status === 200 || response.status === 201)
  }

  const sendRequest = async (
    { url, method, data }:
    { url: string, method: string, data?: any },
  ): Promise<AxiosResponse | null> => {
    let response: AxiosResponse | null = null

    try {
      switch (method) {
        case 'GET':
          response = await getAxios().get(url)
          break
        case 'POST':
          response = await getAxios().post(url, data)
          break
        case 'PUT':
          response = await getAxios().put(url, data)
          break
        case 'DELETE':
          response = await getAxios().delete(url)
          break
      }
    }
    catch (error: any) {
      console.error(error)
    }

    return response
  }

  return {
    isResponseOk,
    sendRequest,
  }
})
