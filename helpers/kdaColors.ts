export function mapKDAToColor(kda: number): string {
  if (kda <= 1) {
    return 'gray'
  }
  else if (kda <= 2) {
    return 'white'
  }
  else if (kda <= 3) {
    return 'green-darken-2'
  }
  else if (kda <= 4) {
    return 'blue-darken-2'
  }
  else if (kda <= 5) {
    return 'red-darken-2'
  }
  else {
    return 'yellow-accent-4'
  }
}
