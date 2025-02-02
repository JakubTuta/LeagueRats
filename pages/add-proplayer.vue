<script setup lang="ts">
import { proRegions, teamPerRegion } from '~/helpers/regions'
import type { IProPlayer } from '~/models/proPlayer'

const proPlayerStore = useProPlayerStore()
const { proAccountNames } = storeToRefs(proPlayerStore)

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
const selectedTab = ref('add')
const transferPlayer = ref<string | null>(null)
const fromTeam = ref<string | null>(null)
const toTeam = ref<string | null>(null)

const tabs = [
  {
    title: 'Add',
    value: 'add',
  },
  {
    title: 'Transfer',
    value: 'transfer',
  },
]

const roles = ['TOP', 'JNG', 'MID', 'ADC', 'SUP']

const accountRegions = ['NA', 'EUW', 'KR']

const allTeams = computed(() => Object.values(teamPerRegion).flat())
const allPlayers = computed(() => {
  if (!proAccountNames.value) {
    return []
  }

  return Array.from(new Set(Object.values(proAccountNames.value).map(e => `[${e.team}] ${e.player}`)).values())
})

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

async function transfer() {
  if (!transferPlayer.value || !fromTeam.value || !toTeam.value)
    return

  const playerName = transferPlayer.value.split('] ')[1]

  await proPlayerStore.transferProPlayer(playerName, fromTeam.value, toTeam.value)

  transferPlayer.value = null
  fromTeam.value = null
  toTeam.value = null
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
          label="Password"
        />
      </v-card-text>
    </v-card>

    <v-card v-if="isCorrectPassword">
      <v-tabs
        v-model="selectedTab"
        color="primary"
        grow
      >
        <v-tab
          v-for="tab in tabs"
          :key="tab.value"
          :value="tab.value"
        >
          {{ tab.title }}
        </v-tab>
      </v-tabs>
    </v-card>

    <v-card
      v-if="isCorrectPassword && selectedTab === 'add'"
    >
      <v-card-text>
        <v-select
          v-model="region"
          :items="proRegions"
          label="region"
        />

        <v-autocomplete
          v-model="team"
          :items="region
            ? teamPerRegion[region]
            : []"
          label="team"
        />

        <v-select
          v-model="role"
          :items="roles"
          label="role"
        />

        <v-text-field
          v-model="name"
          label="name"
        />

        <v-select
          v-model="accountRegion"
          :items="accountRegions"
          label="account region"
        />

        <v-text-field
          v-model="accountName"
          label="account name"
        />

        <v-text-field
          v-model="accountTag"
          label="account tag"
        />

        <v-btn
          @click="add"
        >
          Add
        </v-btn>

        <v-btn>
          Function
        </v-btn>
      </v-card-text>
    </v-card>

    <v-card v-if="isCorrectPassword && selectedTab === 'transfer'">
      <v-card-text>
        <v-row align="center">
          <v-col
            cols="12"
            sm="4"
          >
            <v-combobox
              v-model="transferPlayer"
              :items="allPlayers"
              label="Player name"
              variant="outlined"
            />
          </v-col>

          <v-col
            cols="12"
            sm="4"
          >
            <v-autocomplete
              v-model="fromTeam"
              :items="allTeams"
              label="From team"
            />
          </v-col>

          <v-col
            cols="12"
            sm="4"
          >
            <v-autocomplete
              v-model="toTeam"
              :items="allTeams"
              label="To team"
            />
          </v-col>
        </v-row>

        <v-btn
          @click="transfer"
        >
          Transfer
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>
