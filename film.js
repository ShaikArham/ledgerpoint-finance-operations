(()=>{'use strict';
const video=document.getElementById('film'),poster=document.getElementById('poster'),status=document.getElementById('status'),quality=document.getElementById('quality'),load=document.getElementById('load'),replay=document.getElementById('replay');
let available=false;
const remember=()=>{try{sessionStorage.setItem('ledgerpoint-intro-seen','1')}catch{}};
const fail=()=>{available=false;poster.hidden=false;load.disabled=false;load.textContent='Retry film';status.textContent='The film is unavailable. You can read the complete narration or enter LedgerPoint below.'};
async function start(){
 load.disabled=true;status.textContent='Checking film availability…';
 const src=`assets/ledgerpoint-intro-${quality.value}.mp4`;
 try{const r=await fetch(src,{method:'HEAD'});if(!r.ok||!(r.headers.get('content-type')||'').startsWith('video/'))throw Error('Unavailable');video.src=src;available=true;poster.hidden=true;load.disabled=false;video.load();await video.play();status.textContent='Use the video controls to pause, seek, mute or enable English captions.'}catch(e){if(available){status.textContent='Press play in the video controls to start.'}else fail()}
}
load.addEventListener('click',start);video.addEventListener('error',fail);
video.addEventListener('ended',()=>{remember();replay.hidden=false;status.textContent='Film complete. Enter LedgerPoint to explore the demonstration.';document.getElementById('enter').focus()});
replay.addEventListener('click',()=>{video.currentTime=0;video.play().catch(()=>{status.textContent='Press play to replay the film.'})});
quality.addEventListener('change',()=>{if(available){video.pause();available=false;poster.hidden=false;status.textContent='Press Check film availability to load the selected quality.';load.textContent='Load selected quality'}});
document.getElementById('enter').addEventListener('click',remember);
fetch('assets/ledgerpoint-intro-transcript.txt').then(r=>{if(!r.ok)throw Error();return r.text()}).then(t=>{document.getElementById('transcript').textContent=t}).catch(()=>{document.getElementById('transcript').textContent='Use the download link to open the transcript.'});
})();
