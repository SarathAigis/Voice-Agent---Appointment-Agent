/**
 * Shared types and utilities for the voice agent system
 */

export interface Driver {
  id: string
  name: string
  phone: string
  truckNumber: string
}

export interface Appointment {
  id: string
  driverId: string
  driverName: string
  appointmentType: 'delivery' | 'maintenance' | 'compliance'
  facility: string
  startTime: string
  endTime: string
  status: 'scheduled' | 'completed' | 'cancelled' | 'no-show'
}

export interface Call {
  callSid: string
  driverName: string
  driverPhone: string
  startTime: string
  duration: number
  status: 'initiated' | 'ringing' | 'in-progress' | 'completed' | 'failed'
  outcome: 'completed' | 'voicemail' | 'failed' | 'escalated'
  appointmentBooked: boolean
}

export interface DashboardStats {
  activeCalls: number
  callsToday: number
  avgDuration: number
  successRate: number
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export const formatPhoneNumber = (phone: string): string => {
  // Format +1234567890 to (123) 456-7890
  const cleaned = phone.replace(/\D/g, '')
  const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{4})$/)
  if (match) {
    return `(${match[2]}) ${match[3]}-${match[4]}`
  }
  return phone
}
