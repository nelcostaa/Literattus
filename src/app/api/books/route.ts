import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest): Promise<NextResponse> {
  // Get books endpoint placeholder
  return NextResponse.json({ message: 'Books API endpoint' })
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  // Create book endpoint placeholder
  return NextResponse.json({ message: 'Create book endpoint' })
}
