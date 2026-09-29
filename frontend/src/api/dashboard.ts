import {api} from '../lib/api-config'; export const dashboard=()=>api<any>('/dashboard'); export const health=()=>api<any>('/health'); export const mlops=()=>api<any>('/mlops'); export const feedback=()=>api<any>('/feedback');
export const sendFeedback=(x:any)=>api<any>('/feedback',{method:'POST',body:JSON.stringify(x)});
export const validateFeedback=(id:number)=>api<any>(`/feedback/${id}/validate`,{method:'POST'});
