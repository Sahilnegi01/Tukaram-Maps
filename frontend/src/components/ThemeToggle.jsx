import {useEffect,useState} from 'react';

const initialTheme=()=>localStorage.getItem('tukaram-theme')||'light';

export default function ThemeToggle(){
  const [theme,setTheme]=useState(initialTheme);
  useEffect(()=>{document.documentElement.dataset.theme=theme;localStorage.setItem('tukaram-theme',theme)},[theme]);
  return <div className="themeToggle" role="group" aria-label="Choose color theme">
    <button className={theme==='light'?'active':''} type="button" onClick={()=>setTheme('light')} aria-pressed={theme==='light'}><span aria-hidden="true">☀</span>Light</button>
    <button className={theme==='dark'?'active':''} type="button" onClick={()=>setTheme('dark')} aria-pressed={theme==='dark'}><span aria-hidden="true">☾</span>Dark</button>
  </div>;
}
