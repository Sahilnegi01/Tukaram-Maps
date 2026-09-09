import {useSearchParams} from 'react-router-dom';export default function ReviewResult(){const [p]=useSearchParams(),ok=p.get('status')==='approved';return <main className="page"><h1>{ok?'✓ Action Approved':'✕ Action Rejected'}</h1><p>{ok?'This verified action is now eligible for public display.':'This action will not be displayed publicly.'}</p></main>}

