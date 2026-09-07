"use strict";
document.documentElement.classList.add("js-enabled");
const a=document.getElementById("support-a"),b=document.getElementById("support-b"),out=document.getElementById("support-status");
if(a&&b&&out){const update=()=>{const count=Number(a.checked)+Number(b.checked);out.textContent=count===2?"Conclusion supported through both A and B.":count===1?"Conclusion remains supported through "+(a.checked?"A":"B")+". No reopening is required.":"Conclusion has lost all support and must reopen. Unsupported does not mean false.";};a.addEventListener("change",update);b.addEventListener("change",update);document.getElementById("support-reset").addEventListener("click",()=>{a.checked=true;b.checked=true;update();});update();}
