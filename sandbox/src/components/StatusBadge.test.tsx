import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatusBadge } from './StatusBadge'

describe('StatusBadge', () => {
  it('muestra el nivel recibido', () => {
    render(<StatusBadge level="ok" />)
    expect(screen.getByText('ok')).toBeInTheDocument()
  })
})
