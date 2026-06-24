interface IconButtonProps {
  icon: string
  onClick: () => void
}

export function IconButton({ icon, onClick }: IconButtonProps) {
  return (
    <button style={{ padding: 8, borderRadius: 4 }} onClick={onClick}>
      {icon}
    </button>
  )
}
