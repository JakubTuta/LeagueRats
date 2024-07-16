import type { Auth } from 'firebase/auth'
import type { Firestore } from 'firebase/firestore'
import type { FirebaseStorage } from 'firebase/storage'

export function useFirebase() {
  const nuxtApp = useNuxtApp()

  const firestore = nuxtApp.$firestore as Firestore
  const auth = nuxtApp.$auth as Auth
  const storage = nuxtApp.$storage as FirebaseStorage

  return {
    firestore,
    auth,
    storage,
  }
}
