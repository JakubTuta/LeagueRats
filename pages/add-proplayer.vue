<script setup lang="ts">
import { proRegions, teamPerRegion } from '~/helpers/regions'
import type { IProPlayer } from '~/models/proPlayer'

const proPlayerStore = useProPlayerStore()

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

  const playerData: IProPlayer = {
    player: name.value,
    puuid: [],
    // @ts-expect-error xdd
    region: region.value,
    // @ts-expect-error xdd
    role: role.value,
    team: team.value,
  }

  const accountData = {
    username: accountName.value || '',
    tag: accountTag.value || '',
    region: accountRegion.value || '',
  }

  await proPlayerStore.createProPlayer(playerData, accountData)

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
