import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
const client=new QueryClient({defaultOptions:{queries:{staleTime:30000,retry:1}}});
export default function Providers({children}){return <QueryClientProvider client={client}>{children}</QueryClientProvider>}

