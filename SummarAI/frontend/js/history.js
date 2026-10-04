let type="",timer;const list=$("#list"),dlg=$("#dlg");
async function load(){
  try{const d=await api(`/api/history?q=${encodeURIComponent($("#q").value)}&type=${type}`);
    list.innerHTML=d.items.length?d.items.map(i=>`<article class="card"><div class="row sp"><h3>${esc(i.title)}</h3><span class="meta">${esc(i.summary_type)} · ${i.original_word_count}→${i.summary_word_count} words · ${esc(i.created_at)}</span></div>
      <p>${esc(i.summary.length>280?i.summary.slice(0,280)+"…":i.summary)}</p>
      <div class="row"><button class="btn" data-a="view" data-id="${i.id}">View</button><button class="btn" data-a="copy" data-id="${i.id}">Copy</button><button class="btn danger" data-a="del" data-id="${i.id}">Delete</button></div></article>`).join("")
      :`<p class="meta">No summaries found. <a href="/summarize">Create one</a>.</p>`}
  catch(e){list.innerHTML=`<p class="msg err">${esc(e.message)}</p>`}
}
list.onclick=async e=>{const b=e.target.closest("button");if(!b)return;const id=b.dataset.id;
  try{
    if(b.dataset.a==="del"){if(!confirm("Delete this summary permanently?"))return;await api("/api/history/"+id,{method:"DELETE"});toast("Deleted");load()}
    else{const r=await api("/api/history/"+id);
      if(b.dataset.a==="copy")copyText(r.summary);
      else{$("#dt").textContent=r.title;$("#dm").textContent=`${r.summary_type} · ${r.original_word_count}→${r.summary_word_count} words`;$("#ds").textContent=r.summary;$("#do").textContent=r.original_text;dlg.showModal()}}
  }catch(err){toast(err.message)}};
$("#q").oninput=()=>{clearTimeout(timer);timer=setTimeout(load,250)};
document.querySelectorAll("[data-type]").forEach(b=>b.onclick=()=>{type=b.dataset.type;document.querySelectorAll("[data-type]").forEach(x=>x.setAttribute("aria-pressed",x===b));load()});
$("#close").onclick=()=>dlg.close();load();
