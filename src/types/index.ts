// User Types
export interface User {
  id: number
  email: string
  firstName: string
  lastName: string
  avatar?: string
  bio?: string
  isActive: boolean
  createdAt: Date
  updatedAt: Date
}

// Book Types
export interface Book {
  id: number
  googleBooksId: string
  title: string
  author: string
  isbn?: string
  description?: string
  coverImage?: string
  publishedDate?: string
  pageCount?: number
  genres?: string[]
  averageRating: number
  createdAt: Date
  updatedAt: Date
}

// Club Types
export interface Club {
  id: number
  name: string
  description: string
  coverImage?: string
  isPrivate: boolean
  createdById: number
  maxMembers: number
  createdAt: Date
  updatedAt: Date
}

// Reading Progress Types
export enum ReadingStatus {
  WANT_TO_READ = 'want_to_read',
  CURRENTLY_READING = 'currently_reading',
  COMPLETED = 'completed',
  DNF = 'did_not_finish',
}

export interface ReadingProgress {
  id: number
  userId: number
  bookId: number
  status: ReadingStatus
  currentPage: number
  rating?: number
  review?: string
  startedAt?: Date
  completedAt?: Date
  createdAt: Date
  updatedAt: Date
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// Google Books API Types
export interface GoogleBook {
  id: string
  volumeInfo: {
    title: string
    authors?: string[]
    description?: string
    imageLinks?: {
      thumbnail?: string
      smallThumbnail?: string
    }
    publishedDate?: string
    pageCount?: number
    categories?: string[]
    averageRating?: number
    industryIdentifiers?: Array<{
      type: string
      identifier: string
    }>
  }
}
