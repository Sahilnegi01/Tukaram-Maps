const label=value=>(value||'ACTION').replaceAll('_',' ');

export function EvidenceCard({article}){
  return <a className="evidenceCard" href={article.url} target="_blank" rel="noreferrer">
    <span className="evidenceIcon">↗</span>
    <span><small>{article.source||'Public source'}</small><b>{article.title||'Public coverage'}</b>{article.summary&&<em>{article.summary}</em>}</span>
    <strong>View source</strong>
  </a>;
}

export function ActionHistory({actions=[]}){
  return <div className="auditTimeline">{actions.map((action,index)=><details className={`auditEntry status-${action.type?.toLowerCase()}`} key={action.id} open={index===0}>
    <summary><span className="auditDot"/><span><span className="actionPill">{label(action.type)}</span><time>{action.date||'Date not reported'}</time><b>{action.title||label(action.type)}</b></span><i aria-hidden="true">⌄</i></summary>
    <div className="auditBody">
      <div className="agency"><small>Enforcing Agency</small><b>{action.authority||'Authority not reported'}</b></div>
      <h4>Executive Summary</h4><p>{action.detail||action.reason||'No additional details were included in the public record.'}</p>
      {!!action.infractions?.length&&<><h4>Specific Infractions Noted</h4><div className="infractionTags">{action.infractions.map(item=><span key={item}>{item}</span>)}</div></>}
      {!!action.articles?.length&&<><h4>Supporting Evidence &amp; Public Coverage</h4><div className="evidenceGrid">{action.articles.map(article=><EvidenceCard article={article} key={article.url}/>)}</div></>}
    </div>
  </details>)}</div>;
}
