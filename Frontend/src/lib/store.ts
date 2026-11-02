/* NEXT POS data layer. The UI contract is kept stable; data is loaded from Django API. */
import { useSyncExternalStore } from 'react'
export type Role = 'manager' | 'cashier'
export type Account = { id:string; name:string; email:string; title:string; role:Role; active:boolean; createdAt:number; createdBy:string|null }
export type Shift = { id:string; cashierId:string; startedAt:number; endedAt:number|null }
export type Transaction = { id:string; number:number; cashierId:string; shiftId:string; at:number; items:number; subtotal:number; discount?:number; tax:number; total:number; orderType:string; guestCount?:number|null }
export type Product = { id:number; name:string; description:string; price:number; category:string; image:string; tag:string; active:boolean }
export type Result<T> = {ok:true;value:T}|{ok:false;error:string}
export type ShiftStats = {shift:Shift;orders:number;items:number;sales:number;avgTicket:number;durationMs:number;ordersPerHour:number}
export type CashierSummary = {account:Account;activeShift:Shift|null;shifts:number;orders:number;items:number;sales:number;avgTicket:number;ordersPerHour:number;durationMs:number;recent:ShiftStats[]}
export const MIN_PASSWORD=6
const HOUR=3600000, DAY=86400000
const API=import.meta.env.VITE_API_BASE_URL || '/api'
const KEYS={token:'nextpos.apiToken',account:'nextpos.account',remember:'nextpos.remember',cashiers:'nextpos.accounts',shifts:'nextpos.shifts',transactions:'nextpos.transactions',products:'nextpos.products'}
const memory=new Map<string,string>()
function getItem(k:string):string|null {try{return localStorage.getItem(k)??sessionStorage.getItem(k)}catch{return memory.get(k)??null}}
function setItem(k:string,v:string){try{localStorage.setItem(k,v)}catch{memory.set(k,v)}}
function removeItem(k:string){try{localStorage.removeItem(k);sessionStorage.removeItem(k)}catch{memory.delete(k)}}
function parse<T>(k:string,f:T):T{try{const s=getItem(k);return s?JSON.parse(s) as T:f}catch{return f}}
function persist(k:string,v:unknown){setItem(k,JSON.stringify(v));emit()}
function token(){return getItem(KEYS.token)}
async function api<T>(path:string, options:RequestInit={}, authenticated=true):Promise<T>{
 const headers=new Headers(options.headers); if(options.body && !headers.has('Content-Type')) headers.set('Content-Type','application/json'); if(authenticated&&token()) headers.set('Authorization',`Token ${token()}`)
 const response=await fetch(`${API}${path}`,{...options,headers})
 let body:any={}; try{body=await response.json()}catch{}
 if(!response.ok) throw new Error(body.error||body.detail||Object.values(body).flat().join(' ')||`Permintaan gagal (${response.status})`)
 return body as T
}
let accounts:Account[]=parse(KEYS.cashiers,[]), shifts:Shift[]=parse(KEYS.shifts,[]), transactions:Transaction[]=parse(KEYS.transactions,[]), products:Product[]=parse(KEYS.products,[])
let version=0;const listeners=new Set<()=>void>();const pendingShiftStarts=new Map<string,Promise<unknown>>()
function emit(){version++;listeners.forEach(fn=>fn())}
export function subscribe(fn:()=>void){listeners.add(fn);return()=>listeners.delete(fn)}
export function useStoreVersion(){return useSyncExternalStore(subscribe,()=>version)}
function saveCache(){setItem(KEYS.cashiers,JSON.stringify(accounts));setItem(KEYS.shifts,JSON.stringify(shifts));setItem(KEYS.transactions,JSON.stringify(transactions));setItem(KEYS.products,JSON.stringify(products));emit()}
function cacheBootstrap(data:any){accounts=[...(data.cashiers||[])];const me=data.account as Account;if(me&&!accounts.some(a=>a.id===me.id))accounts.push(me);shifts=data.shifts||[];transactions=data.transactions||[];products=data.products||[];if(me)setItem(KEYS.account,JSON.stringify(me));saveCache()}
async function refresh(){if(!token())return;const data=await api<any>('/bootstrap/');cacheBootstrap(data)}
export function startOfToday(){const d=new Date();d.setHours(0,0,0,0);return d.getTime()}
export function currentAccount():Account|null {if(!token())return null;return parse<Account|null>(KEYS.account,null)}
export function logout(){const t=token();if(t) void api('/auth/logout/',{method:'POST'}).catch(()=>{});removeItem(KEYS.token);removeItem(KEYS.account);emit()}
function valid(name:string,email:string,password:string){if(name.trim().length<2)return 'Nama lengkap minimal 2 karakter.';if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))return 'Masukkan alamat email yang valid.';if(password.length<MIN_PASSWORD)return `Kata sandi minimal ${MIN_PASSWORD} karakter.`;return null}
function setAuth(data:any,remember:boolean):Account{removeItem(KEYS.token);try{(remember?localStorage:sessionStorage).setItem(KEYS.token,data.token)}catch{memory.set(KEYS.token,data.token)}setItem(KEYS.account,JSON.stringify(data.account));return data.account}
export async function registerManager(input:{name:string;email:string;password:string},remember:boolean):Promise<Result<Account>>{const issue=valid(input.name,input.email,input.password);if(issue)return{ok:false,error:issue};try{const data=await api<any>('/auth/register-manager/',{method:'POST',body:JSON.stringify(input)},false);const account=setAuth(data,remember);await refresh();return{ok:true,value:account}}catch(e){return{ok:false,error:(e as Error).message}}}
export async function login(email:string,password:string,remember:boolean):Promise<Result<Account>>{if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))return{ok:false,error:'Masukkan alamat email yang valid.'};if(!password)return{ok:false,error:'Masukkan kata sandi Anda.'};try{const data=await api<any>('/auth/login/',{method:'POST',body:JSON.stringify({email,password})},false);const account=setAuth(data,remember);await refresh();return{ok:true,value:account}}catch(e){return{ok:false,error:(e as Error).message}}}
export async function createCashier(actorId:string,input:{name:string;email:string;password:string;title:string}):Promise<Result<Account>>{const issue=valid(input.name,input.email,input.password);if(issue)return{ok:false,error:issue};try{const account=await api<Account>('/cashiers/',{method:'POST',body:JSON.stringify(input)});accounts=[...accounts,account];saveCache();return{ok:true,value:account}}catch(e){return{ok:false,error:(e as Error).message}}}
export async function resetCashierPassword(_actorId:string,cashierId:string,password:string):Promise<Result<true>>{if(password.length<MIN_PASSWORD)return{ok:false,error:`Kata sandi minimal ${MIN_PASSWORD} karakter.`};try{await api('/cashiers/password/',{method:'POST',body:JSON.stringify({id:cashierId,password})});return{ok:true,value:true}}catch(e){return{ok:false,error:(e as Error).message}}}
export function setCashierActive(_actorId:string,cashierId:string,active:boolean):Result<true>{const found=accounts.some(a=>a.id===cashierId&&a.role==='cashier');if(!found)return{ok:false,error:'Kasir tidak ditemukan.'};accounts=accounts.map(a=>a.id===cashierId?{...a,active}:a);if(!active)shifts=shifts.map(s=>s.cashierId===cashierId&&s.endedAt===null?{...s,endedAt:Date.now()}:s);saveCache();void api('/cashiers/',{method:'PATCH',body:JSON.stringify({id:cashierId,active})}).then(refresh).catch(console.error);return{ok:true,value:true}}
export function updateProfile(accountId:string,changes:{name:string;title:string}):Result<Account>{const account=currentAccount();if(!account||account.id!==accountId)return{ok:false,error:'Akun tidak ditemukan.'};if(changes.name.trim().length<2)return{ok:false,error:'Nama lengkap minimal 2 karakter.'};const updated={...account,name:changes.name.trim(),title:changes.title.trim()||account.title};setItem(KEYS.account,JSON.stringify(updated));accounts=accounts.map(a=>a.id===accountId?updated:a);saveCache();void api<Account>('/profile/',{method:'PATCH',body:JSON.stringify(changes)}).then(data=>{setItem(KEYS.account,JSON.stringify(data));accounts=accounts.map(a=>a.id===accountId?data:a);saveCache()}).catch(console.error);return{ok:true,value:updated}}
export function listCashiers(){return accounts.filter(a=>a.role==='cashier')}
export function listShifts(since=0){return shifts.filter(s=>(s.endedAt??Date.now())>=since).sort((a,b)=>b.startedAt-a.startedAt)}
export function activeShift(cashierId:string){return shifts.find(s=>s.cashierId===cashierId&&s.endedAt===null)??null}
export function startShift(cashierId:string):Shift{let s=activeShift(cashierId);if(s&&Date.now()-s.startedAt<14*HOUR)return s;if(s){shifts=shifts.map(x=>x.id===s!.id?{...x,endedAt:x.startedAt+14*HOUR}:x)}s={id:`local-${Date.now()}`,cashierId,startedAt:Date.now(),endedAt:null};shifts=[s,...shifts];saveCache();const pending=api<Shift>('/shifts/',{method:'POST',body:JSON.stringify({action:'start'})}).then(async saved=>{shifts=shifts.map(x=>x.id===s!.id?saved:x);saveCache();await refresh();return saved}).catch(error=>{console.error(error);throw error}).finally(()=>pendingShiftStarts.delete(cashierId));pendingShiftStarts.set(cashierId,pending);return s}
export function endShift(cashierId:string,endedAt=Date.now()):Shift|null{const s=activeShift(cashierId);if(!s)return null;const closed={...s,endedAt};shifts=shifts.map(x=>x.id===s.id?closed:x);saveCache();void api('/shifts/',{method:'POST',body:JSON.stringify({action:'end'})}).then(refresh).catch(console.error);return closed}
export function nextOrderNumber(){const nums=transactions.map(t=>t.number);return nums.length?Math.max(...nums)+1:1}
export async function recordTransaction(input:{cashierId:string;items:number;subtotal:number;discount?:number;tax:number;orderType:string;guestCount?:number|null}):Promise<Result<Transaction>>{
 const shift=activeShift(input.cashierId)
 if(!shift)return{ok:false,error:'Aktifkan shift terlebih dahulu sebelum memproses pembayaran.'}
 try{const pending=pendingShiftStarts.get(input.cashierId);if(pending)await pending;const saved=await api<Transaction>('/transactions/',{method:'POST',body:JSON.stringify(input)});transactions=[saved,...transactions.filter(t=>t.id!==saved.id)];saveCache();void refresh().catch(console.error);return{ok:true,value:saved}}
 catch(e){return{ok:false,error:(e as Error).message}}
}
export function listTransactions(options?:{cashierId?:string;since?:number}){return transactions.filter(tx=>(!options?.cashierId||tx.cashierId===options.cashierId)&&(!options?.since||tx.at>=options.since)).sort((a,b)=>b.at-a.at)}
export function shiftStats(shift:Shift,all:Transaction[],now=Date.now()):ShiftStats{const own=all.filter(t=>t.shiftId===shift.id),orders=own.length,items=own.reduce((s,t)=>s+t.items,0),sales=own.reduce((s,t)=>s+t.total,0),durationMs=Math.max(0,(shift.endedAt??now)-shift.startedAt),hours=Math.max(durationMs,10*60000)/HOUR;return{shift,orders,items,sales,avgTicket:orders?sales/orders:0,durationMs,ordersPerHour:orders/hours}}
export function currentShiftStats(cashierId:string):ShiftStats|null{const s=activeShift(cashierId);return s?shiftStats(s,transactions):null}
export function cashierSummaries(since=0):CashierSummary[]{const now=Date.now();return listCashiers().map(account=>{const ownShifts=shifts.filter(s=>s.cashierId===account.id&&(s.endedAt??now)>=since),stats=ownShifts.map(s=>shiftStats(s,transactions,now)),activeShift=ownShifts.find(s=>s.endedAt===null)||null;const orders=stats.reduce((n,s)=>n+s.orders,0),items=stats.reduce((n,s)=>n+s.items,0),sales=stats.reduce((n,s)=>n+s.sales,0),durationMs=stats.reduce((n,s)=>n+s.durationMs,0);return{account,activeShift,shifts:ownShifts.length,orders,items,sales,avgTicket:orders?sales/orders:0,ordersPerHour:durationMs?orders/(durationMs/HOUR):0,durationMs,recent:stats.slice(0,5)}})}
export async function ensureSeed():Promise<void>{if(token()){try{await refresh()}catch(e){console.error('API bootstrap failed:',e)}}}
export function listProducts(){return products}
export async function addProduct(input:Omit<Product,'id'>):Promise<Result<Product>>{try{const p=await api<Product>('/products/',{method:'POST',body:JSON.stringify(input)});products=[...products,p];saveCache();return{ok:true,value:p}}catch(e){return{ok:false,error:(e as Error).message}}}
export function toggleProduct(id:number):Result<true>{const p=products.find(x=>x.id===id);if(!p)return{ok:false,error:'Menu tidak ditemukan.'};products=products.map(x=>x.id===id?{...x,active:!x.active}:x);saveCache();void api('/products/',{method:'PATCH',body:JSON.stringify({id,active:!p.active})}).then(refresh).catch(console.error);return{ok:true,value:true}}
export function deleteProduct(id:number):Result<true>{products=products.filter(x=>x.id!==id);saveCache();void api('/products/',{method:'DELETE',body:JSON.stringify({id})}).then(refresh).catch(console.error);return{ok:true,value:true}}
