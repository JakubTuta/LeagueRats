import axios, { type AxiosError, type AxiosInstance, type AxiosResponse } from 'axios'

export interface ApiError {
  message: string
  status?: number
  data?: any
}

export const useApiStore = defineStore('api', () => {
  const config = useRuntimeConfig()
  const baseUrl = config.public.server_url

  let axiosInstance: AxiosInstance | null = null

  const getAxiosInstance = (): AxiosInstance => {
    if (axiosInstance) {
      return axiosInstance
    }

    axiosInstance = axios.create({
      baseURL: baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      responseType: 'json',
      timeout: 30000,
    })

    axiosInstance.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      },
    )

    axiosInstance.interceptors.response.use(
      (response) => {
        return response
      },
      (error: AxiosError) => {
        const apiError: ApiError = {
          message: error.message || 'An unknown error occurred',
          status: error.response?.status,
          data: error.response?.data,
        }

        if (error.response?.status === 404) {
          apiError.message = 'Resource not found'
        }
        else if (error.response?.status === 500) {
          apiError.message = 'Server error occurred'
        }
        else if (error.code === 'ECONNABORTED') {
          apiError.message = 'Request timeout'
        }

        return Promise.reject(apiError)
      },
    )

    return axiosInstance
  }

  const isResponseOk = (response: AxiosResponse | null): boolean => {
    return response !== null && (response.status === 200 || response.status === 201)
  }

  const sendRequest = async (
    { url, method, data }:
    { url: string, method: 'GET' | 'POST' | 'PUT' | 'DELETE', data?: any },
  ): Promise<AxiosResponse | null> => {
    try {
      const instance = getAxiosInstance()

      switch (method) {
        case 'GET':
          return await instance.get(url)
        case 'POST':
          return await instance.post(url, data)
        case 'PUT':
          return await instance.put(url, data)
        case 'DELETE':
          return await instance.delete(url)
      }
    }
    catch (error: any) {
      console.error('API Request Error:', error)

      return null
    }
  }

  return {
    isResponseOk,
    sendRequest,
    getAxiosInstance,
  }
})
