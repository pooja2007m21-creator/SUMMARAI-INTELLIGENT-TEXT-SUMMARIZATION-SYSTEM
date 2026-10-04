(async()=>{
  try{
    const s=await api("/api/stats");
    $("#kpis").innerHTML=[["Total summaries",s.total_summaries],["Words processed",s.total_words.toLocaleString()],["Average summary length",s.avg_summary_length+" words"],["Average compression",s.avg_compression+"%"]]
      .map(([a,b])=>`<div class="stat"><span class="meta">${a}</span><b>${b}</b></div>`).join("");
    if(!s.total_summaries){$("#empty").hidden=false;return}
    const css=getComputedStyle(document.documentElement),acc=css.getPropertyValue("--acc").trim();
    new Chart($("#c1"),{type:"line",data:{labels:s.over_time.map(r=>r.date),datasets:[{label:"Summaries",data:s.over_time.map(r=>r.count),borderColor:acc,backgroundColor:acc+"33",fill:true,tension:.3}]},options:{scales:{y:{beginAtZero:true,ticks:{precision:0}}}}});
    const t=["short","medium","detailed"];
    new Chart($("#c2"),{type:"doughnut",data:{labels:t,datasets:[{data:t.map(k=>s.by_type[k]||0),backgroundColor:["#0f766e","#d97706","#475569"]}]}});
  }catch(e){$("#kpis").innerHTML=`<p class="msg err">${esc(e.message)}</p>`}
})();
