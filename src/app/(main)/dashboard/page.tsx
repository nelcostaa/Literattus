import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dashboard - Literattus',
  description: 'Your personal reading dashboard',
}

export default function DashboardPage(): JSX.Element {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-2">Reading Progress</h2>
          <p className="text-gray-600">Track your current books and goals</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-2">Active Clubs</h2>
          <p className="text-gray-600">Your book club memberships</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-2">Recommendations</h2>
          <p className="text-gray-600">Discover new books</p>
        </div>
      </div>
    </div>
  )
}
