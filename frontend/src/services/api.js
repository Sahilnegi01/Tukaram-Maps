const BASE=import.meta.env.VITE_API_URL || '/api/v1';
async function request(path,options){const r=await fetch(`${BASE}${path}`,{headers:{'Content-Type':'application/json'},...options});const body=await r.json().catch(()=>({}));if(!r.ok)throw Object.assign(new Error(body.error?.message||'Unable to load data.'),{code:body.error?.code,status:r.status});return body.data;}
const qs=p=>{const s=new URLSearchParams();Object.entries(p||{}).forEach(([k,v])=>v!==''&&v!=null&&s.set(k,v));return s.toString()};
export const getMapEstablishments=p=>request(`/map/establishments?${qs(p)}`);
export const getOverview=()=>request('/map/overview');
export const searchEstablishments=q=>request(`/establishments/search?q=${encodeURIComponent(q)}`);
export const getEstablishment=id=>request(`/establishments/${id}`);
export const getReview=token=>request(`/reviews/${encodeURIComponent(token)}`);
export const approveReview=token=>request(`/reviews/${encodeURIComponent(token)}/approve`,{method:'POST'});
export const rejectReview=token=>request(`/reviews/${encodeURIComponent(token)}/reject`,{method:'POST'});
export const getPendingReviews=key=>request('/internal/reviews',{headers:{'X-Internal-API-Key':key}});
export const createReviewAccessLink=(id,key)=>request(`/internal/reviews/${id}/access-link`,{method:'POST',headers:{'X-Internal-API-Key':key,'Content-Type':'application/json'}});
