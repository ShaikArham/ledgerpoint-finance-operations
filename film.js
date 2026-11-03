(()=>{'use strict';
const video=document.getElementById('film'),poster=document.getElementById('poster'),status=document.getElementById('status'),quality=document.getElementById('quality'),qualityWrap=document.getElementById('quality-wrap'),load=document.getElementById('load'),replay=document.getElementById('replay'),pending=document.getElementById('film-pending');
let sources=[];
const remember=()=>{try{sessionStorage.setItem('ledgerpoint-intro-seen','1')}catch{}};
async function checkSource(file){try{const r=await fetch('assets/'+file,{method:'HEAD',cache:'no-store'});return r.ok&&(r.headers.get('content-type')||'').toLowerCase().includes('video')}catch{return false}}
function unavailable(){video.hidden=true;poster.hidden=false;load.hidden=true;qualityWrap.hidden=true;pending.hidden=false;status.textContent='The film is being produced separately. Explore LedgerPoint now or read the narration below.'}
async function discover(){const files=['ledgerpoint-intro-1080p.mp4','ledgerpoint-intro-web.mp4'];const results=await Promise.all(files.map(checkSource));sources=files.filter((_,i)=>results[i]);if(!sources.length){unavailable();return}quality.replaceChildren(...sources.map(file=>{const o=document.createElement('option');o.value=file;o.textContent=file.includes('1080p')?'1080p':'Web';return o}));qualityWrap.hidden=sources.length<2;load.hidden=false;load.disabled=false;load.textContent='Play the film';pending.hidden=true;status.textContent='The film is ready. Select Play the film to watch.'}
async function play(){const file=quality.value;if(!sources.includes(file))return;video.src='assets/'+file;video.hidden=false;poster.hidden=true;try{await video.play();status.textContent='Use the player controls to pause, seek, mute or enable captions.'}catch{status.textContent='Press play in the video player to begin.'}}
load.addEventListener('click',play);quality.addEventListener('change',()=>{video.pause();video.removeAttribute('src');video.load();video.hidden=true;poster.hidden=false;load.hidden=false;status.textContent='Select Play the film to load this version.'});
video.addEventListener('error',()=>{poster.hidden=false;video.hidden=true;status.textContent='Playback could not start. You can still explore LedgerPoint below.';load.hidden=false;load.textContent='Retry playback'});
video.addEventListener('ended',()=>{remember();replay.hidden=false;status.textContent='Film complete. Enter LedgerPoint to explore the demonstration.'});
replay.addEventListener('click',()=>{video.currentTime=0;video.play().catch(()=>{status.textContent='Press play in the video controls to replay.'})});
document.getElementById('enter').addEventListener('click',remember);
fetch('assets/ledgerpoint-intro-transcript.txt').then(r=>{if(!r.ok)throw Error();return r.text()}).then(t=>{document.getElementById('transcript').textContent=t}).catch(()=>{document.getElementById('transcript').textContent='Transcript temporarily unavailable.'});
discover();
})();