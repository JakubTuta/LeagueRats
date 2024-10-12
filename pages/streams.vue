<script setup lang="ts">
import 'twitch-stream-embed'
import { useDisplay } from 'vuetify'
import { fullUrl } from '~/helpers/url'
import type { IStream } from '~/stores/proplayerStore'

const proStore = useProPlayerStore()
const { liveStreams, notLiveStreams } = storeToRefs(proStore)

const storageStore = useStorageStore()
const { teamImages } = storeToRefs(storageStore)

const { smAndDown, height } = useDisplay()

const currentStream = ref<IStream | null>(null)
const search = ref('')
const renderComponent = ref(true)

onMounted(() => {
  proStore.getLiveStreams()
  proStore.getNotLiveStreams()
})

const allStreams = computed(() => Object.values(liveStreams.value).concat(Object.values(notLiveStreams.value)))
const searchStreams = computed(() => {
  if (!search.value)
    return allStreams.value

  const lowerCaseSearch = search.value.toLowerCase()

  return allStreams.value.filter(stream => stream.player.toLowerCase().includes(lowerCaseSearch)
    || stream.team.toLowerCase().includes(lowerCaseSearch)
    || stream.twitch.toLowerCase().includes(lowerCaseSearch),
  )
})

watch(liveStreams, (newLiveStreams) => {
  if (Object.values(newLiveStreams).length > 0) {
    currentStream.value = Object.values(newLiveStreams)[0]
  }
}, { immediate: true })

watch(allStreams, (newStreams) => {
  const uniqueTeamsPerRegion = newStreams.reduce((acc, stream) => {
    if (!acc[stream.region]) {
      acc[stream.region] = new Set()
    }
    acc[stream.region].add(stream.team)

    return acc
  }, {} as { [key: string]: Set<string> })

  Object.entries(uniqueTeamsPerRegion).forEach(([region, teams]) => {
    teams.forEach((team) => {
      storageStore.getTeamImages(region, team)
    })
  })
})

async function forceUpdate() {
  renderComponent.value = false
  await nextTick()
  renderComponent.value = true
}

function changeStream(stream: IStream) {
  if (currentStream.value?.twitch === stream.twitch)
    return

  currentStream.value = stream
  forceUpdate()
}
</script>

<template>
  <v-container style="max-width: 1600px">
    <v-card>
      <v-card-title class="text-h5">
        {{ $t('navbar.streams') }}
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="search"
              label="Search"
              clearable
              append-inner-icon="mdi-magnify"
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col
            cols="12"
            md="4"
            :order="smAndDown
              ? 2
              : 1"
          >
            <v-list
              :style="`max-height: ${height - 350}px; overflow-y: auto;`"
              lines="three"
              variant="elevated"
            >
              <v-list-item
                v-for="stream in searchStreams"
                :key="stream.player"
                :class="stream.isLive
                  ? 'fading-background-live mb-5'
                  : 'fading-background-not-live mb-5'"
                @click="changeStream(stream)"
              >
                <template #prepend>
                  <v-avatar
                    rounded="0"
                    size="70"
                    class="mr-1"
                  >
                    <v-img
                      :src="teamImages[stream.team]?.[stream.player.toLowerCase()]"
                      lazy-src="~/assets/default.png"
                    />
                  </v-avatar>
                </template>

                <div style="display: flex; align-items: center; justify-content: space-between">
                  <span class="text-h6">
                    {{ `${stream.team} ${stream.player}` }}
                  </span>

                  <div class="mr-6">
                    <NuxtLink
                      :to="`/player/${stream.team}/${stream.player}`"
                      @click.stop
                    >
                      <v-avatar
                        size="40"
                        class="mr-3"
                      >
                        <v-icon
                          size="40"
                          icon="mdi-account"
                          color="gray"
                        />

                        <v-tooltip
                          activator="parent"
                          location="bottom"
                        >
                          {{ $t('streams.profile') }}
                        </v-tooltip>
                      </v-avatar>
                    </NuxtLink>

                    <NuxtLink
                      v-if="stream.isLive"
                      external
                      :to="`${fullUrl.twitch}/${stream.twitch}`"
                      @click.stop
                    >
                      <v-avatar
                        size="50"
                        rounded="0"
                        variant="flat"
                      >
                        <v-badge
                          dot
                          color="red"
                        >
                          <v-icon
                            size="40"
                            icon="mdi-twitch"
                            color="secondary"
                          />

                          <v-tooltip
                            activator="parent"
                            location="bottom"
                          >
                            {{ $t('proPlayers.isLive', {"player": stream.player}) }}
                          </v-tooltip>
                        </v-badge>
                      </v-avatar>
                    </NuxtLink>

                    <NuxtLink
                      v-else-if="!stream.isLive"
                      external
                      :to="`${fullUrl.twitch}/${stream.twitch}`"
                      @click.stop
                    >
                      <v-avatar
                        size="50"
                        rounded="0"
                        variant="flat"
                      >
                        <v-icon
                          size="40"
                          icon="mdi-twitch"
                          color="gray"
                        />
                      </v-avatar>
                    </NuxtLink>
                  </div>
                </div>
              </v-list-item>
            </v-list>
          </v-col>

          <v-col
            cols="12"
            md="8"
            style="display: flex; justify-content: center; align-items: start;"
            :order="smAndDown
              ? 1
              : 2"
          >
            <twitch-stream
              v-if="renderComponent && currentStream?.twitch"
              height="480px"
              width="854px"
              :channel="currentStream.twitch"
              muted
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<!-- secondary -->
<style scoped>
.fading-background-live {
  background: linear-gradient(to right, rgba(113, 108, 147, 0.5), rgba(0, 0, 0, 0));
}

.fading-background-not-live {
  background: linear-gradient(to right, rgba(150, 150, 150, 0.5), rgba(0, 0, 0, 0));
}
</style>
