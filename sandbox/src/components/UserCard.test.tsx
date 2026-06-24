import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { UserCard } from './UserCard'

describe('UserCard', () => {
  it('muestra el nombre del usuario', () => {
    render(
      <UserCard user={{ id: 1, name: 'Ada Lovelace', avatarUrl: '/a.png' }} />,
    )
    expect(screen.getByText('Ada Lovelace')).toBeInTheDocument()
  })
})
