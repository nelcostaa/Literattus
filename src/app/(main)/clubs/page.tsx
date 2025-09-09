import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Book Clubs - Literattus',
  description: 'Discover and join book clubs',
}

export default function ClubsPage(): JSX.Element {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Book Clubs</h1>
      <p className="text-gray-600 mb-8">
        Discover, join, and create book clubs with fellow readers.
      </p>
    </div>
  )
}
