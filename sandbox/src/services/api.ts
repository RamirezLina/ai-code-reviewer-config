export interface User {
  id: number;
  name: string;
  avatarUrl: string;
}

const BASE_URL = '/api';

export async function getUser (id: number): Promise<User> {
  console.log(`getUser(${id})`); //Tdodo recordar borrar
  const res = await fetch(`${BASE_URL}/users/${id}`);
  if (!res.ok) throw new Error(`getUser failed: ${res.status}`);
  return (await res.json()) as User;
}
