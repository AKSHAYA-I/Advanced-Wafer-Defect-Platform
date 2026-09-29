export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
export async function api<T>(path:string, options:RequestInit={}) : Promise<T>{
 const r=await fetch(`${API_BASE_URL}${path}`,{headers:{'Content-Type':'application/json',...(options.headers||{})},...options});
 const data=await r.json().catch(()=>({detail:'Invalid server response'})); if(!r.ok) throw new Error(data.detail||`HTTP ${r.status}`); return data;
}
