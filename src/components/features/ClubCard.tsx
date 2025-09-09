import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

interface ClubCardProps {
  name: string
  description: string
  memberCount: number
  coverImage?: string
  isPrivate?: boolean
  className?: string
}

export function ClubCard({
  name,
  description,
  memberCount,
  coverImage,
  isPrivate = false,
  className
}: ClubCardProps): JSX.Element {
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{name}</CardTitle>
            <CardDescription className="mt-1">{description}</CardDescription>
          </div>
          {isPrivate && (
            <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">
              Private
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>{memberCount} members</span>
          <span>📚</span>
        </div>
      </CardContent>
    </Card>
  )
}
