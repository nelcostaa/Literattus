interface MainLayoutProps {
  children: React.ReactNode
}

export default function MainLayout({ children }: MainLayoutProps): JSX.Element {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-blue-600">Literattus</h1>
            </div>
            <nav className="flex space-x-8">
              <span className="text-gray-700 hover:text-blue-600">Dashboard</span>
              <span className="text-gray-700 hover:text-blue-600">Clubs</span>
              <span className="text-gray-700 hover:text-blue-600">Books</span>
              <span className="text-gray-700 hover:text-blue-600">Profile</span>
            </nav>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}
