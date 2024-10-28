// @ts-expect-error correct path
import SummonerBarrier from '~/assets/summoners/SummonerBarrier.png'
// @ts-expect-error correct path
import SummonerBoost from '~/assets/summoners/SummonerBoost.png'
// @ts-expect-error correct path
import SummonerDot from '~/assets/summoners/SummonerDot.png'
// @ts-expect-error correct path
import SummonerExhaust from '~/assets/summoners/SummonerExhaust.png'
// @ts-expect-error correct path
import SummonerFlash from '~/assets/summoners/SummonerFlash.png'
// @ts-expect-error correct path
import SummonerHaste from '~/assets/summoners/SummonerHaste.png'
// @ts-expect-error correct path
import SummonerHeal from '~/assets/summoners/SummonerHeal.png'
// @ts-expect-error correct path
import SummonerMana from '~/assets/summoners/SummonerMana.png'
// @ts-expect-error correct path
import SummonerSmite from '~/assets/summoners/SummonerSmite.png'
// @ts-expect-error correct path
import SummonerSnowball from '~/assets/summoners/SummonerSnowball.png'
// @ts-expect-error correct path
import SummonerTeleport from '~/assets/summoners/SummonerTeleport.png'
import { summonerSpellsIds } from '~/helpers/summonerSpellsIds'

export const useSummonerSpellsStore = defineStore('summonerSpellsStore', () => {
  const summonerSpellIcons = ref<Record<number, string>>({})

  const getAllSummonerSpellIcons = () => {
    for (const [summonerId, summonerName] of Object.entries(summonerSpellsIds)) {
      switch (summonerName) {
        case 'SummonerBarrier':
          summonerSpellIcons.value[Number(summonerId)] = SummonerBarrier
          break
        case 'SummonerBoost':
          summonerSpellIcons.value[Number(summonerId)] = SummonerBoost
          break
        case 'SummonerDot':
          summonerSpellIcons.value[Number(summonerId)] = SummonerDot
          break
        case 'SummonerExhaust':
          summonerSpellIcons.value[Number(summonerId)] = SummonerExhaust
          break
        case 'SummonerFlash':
          summonerSpellIcons.value[Number(summonerId)] = SummonerFlash
          break
        case 'SummonerHaste':
          summonerSpellIcons.value[Number(summonerId)] = SummonerHaste
          break
        case 'SummonerHeal':
          summonerSpellIcons.value[Number(summonerId)] = SummonerHeal
          break
        case 'SummonerMana':
          summonerSpellIcons.value[Number(summonerId)] = SummonerMana
          break
        case 'SummonerSmite':
          summonerSpellIcons.value[Number(summonerId)] = SummonerSmite
          break
        case 'SummonerSnowball':
          summonerSpellIcons.value[Number(summonerId)] = SummonerSnowball
          break
        case 'SummonerTeleport':
          summonerSpellIcons.value[Number(summonerId)] = SummonerTeleport
          break
        default:
          console.warn(`No image found for summoner spell: ${summonerName}`)
      }
    }
  }

  getAllSummonerSpellIcons()

  return {
    summonerSpellIcons,
  }
})
