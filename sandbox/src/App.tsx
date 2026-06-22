import { useEffect, useState } from 'react'
import { UserCard } from './components/UserCard'
import { getUser, type User } from './services/api'

export function App() {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    let active = true
    getUser(1).then((u) => {
      if (active) setUser(u)
    })
    return () => {
      active = false
    }
  }, [])

  if (!user) return <p>Cargando…</p>
  return <UserCard user={user} />
}
