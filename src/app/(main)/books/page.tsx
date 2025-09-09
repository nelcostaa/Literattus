import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Books - Literattus',
  description: 'Browse and manage your book library',
}

export default function BooksPage(): JSX.Element {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Books</h1>
      <p className="text-gray-600 mb-8">
        Manage your personal library and discover new reads.
      </p>
    </div>
  )
}
