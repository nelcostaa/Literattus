import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Register - Literattus',
  description: 'Create your Literattus account',
}

export default function RegisterPage(): JSX.Element {
  return (
    <div>
      <h1 className="text-2xl font-bold text-center mb-6">Register</h1>
      <p className="text-center text-gray-600">
        Join the Literattus community and start your reading journey!
      </p>
    </div>
  )
}
