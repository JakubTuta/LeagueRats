export function requiredRule(t: (arg0: string) => string) {
  return (value: string | number | null, textError = t('rules.requiredField')) => {
    return Boolean(value) || textError
  }
}

export function lengthRule(t: (arg0: string, arg1: { length: number }) => string, length: number) {
  return (value: string | null, textError = t('rules.maxLength', { length })) => {
    return !value || value.length <= length || textError
  }
}
