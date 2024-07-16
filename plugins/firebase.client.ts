import { initializeApp } from 'firebase/app'
import { browserLocalPersistence, browserPopupRedirectResolver, indexedDBLocalPersistence, initializeAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  const firebaseConfig = {
    apiKey: config.public.apiKey,
    authDomain: config.public.authDomain,
    projectId: config.public.projectId,
    storageBucket: config.public.storageBucket,
    messagingSenderId: config.public.messagingSenderId,
    appId: config.public.appId,
  }

  const app = initializeApp(firebaseConfig, 'primary')
  const firestore = getFirestore(app)
  const storage = getStorage(app)

  const auth = initializeAuth(app, {
    persistence: [indexedDBLocalPersistence, browserLocalPersistence],
    popupRedirectResolver: browserPopupRedirectResolver,
  })

  nuxtApp.provide(
    'auth',
    auth,
  )

  nuxtApp.provide(
    'firestore',
    firestore,
  )

  nuxtApp.provide(
    'storage',
    storage,
  )
})
