import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

interface BookCardProps {
  title: string
  author: string
  coverImage?: string
  description?: string
  rating?: number
  className?: string
}

export function BookCard({
  title,
  author,
  coverImage,
  description,
  rating,
  className
}: BookCardProps): JSX.Element {
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex gap-4">
          {coverImage && (
            <div className="h-24 w-16 bg-gray-200 rounded flex-shrink-0">
              {/* Book cover placeholder */}
            </div>
          )}
          <div className="flex-1">
            <CardTitle className="text-lg">{title}</CardTitle>
            <CardDescription>by {author}</CardDescription>
            {rating && (
              <div className="mt-2 text-sm text-yellow-600">
                ⭐ {rating.toFixed(1)}
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      {description && (
        <CardContent>
          <p className="text-sm text-gray-600 line-clamp-3">{description}</p>
        </CardContent>
      )}
    </Card>
  )
}
