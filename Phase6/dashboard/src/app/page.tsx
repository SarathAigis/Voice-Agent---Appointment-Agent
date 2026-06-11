'use client'

import { useEffect, useState } from 'react'
import LiveCallsPanel from '@/components/LiveCallsPanel'
import MetricsOverview from '@/components/MetricsOverview'
import RecentCallsTable from '@/components/RecentCallsTable'
import { Phone, TrendingUp, Clock, AlertCircle } from 'lucide-react'

interface DashboardStats {
  activeCalls: number
  callsToday: number
  avgDuration: number
  successRate: number
}

export default function DashboardHome() {
  const [stats, setStats] = useState<DashboardStats>({
    activeCalls: 0,
    callsToday: 0,
    avgDuration: 0,
    successRate: 0,
  })

  useEffect(() => {
    // Fetch dashboard stats
    const fetchStats = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/stats`)
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Appointment Agent Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Monitor calls, manage appointments, and track performance
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                System Online
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Active Calls"
            value={stats.activeCalls}
            icon={<Phone className="w-6 h-6" />}
            color="blue"
            trend={stats.activeCalls > 0 ? 'up' : 'neutral'}
          />
          <StatCard
            title="Calls Today"
            value={stats.callsToday}
            icon={<TrendingUp className="w-6 h-6" />}
            color="green"
          />
          <StatCard
            title="Avg Duration"
            value={`${Math.floor(stats.avgDuration / 60)}:${(stats.avgDuration % 60).toString().padStart(2, '0')}`}
            icon={<Clock className="w-6 h-6" />}
            color="purple"
          />
          <StatCard
            title="Success Rate"
            value={`${stats.successRate}%`}
            icon={<AlertCircle className="w-6 h-6" />}
            color="indigo"
          />
        </div>

        {/* Live Calls */}
        <div className="mb-8">
          <LiveCallsPanel />
        </div>

        {/* Metrics Overview */}
        <div className="mb-8">
          <MetricsOverview />
        </div>

        {/* Recent Calls */}
        <div>
          <RecentCallsTable />
        </div>
      </main>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  color: 'blue' | 'green' | 'purple' | 'indigo'
  trend?: 'up' | 'down' | 'neutral'
}

function StatCard({ title, value, icon, color, trend }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    indigo: 'bg-indigo-500',
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
        </div>
        <div className={`${colorClasses[color]} p-3 rounded-lg`}>
          <div className="text-white">{icon}</div>
        </div>
      </div>
      {trend && (
        <div className="mt-4">
          <span
            className={`inline-flex items-center text-sm ${
              trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
            }`}
          >
            {trend === 'up' && '↑'}
            {trend === 'down' && '↓'}
            {trend === 'neutral' && '→'}
          </span>
        </div>
      )}
    </div>
  )
}
