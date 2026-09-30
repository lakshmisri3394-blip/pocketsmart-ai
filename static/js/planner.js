const form=document.getElementById("plannerForm");
if(form){
 form.addEventListener("submit",async(e)=>{
  e.preventDefault();
  const loading=document.getElementById("loading"), result=document.getElementById("result");
  loading.classList.remove("hidden"); result.innerHTML="";
  try{
   const response=await fetch(form.dataset.endpoint,{method:"POST",body:new FormData(form)});
   const data=await response.json();
   if(!response.ok) throw new Error(data.detail||"Request failed");
   renderResult(data,result);
  }catch(err){
   result.innerHTML=`<div class="result-box error">${escapeHtml(err.message)}</div>`;
  }finally{loading.classList.add("hidden")}
 });
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));}
function renderResult(data,root){
 let html=`<div class="result-box"><p class="eyebrow">AI RECOMMENDATION</p><h2>${escapeHtml(data.summary||"Your personalized plan")}</h2>`;
 if(data.budget_breakdown?.length){
  html+=`<h3>Budget Breakdown</h3><div class="breakdown">`;
  data.budget_breakdown.forEach(x=>html+=`<div class="break"><strong>${escapeHtml(x.category)}</strong><br>₹${Number(x.amount||0).toLocaleString("en-IN")}</div>`);
  html+=`</div>`;
 }
 html+=`<h3>Recommendations</h3><div class="recommendations">`;
 (data.recommendations||[]).forEach(x=>{
  html+=`<div class="rec"><h3>${escapeHtml(x.item||"Recommendation")}</h3><p>${escapeHtml(x.reason||"")}</p><div class="price">₹${Number(x.estimated_price||0).toLocaleString("en-IN")} <small>estimated</small></div>${x.search_link?`<p><a target="_blank" rel="noopener" href="${x.search_link}">Search on ${escapeHtml(x.platform||"platform")} →</a></p>`:""}</div>`;
 });
 html+=`</div></div>`;
 root.innerHTML=html;
}