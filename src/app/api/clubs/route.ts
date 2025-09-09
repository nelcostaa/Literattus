import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest): Promise<NextResponse> {
  // Get clubs endpoint placeholder
  return NextResponse.json({ message: 'Clubs API endpoint' })
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  // Create club endpoint placeholder
  return NextResponse.json({ message: 'Create club endpoint' })
}
