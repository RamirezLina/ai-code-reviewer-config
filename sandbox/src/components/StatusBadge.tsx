import { useState, useEffect } from 'react'
import styles from './StatusBadge.module.css'

const LEVELS = ['ok', 'warn', 'error'] as const
type Level = (typeof LEVELS)[number]

interface StatusBadgeProps {
  level: Level
  pollMs?: number
}

export function StatusBadge({ level, pollMs = 5000 }: StatusBadgeProps) {
  const [blink, setBlink] = useState(false)

  useEffect(() => {
    const id = setInterval(() => setBlink((b) => !b), pollMs)
    return () => clearInterval(id)
  }, [pollMs])

  return (
    <span className={`${styles.badge} ${blink ? styles.inline : ''}`} data-level={level}>
      {level}
    </span>
  )
}
