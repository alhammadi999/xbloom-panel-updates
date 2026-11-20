'use strict';
function panelCallback(search) {
  const q = new URLSearchParams(search);
  if (q.has('error')) throw new Error('Sign-in was cancelled. Scan a new QR on the panel to try again.');
  if ([...q.keys()].length !== 2 || q.getAll('state').length !== 1 || q.getAll('code').length !== 1) throw new Error('Invalid sign-in response.');
  const state = q.get('state'), code = q.get('code');
  const match = /^(\d{1,3}(?:\.\d{1,3}){3})~[a-f0-9]{32}$/.exec(state);
  if (!match || !code || code.length > 2048 || !/^[\x21-\x7e]+$/.test(code)) throw new Error('Invalid sign-in response.');
  const octets = match[1].split('.').map(Number), [a,b] = octets;
  if (octets.some(n => n > 255) || octets.join('.') !== match[1] || !(a===10 || a===172 && b>=16 && b<=31 || a===192 && b===168)) throw new Error('Invalid panel address.');
  return 'http://' + match[1] + '/spotify/callback?' + new URLSearchParams({state,code});
}
function cloudCallback(search) {
  const q=new URLSearchParams(search);
  if(q.getAll('state').length!==1||q.getAll('code').length!==1||[...q.keys()].length!==2)throw new Error('Invalid sign-in response.');
  const state=q.get('state'),code=q.get('code');
  if(!/^r2\.[a-f0-9]{64}\.[a-f0-9]{64}$/.test(state)||!code||code.length>2048||! /^[\x21-\x7e]+$/.test(code))throw new Error('Invalid sign-in response.');
  return {state,code};
}
if (typeof module !== 'undefined') module.exports = {panelCallback,cloudCallback};
if (typeof window !== 'undefined') {
 (async()=>{try {
    if (!window.location.search) return;
    if(new URLSearchParams(window.location.search).get('state')?.startsWith('r2.')){
      const payload=cloudCallback(window.location.search);
      history.replaceState(null,'',window.location.pathname);
      document.getElementById('message').textContent='Completing sign-in with your panel. You can stay on mobile data.';
      const r=await fetch('https://threedup-spotify-link.s-alhammadi999.chatgpt.site/api/complete',{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if(!r.ok)throw new Error('Link expired or unavailable. Scan a new QR on the panel and try again.');
      document.getElementById('message').textContent='Sign-in received. Your panel will finish connecting automatically. You can close this page and check the panel.';
      return;
    }
    const target = panelCallback(window.location.search);
    history.replaceState(null, '', window.location.pathname);
    document.getElementById('message').textContent = 'Returning to your panel. Keep your phone on the same Wi-Fi.';
    const link = document.getElementById('return'); link.href=target; link.hidden=false;
    window.location.replace(target);
  } catch(e) {
    history.replaceState(null, '', window.location.pathname);
    document.getElementById('message').textContent = e.message;
  }})();
}

