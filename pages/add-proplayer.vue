<script setup lang="ts">
import { collection, deleteDoc, doc, getDocs, setDoc } from 'firebase/firestore';
import { proRegions, teamPerRegion } from '~/helpers/regions';
import { useFirebase } from '~/helpers/useFirebase';

const { firestore } = useFirebase()

const correctPassword = 'password123'
const isCorrectPassword = ref(false)
const password = ref('')

const region = ref<string | null>(null)
const team = ref<string | null>(null)
const role = ref<string | null>(null)
const name = ref('')
const accountName = ref('')
const accountTag = ref('')

const roles = ['TOP', 'JNG', 'MID', 'ADC', 'SUP']

const mappedRegions: { [key: string]: string } = {
  EUW: 'LEC',
  NA: 'LCS',
  KR: 'LCK',
  CN: 'LPL',
}

function add() {
  if (!region.value || !team.value || !role.value || !name.value)
    return

  const collectionRef = collection(firestore, `pro_players/${region.value}/${team.value}`)
  const docRef = doc(collectionRef, name.value.toLowerCase())

  setDoc(docRef, {
    player: name.value,
    gameName: accountName.value,
    tagLine: accountTag.value,
    region: mapRegion(),
    role: role.value,
    team: team.value,
  }).catch(error => console.error(error))

  // region.value = null
  // team.value = null
  role.value = null
  name.value = ''
  accountName.value = ''
  accountTag.value = ''
}

watch(password, (value) => {
  isCorrectPassword.value = value === correctPassword
})

// function addTeams() {
//   proRegions.forEach((region) => {
//     teamPerRegion[region].forEach(async (team) => {
//       const collectionRef = collection(firestore, `pro_players/${region}/${team}`)
//       const querySnapshot = await getDocs(collectionRef)

//       querySnapshot.forEach((document) => {
//         updateDoc(document.ref, { team })
//       })
//     })
//   })
// }

// function changeNames() {
//   regions.forEach((region) => {
//     teamPerRegion[region].forEach(async (team) => {
//       const collectionRef = collection(firestore, `pro_players/${region}/${team}`)
//       const querySnapshot = await getDocs(collectionRef)

//       querySnapshot.forEach((document) => {
//         const docRef = doc(collectionRef, document.id)
//         const docData = mapIProPlayer(document.data())

//         deleteDoc(docRef)
//         setDoc(doc(collectionRef, docRef.id.toLowerCase()), docData)
//       })
//     })
//   })
// }

// function puuidToArray() {
//   proRegions.forEach((region) => {
//     teamPerRegion[region].forEach(async (team) => {
//       const collectionRef = collection(firestore, `pro_players/${region}/${team}`)
//       const querySnapshot = await getDocs(collectionRef)

//       querySnapshot.forEach((document) => {
//         const docRef = doc(collectionRef, document.id)

//         deleteDoc(docRef)

//         const docData = document.data()
//         const newDocData = {
//           player: docData.player,
//           region: docData.region,
//           role: docData.role,
//           team: docData.team,
//           puuid: [docData.puuid],
//         }
//         setDoc(doc(collectionRef, docRef.id), newDocData)
//       })
//     })
//   })
// }

function mapRegion() {
  proRegions.forEach((region) => {
    teamPerRegion[region].forEach(async (team) => {
      const collectionRef = collection(firestore, `pro_players/${region}/${team}`)
      const querySnapshot = await getDocs(collectionRef)

      querySnapshot.forEach((document) => {
        const docRef = doc(collectionRef, document.id)

        deleteDoc(docRef)

        const docData = document.data()
        docData.region = mappedRegions[docData.region]
        setDoc(doc(collectionRef, docRef.id), docData)
      })
    })
  })
}
</script>

<!-- eslint-disable vue/no-bare-strings-in-template -->
<template>
  <v-card
    v-if="!isCorrectPassword"
    class="ma-2"
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
    class="ma-2"
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

      <v-btn @click="mapRegion">
        Function
      </v-btn>
    </v-card-text>
  </v-card>
</template>
