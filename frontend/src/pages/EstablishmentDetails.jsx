import {useQuery} from '@tanstack/react-query';
import {useNavigate,useParams} from 'react-router-dom';
import {ActionHistory} from '../components/Establishment/ActionHistory';
import ThemeToggle from '../components/ThemeToggle';
import {getEstablishment} from '../services/api';

const label=value=>(value||'Unknown').replaceAll('_',' ');
const severeTypes=new Set(['SEALED','RAIDED','LICENSE_CANCELLED','SHUT_DOWN','DEMOLISHED']);
const statusCopy={OPEN:'Operating at present',CLOSED:'Not operating at present',UNKNOWN:'Current operating status is unconfirmed'};
const severity=actions=>actions.some(action=>severeTypes.has(action.type))?'Critical Action':actions.some(action=>action.type==='NOTICE_ISSUED')?'Notice Issued':'Recorded Action';

export default function EstablishmentDetails(){
  const {id}=useParams(),navigate=useNavigate();
  const {data,isLoading,error}=useQuery({queryKey:['establishment',id],queryFn:()=>getEstablishment(id)});
  if(isLoading)return <div className="detailState">Loading record…</div>;
  if(error)return <div className="detailState"><b>Unable to load this record.</b><button onClick={()=>navigate('/')}>Back to Map</button></div>;
  const actions=data.actions||[],latest=actions[0]||{},evidenceCount=actions.reduce((count,action)=>count+(action.articles?.length||0),0),area=data.address?.split(',')[0];
  const share=async()=>{const payload={title:data.name,text:`Public record for ${data.name}`,url:window.location.href};if(navigator.share)await navigator.share(payload);else await navigator.clipboard?.writeText(window.location.href)};
  const viewOnMap=()=>navigate('/',{state:{focus:{id:data.id,name:data.name,city:data.city,state:data.state,latitude:data.latitude,longitude:data.longitude}}});
  return <main className="recordPage">
    <header className="recordTopbar"><div><button className="backButton" type="button" onClick={()=>navigate('/')}>← Back to Map</button><span>Tukaram Maps · Public Record</span></div><nav><ThemeToggle/><button onClick={share}>Share</button><button onClick={()=>window.print()}>Export PDF</button><button className="disputeButton">Report Dispute</button></nav></header>
    <div className="recordContent">
      <nav className="breadcrumbs" aria-label="Breadcrumb"><button onClick={()=>navigate('/')}>Home</button><span>/</span><span>{data.state}</span><span>/</span><span>{data.city}</span>{area&&<><span>/</span><span>{area}</span></>}<span>/</span><b>{data.name}</b></nav>
      <section className="recordHero"><div className="recordIdentity"><div className="recordBadges"><span>{label(data.type)}</span><span className="verifiedBadge">✓ Government Verified Record · {evidenceCount} {evidenceCount===1?'source':'sources'}</span></div><code>RECORD · {String(data.id).slice(0,8).toUpperCase()}</code><h1>{data.name}</h1><p>⌖ {data.address&&`${data.address}, `}{data.city}, {data.state} <button onClick={viewOnMap}>View on Map</button></p></div><aside className={`currentStatus current-${data.current_status?.toLowerCase()}`}><small>Current Status</small><b>{label(data.current_status)}</b><p>{statusCopy[data.current_status]||statusCopy.UNKNOWN}</p></aside></section>
      <section className="recordInfo" aria-label="Record summary"><div><small>Severity Level</small><b>{severity(actions)}</b></div><div><small>Issuing Authority</small><b>{latest.authority||'Not reported'}</b></div><div><small>Order Date</small><b>{latest.date||'Not reported'}</b></div><div><small>Legal Sanction / Outcome</small><b>{label(latest.type)}</b></div></section>
      <section className="historySection"><div className="sectionHeading"><div><h2>Historical Actions &amp; Audit Log</h2><p>Verified actions shown from most recent to oldest.</p></div><span>{actions.length} Enforced {actions.length===1?'Event':'Events'}</span></div>{actions.length?<ActionHistory actions={actions}/>:<p className="emptyHistory">No verified historical actions are available.</p>}</section>
      <aside className="publicNotice"><b>Public Record Notice</b><p>This page summarizes public regulatory notices and press reporting. Current operating status is shown separately from historical actions. Businesses may report inaccurate information for review.</p></aside>
    </div>
    <footer className="recordFooter"><span>© {new Date().getFullYear()} Tukaram Maps</span><nav><a href="mailto:negisahil642@gmail.com">Contact: negisahil642@gmail.com</a></nav></footer>
  </main>;
}
