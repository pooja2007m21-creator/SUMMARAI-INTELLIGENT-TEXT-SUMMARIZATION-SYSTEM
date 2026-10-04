const ed=$("#text"),out=$("#out");let last=null;
const wc=t=>(t.match(/\b[\w'-]+\b/g)||[]).length, sc=t=>(t.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[]).filter(s=>s.trim()).length;
function counts(){const t=ed.value;$("#counts").textContent=`${wc(t)} words · ${t.length} characters · ${sc(t)} sentences`}
ed.addEventListener("input",counts);counts();
function msg(t,k){const m=$("#msg");m.className="msg "+(k||"");m.textContent=t}
$("#go").onclick=async()=>{
  msg("");$("#bar").classList.add("on");$("#go").disabled=true;$("#go").textContent="Summarizing…";
  try{
    const d=await api("/api/summarize",{method:"POST",body:JSON.stringify({title:$("#title").value,text:ed.value,length:$("#length").value,mode:$("#mode").value})});
    last=d;out.className="card out";out.textContent=d.summary;
    msg(d.status+(d.note?" "+d.note:""),"ok");
    const ow=d.original_words,sw=d.summary_words;
    $("#stats").innerHTML=[["Original words",ow],["Summary words",sw],["Compression",d.compression+"%"],["Sentences selected",d.summary_sentences+" of "+d.original_sentences],["Method",d.mode],["Time",d.seconds+" s"]]
      .map(([a,b])=>`<div class="stat"><span class="meta">${a}</span><b>${esc(b)}</b></div>`).join("");
    $("#kw").innerHTML=d.keywords.length?"Key terms: "+d.keywords.map(k=>`<span>${esc(k)}</span>`).join(""):"";
    $("#compare").hidden=false;
    $("#compare tbody").innerHTML=`<tr><td>Original content</td><td>${ow}</td><td>${d.original_sentences}</td></tr><tr><td>Summary</td><td>${sw}</td><td>${d.summary_sentences}</td></tr>`;
  }catch(e){msg(e.message,"err")}
  finally{$("#bar").classList.remove("on");$("#go").disabled=false;$("#go").textContent="Summarize"}
};
$("#clear").onclick=()=>{ed.value="";$("#title").value="";out.className="card out empty";out.textContent="Your summary will appear here.";$("#stats").innerHTML="";$("#kw").innerHTML="";$("#compare").hidden=true;msg("");last=null;counts()};
$("#copy").onclick=()=>last?copyText(last.summary):toast("Generate a summary first");
$("#dl").onclick=()=>last?download($("#title").value||"summary",last.summary):toast("Generate a summary first");
