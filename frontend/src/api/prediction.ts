import {api} from '../lib/api-config'; import {Wafer} from '../types';
export const predict=(x:Wafer)=>api<any>('/predict',{method:'POST',body:JSON.stringify(x)});
export const preprocess=(x:Wafer)=>api<any>('/preprocess',{method:'POST',body:JSON.stringify(x)});
export const unknownDefect=(x:Wafer)=>api<any>('/unknown-defect',{method:'POST',body:JSON.stringify(x)});
export const rootCause=(x:Wafer)=>api<any>('/recommend-cause',{method:'POST',body:JSON.stringify(x)});
export const whatIf=(x:any)=>api<any>('/what-if',{method:'POST',body:JSON.stringify(x)});
