<script setup lang="ts">
import { collection, doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';
import { proRegions, teamPerRegion } from '~/helpers/regions';
import { useFirebase } from '~/helpers/useFirebase';
import type { IAccount } from '~/models/account';

const { firestore } = useFirebase()

const restStore = useRestStore()

const correctPassword = 'password123'
const isCorrectPassword = ref(false)
const password = ref('')

const region = ref<string | null>(null)
const team = ref<string | null>(null)
const role = ref<string | null>(null)
const name = ref('')
const accountName = ref('')
const accountTag = ref('')
const accountRegion = ref<string | null>(null)

const roles = ['TOP', 'JNG', 'MID', 'ADC', 'SUP']

const accountRegions = ['NA', 'EUW', 'KR']

watch(password, (value) => {
  isCorrectPassword.value = value === correctPassword
})

async function add() {
  if (!region.value || !team.value || !role.value || !name.value)
    return

  const collectionRef = collection(firestore, `pro_players/${region.value}/${team.value}`)
  const docRef = doc(collectionRef, name.value.toLowerCase())

  const docData = await getDoc(docRef)

  let account: IAccount | null = null
  if (accountRegion.value && accountName.value && accountTag.value)
    account = await restStore.saveAccount(accountRegion.value, accountName.value, accountTag.value)

  if (docData.exists() && account) {
    const newPuuids = [...docData.data().puuid]
    if (!newPuuids.includes(account.puuid))
      newPuuids.push(account.puuid)

    updateDoc(docRef, { puuid: newPuuids })
  }
  else if (!docData.exists()) {
    const puuid = account
      ? [account.puuid]
      : []

    setDoc(docRef, {
      player: name.value,
      region: region.value,
      role: role.value,
      team: team.value,
      puuid,
    }).catch(error => console.error(error))
  }

  // region.value = null
  // team.value = null
  // accountRegion.value = null
  role.value = null
  name.value = ''
  accountName.value = ''
  accountTag.value = ''
}
</script>

<!-- eslint-disable vue/no-bare-strings-in-template -->
<template>
  <v-container>
    <v-card
      v-if="!isCorrectPassword"
    >
      <v-card-text>
        <v-text-field
          v-model="password"
          variant="outlined"
          label="Password"
        />
      </v-card-text>
    </v-card>

    <v-card
      v-else
    >
      <v-card-text>
        <v-select
          v-model="region"
          variant="outlined"
          :items="proRegions"
          label="region"
        />

        <v-autocomplete
          v-model="team"
          variant="outlined"
          :items="region
            ? teamPerRegion[region]
            : []"
          label="team"
        />

        <v-select
          v-model="role"
          variant="outlined"
          :items="roles"
          label="role"
        />

        <v-text-field
          v-model="name"
          variant="outlined"
          label="name"
        />

        <v-select
          v-model="accountRegion"
          variant="outlined"
          :items="accountRegions"
          label="account region"
        />

        <v-text-field
          v-model="accountName"
          variant="outlined"
          label="account name"
        />

        <v-text-field
          v-model="accountTag"
          variant="outlined"
          label="account tag"
        />

        <v-btn
          variant="outlined"
          @click="add"
        >
          Add
        </v-btn>

        <v-btn>
          Function
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>
