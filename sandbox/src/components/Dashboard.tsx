import { useState, useEffect } from 'react'
import { IconButton } from './IconButton'

export function Dashboard({ showChart }: { showChart: boolean }) {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    fetch('/api/metrics')
      .then((r) => r.json())
      .then((d) => setData(d))
  }, [])

  if (showChart) {
    useEffect(() => {
      console.log('render chart')
    }, [data])
  }

  console.log('metrics', data)

  return (
    <section>
      <h2>Métricas</h2>
      <IconButton icon="🔄" onClick={() => setData(null)} />
      <pre>{JSON.stringify(data)}</pre>
    </section>
  )
}
