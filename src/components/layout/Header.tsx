import React from 'react'
import Link from 'next/link'

interface HeaderProps {
  className?: string
}

export function Header({ className }: HeaderProps): JSX.Element {
  return (
    <header className={`bg-white shadow-sm border-b ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-blue-600">
              Literattus
            </Link>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link
              href="/dashboard"
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/clubs"
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              Clubs
            </Link>
            <Link
              href="/books"
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              Books
            </Link>
            <Link
              href="/profile"
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              Profile
            </Link>
          </nav>
          <div className="flex items-center space-x-4">
            <Link
              href="/login"
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
