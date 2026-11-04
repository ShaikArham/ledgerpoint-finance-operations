(() => {
"use strict";
const names={guide:"Start here",overview:"Executive overview",reconciliation:"Bank reconciliation",invoices:"Invoice register",performance:"Financial performance","case-study":"Case study","investigation-lab":"Investigation lab",about:"About & application"};
const pages=new Set(["guide","overview","investigation-lab","reconciliation","invoices","performance","case-study","about"]);
const views=Array.from(document.querySelectorAll(".view"));
const links=Array.from(document.querySelectorAll("[data-view]"));
const reduce=()=>window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function navigate(name,scroll=true){
 const target=names[name]?name:"overview";
 const page=target;
 views.forEach(el=>{const active=el.id===page;el.classList.toggle("active",active);el.hidden=!active;});const hero=document.querySelector(".hero");if(hero)hero.hidden=page!=="overview";
 links.forEach(a=>{const active=a.dataset.view===page;a.classList.toggle("active",active);if(a.closest("nav")){if(active)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current");}});
 document.title="LedgerPoint | "+names[target];
 if(scroll){requestAnimationFrame(()=>{const node=document.getElementById(target);if(node)node.scrollIntoView({behavior:reduce()?"auto":"smooth",block:"start"});});}
}
function current(){const hash=decodeURIComponent(location.hash.slice(1));return names[hash]?hash:"overview";}
document.addEventListener("click",event=>{
 const anchor=event.target.closest('a[href^="#"]');
 if(!anchor)return;
 const id=decodeURIComponent(anchor.getAttribute("href").slice(1));
 if(!names[id])return;
 event.preventDefault();
 if(location.hash!=="#"+id){history.pushState(null,"","#"+id);}
 navigate(id,true);
});
window.addEventListener("popstate",()=>navigate(current(),true));
window.addEventListener("hashchange",()=>navigate(current(),true));
navigate(current(),Boolean(location.hash));
})();

(()=>{"use strict";const root=document.getElementById("investigation-lab");if(!root)return;const $=id=>document.getElementById(id);const records={receipt:"Customer receipt +€500: a corresponding ledger payment allocation is present. Matched.",supplier:"Supplier settlement −€369: a corresponding payment is present. Matched.",unknown:"Unclassified bank debit −€12: no matching ledger entry or supporting explanation. Investigation required."};let current="unknown",history=[];function log(t){history.unshift(t);$("lab-log").replaceChildren(...history.slice(0,5).map(s=>{const li=document.createElement("li");li.textContent=s;return li}))}function figures(profit="€700",cash="€131",open="1",status="Under review"){$("lab-profit").textContent=profit;$("lab-cash").textContent=cash;$("lab-open").textContent=open;$("lab-status").textContent=status}function choose(k){current=k;root.querySelectorAll("[data-txn]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.txn===k)));$("lab-evidence").textContent=records[k];$("lab-type").value="unknown";$("lab-proof").checked=false;figures();$("lab-result").textContent=k==="unknown"?"No confirmed explanation. Test a hypothesis or keep it under review.":"Already matched. No adjustment is required.";log("Inspected "+k+" transaction.")}root.querySelectorAll("[data-txn]").forEach(b=>b.addEventListener("click",()=>choose(b.dataset.txn)));$("lab-preview").addEventListener("click",()=>{if(current!=="unknown"){$("lab-result").textContent="This item is matched. No correction is needed.";return}const type=$("lab-type").value,proof=$("lab-proof").checked;const desc={unknown:"Still unidentified. Request evidence before classification.",fee:"If this were a new bank fee, illustrative profit could be €688 instead of €700.",supplier:"A new supplier expense might reduce profit to €688, while settlement of an existing payable would not. Investigate first.",duplicate:"A possible duplicate requires statement verification and any reversal evidence. No automatic offset is justified."};$("lab-result").textContent=desc[type]+(proof?" The checkbox cannot verify the documents. Nothing has been posted.":" No supporting documentation has been provided.");figures(type==="fee"?"€688*":"€700","€131","1","Preview only");log("Tested "+type+" hypothesis. No posting.");});$("lab-hold").addEventListener("click",()=>{$("lab-result").textContent="The €12 remains unresolved. Obtain bank evidence and assign an investigation owner before deciding whether to post.";figures();log("Kept exception under review.")});$("lab-reset").addEventListener("click",()=>{history=[];choose("unknown");log("Scenario reset.")});choose("unknown");})();