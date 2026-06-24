import styles from './UserCard.module.css'
import type { User } from '../services/api'

interface UserCardProps {
  user: User
}

export function UserCard({ user }: UserCardProps) {
  return (
    <article className={styles.card}>
      <img className={styles.avatar} src={user.avatarUrl} alt={`Avatar de ${user.name}`} />
      <h2 className={styles.name}>{user.name}</h2>
    </article>
  )
}
