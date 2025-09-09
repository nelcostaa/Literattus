import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Welcome to Literattus',
  description: 'Your social hub for book clubs and reading communities.',
}

export default function HomePage(): JSX.Element {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="mb-6 text-5xl font-bold text-gray-900">
            Welcome to <span className="text-blue-600">Literattus</span>
          </h1>
          <p className="mb-8 text-xl text-gray-600">
            Your social hub for book clubs and reading communities 📚
          </p>
          <div className="flex justify-center gap-4">
            <div className="rounded-lg bg-white p-6 shadow-lg">
              <h2 className="mb-2 text-lg font-semibold">Join Book Clubs</h2>
              <p className="text-gray-600">Connect with fellow readers</p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow-lg">
              <h2 className="mb-2 text-lg font-semibold">Track Reading</h2>
              <p className="text-gray-600">Monitor your progress</p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow-lg">
              <h2 className="mb-2 text-lg font-semibold">Discover Books</h2>
              <p className="text-gray-600">Find your next great read</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
