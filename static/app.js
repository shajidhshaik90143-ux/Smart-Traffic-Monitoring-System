function $(id){return document.getElementById(id)}
async function api(url,options){const r=await fetch(url,options);if(!r.ok)throw new Error(await r.text());return r.json()}

function setDensity(v){
  const e=$("density");e.textContent=v;e.className="density "+v.toLowerCase();
  $("densityText").textContent=v;
  $("densityBar").style.width=({LOW:15,MEDIUM:40,HIGH:70,SEVERE:100}[v]||10)+"%";
}
function setBar(id,value,max){$(id).style.width="0px";}

async function refresh(){
  try{
    const st=await api("/api/status");
    $("systemStatus").textContent=st.running?"● Detection running":"○ Detection stopped";
    $("systemStatus").style.color=st.running?"#86efac":"#fbbf24";
    $("errorStatus").textContent=st.error||"";
    const s=await api("/api/traffic/current");
    ["total","cars","motorcycles","buses","trucks"].forEach(k=>$(k).textContent=s[k]);
    $("barCars").textContent=s.cars;$("barBikes").textContent=s.motorcycles;
    $("barBuses").textContent=s.buses;$("barTrucks").textContent=s.trucks;
    setDensity(s.density);
    $("congestion").textContent=s.congestion?"YES":"NO";
    $("congestion").style.color=s.congestion?"#fca5a5":"#86efac";
    $("updated").textContent=s.timestamp||"—";
    $("cameraMessage").style.display=st.has_frame?"none":"block";
    if(st.has_frame)$("video").src="/video_feed?t="+Date.now();
  }catch(e){$("systemStatus").textContent="Backend unavailable";$("errorStatus").textContent=e.message}
}
async function loadAlerts(){
  const a=await api("/api/alerts?limit=20"),box=$("alerts");
  box.innerHTML=a.length?a.map(x=>`<div class="alert-item"><b>${esc(x.alert_type)} — ${esc(x.severity)}</b><div>${esc(x.message)}</div><small>${esc(x.timestamp)}</small></div>`).join(""):"<p>No alerts yet.</p>";
}
async function loadHistory(){
  const r=await api("/api/traffic/history?limit=30");
  $("history").innerHTML=r.map(x=>`<tr><td>${esc(x.timestamp)}</td><td>${x.total}</td><td>${x.cars}</td><td>${x.motorcycles}</td><td>${x.buses}</td><td>${x.trucks}</td><td>${esc(x.density)}</td></tr>`).join("");
}
async function startDetection(){await api("/api/detection/start",{method:"POST"});refresh()}
async function stopDetection(){await api("/api/detection/stop",{method:"POST"});refresh()}
function esc(v){return String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
setInterval(refresh,2000);setInterval(loadAlerts,5000);setInterval(loadHistory,7000);
refresh();loadAlerts();loadHistory();
