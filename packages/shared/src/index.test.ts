import { describe, it, expect } from 'vitest'
import { formatDuration, formatPhoneNumber } from './index'

describe('formatDuration', () => {
  it('should format seconds to MM:SS', () => {
    expect(formatDuration(65)).toBe('1:05')
    expect(formatDuration(125)).toBe('2:05')
    expect(formatDuration(0)).toBe('0:00')
  })
})

describe('formatPhoneNumber', () => {
  it('should format US phone numbers', () => {
    expect(formatPhoneNumber('+12345678900')).toBe('(234) 567-8900')
  })

  it('should return original if format does not match', () => {
    expect(formatPhoneNumber('invalid')).toBe('invalid')
  })
})
