import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Login - Literattus',
  description: 'Sign in to your Literattus account',
}

export default function LoginPage(): JSX.Element {
  return (
    <div>
      <h1 className="text-2xl font-bold text-center mb-6">Login</h1>
      <p className="text-center text-gray-600">
        Welcome back to Literattus! Please sign in to continue.
      </p>
    </div>
  )
}
