"""Protótipo: régua vertical no computador (no celular continua a horizontal). Uso: python3 proto_regua.py arquivo.html"""
import sys
p = sys.argv[1]
s = open(p).read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


CSS = r"""
/* régua vertical (computador): régua de verdade + frequência + marcos */
.vgauge,.nav-hint2{display:none}
@media (min-width:821px){
  .timeline{display:none}
  .vgauge{display:grid;grid-template-rows:auto 1fr auto;gap:10px;top:calc(196px + env(safe-area-inset-top,0px));bottom:calc(20px + env(safe-area-inset-bottom,0px));right:max(24px,env(safe-area-inset-right,0px));width:264px;border-radius:var(--r);padding:14px 12px 12px 14px;box-sizing:border-box}
  .card{right:calc(max(24px,env(safe-area-inset-right,0px)) + 276px)}
  .legend{max-height:calc(100% - 272px)}
  .nav-hint2{display:block;bottom:calc(20px + env(safe-area-inset-bottom,0px));left:50%;transform:translateX(-50%);padding:5px 12px;border-radius:999px;font-size:12px;color:var(--muted);white-space:nowrap}
}
.vg-head{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:center}
.vg-head .play{width:36px;height:36px}
.vg-head .play svg{width:13px;height:13px}
.vg-head b{display:block;font-family:var(--f-display);font-size:16px;font-weight:700;letter-spacing:-.02em;line-height:1.15}
.vg-head span{display:block;font-size:11.5px;color:var(--muted);line-height:1.3}
#vg{display:block;width:100%;height:100%;min-height:0;touch-action:none;cursor:ns-resize;outline:none}
#vg:focus-visible{box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 45%,transparent);border-radius:10px}
.vg-key{margin:0;font-size:11.5px;color:var(--muted);line-height:1.4}
.vg-key i{display:inline-block;width:10px;height:26px;border-radius:2px;float:left;margin:2px 8px 0 0;background:linear-gradient(to top,var(--water),color-mix(in srgb,var(--water) 8%,transparent))}
"""
rep("@media (prefers-reduced-motion: reduce)", CSS + "@media (prefers-reduced-motion: reduce)")

HTML = """
  <div class="ui vgauge glass" id="vgauge">
    <div class="vg-head">
      <button class="play" id="play2" type="button" aria-label="Encher: subir a régua até a maior cheia"><svg viewBox="0 0 16 16" aria-hidden="true"><path id="playIco2" d="M4.5 2.6v10.8c0 .6.7 1 1.2.7l8.4-5.4a.8.8 0 000-1.4L5.7 1.9c-.5-.3-1.2.1-1.2.7z" fill="currentColor"></path></svg></button>
      <div><b id="vgTitle">Régua</b><span>Arraste para subir ou descer a água. Clique num marco para ir até ele.</span></div>
    </div>
    <canvas id="vg" role="slider" tabindex="0" aria-orientation="vertical" aria-label="Régua do rio: arraste para escolher o nível"></canvas>
    <p class="vg-key" id="vgKey"></p>
  </div>
  <span class="ui nav-hint2 glass cityui">Arraste para girar · botão direito ou Shift para inclinar · role para aproximar</span>
"""
rep('  <aside class="ui card glass" id="card" hidden aria-live="polite"></aside>', HTML + '  <aside class="ui card glass" id="card" hidden aria-live="polite"></aside>')

# play: os dois botões mostram o mesmo ícone
s = s.replace("document.getElementById('playIco').setAttribute('d',", "setIco(")
rep("function stop(){", "function setIco(d){ for(const id of ['playIco','playIco2']){ const el=document.getElementById(id); if(el) el.setAttribute('d',d); } }\nfunction stop(){")
rep("document.querySelectorAll('.modes button').forEach(b=>b.addEventListener('click',async()=>{",
    "document.getElementById('play2').addEventListener('click',()=>document.getElementById('play').click());\n"
    "document.querySelectorAll('.modes button').forEach(b=>b.addEventListener('click',async()=>{")

# desenhar a régua vertical sempre que a horizontal é desenhada
rep("function drawHist(){\n", "function drawHist(){\n  drawVG();\n")

JS = r"""
/* ---------- régua vertical ---------- */
const vg=document.getElementById('vg');
var vgLabels=[];
function vgY(h,H){ return 14+(HMAX-h)/(HMAX-HMIN)*(H-28); }
function vgH(y,H){ return HMAX-(y-14)/(H-28)*(HMAX-HMIN); }
function plain(t){ const d=document.createElement('div'); d.innerHTML=t; const f=d.querySelector('.full'); return (f?f.textContent:d.textContent).trim(); }
function vgMarks(){
  const out=[], near=h=>out.some(o=>Math.abs(o.h-h)<.06);
  for(const e of EVENTS){ const t=plain(e.t).replace(/^[\d.,]+ ?m · /,''); out.push({h:e.h,t,k:/onset/.test(e.c||'')||/cota/.test(t)?'quota':'event'}); }
  for(const q of (K.quotas||[])) if(!near(q.h)) out.push({h:q.h,t:q.t,k:'quota'});
  const first=(list,t)=>{ const v=list.filter(p=>p.s<25).map(p=>gH(p.s)); if(!v.length) return; const h=Math.min(...v); if(h>=HMIN&&h<=HMAX) out.push({h,t,k:'hit'}); };
  first(schools,'1ª escola alcançada'); first(hosps,'1º hospital alcançado');
  const am=YEARS.map(y=>D.annmax[y]).sort((a,b)=>b-a), q=f=>am[Math.max(0,Math.ceil(f*NY)-1)];
  const add=(h,t)=>{ if(h>=HMIN&&h<=HMAX&&!near(h)) out.push({h,t,k:'freq'}); };
  add(q(.5),'metade dos anos'); add(q(.1),'1 em cada 10 anos');
  return out.sort((a,b)=>b.h-a.h);
}
function drawVG(){
  const vg=document.getElementById('vg'); if(!vg||!D) return; const r=vg.getBoundingClientRect(); if(!r.width||!r.height) return;
  const dpr=Math.min(2,devicePixelRatio||1); vg.width=Math.round(r.width*dpr); vg.height=Math.round(r.height*dpr);
  const x=vg.getContext('2d'); x.scale(dpr,dpr); const W=r.width, H=r.height, Y=h=>vgY(h,H);
  const ink=css('--ink'), muted=css('--muted'), hit=css('--hit'), obs=css('--obs'), plate=css('--block'), panel=css('--panel-solid');
  const wr=rgb(css('--water')).join(','), fw=11, sx=17, sw=30, lx=sx+sw+12, cur=gH(level), yl=Y(cur);
  document.getElementById('vgTitle').textContent='Régua de '+K.gauge;
  document.getElementById('vgKey').innerHTML=`<i></i>Faixa à esquerda: em quantos anos o rio chegou a cada altura (${YEARS[0]}–${YEARS[NY-1]}). Escuro, quase todo ano; claro, raro.`;
  vg.setAttribute('aria-valuemin',HMIN); vg.setAttribute('aria-valuemax',HMAX); vg.setAttribute('aria-valuenow',cur.toFixed(2)); vg.setAttribute('aria-valuetext',fmt(cur,2)+' metros na régua');
  // frequência: fração dos anos em que o máximo anual chegou a cada altura
  for(let h=HMIN;h<HMAX-1e-9;h+=.1){ const sh=freq(h+.05).length/NY;
    x.fillStyle=`rgba(${wr},${(.05+.9*Math.pow(sh,.55)).toFixed(3)})`; x.fillRect(0,Y(h+.1),fw,Y(h)-Y(h+.1)+.6); }
  // placa da régua
  x.fillStyle=plate; x.beginPath(); x.roundRect?x.roundRect(sx,Y(HMAX)-6,sw,Y(HMIN)-Y(HMAX)+12,5):x.rect(sx,Y(HMAX)-6,sw,Y(HMIN)-Y(HMAX)+12); x.fill();
  x.strokeStyle='rgba(0,0,0,.12)'; x.lineWidth=.5; x.stroke();
  for(let i=Math.ceil(HMIN*10);i<=Math.round(HMAX*10);i++){ const y=Y(i/10), m=i%10===0, hf=i%5===0;
    if(!m&&!hf&&Y(0)-Y(.1)<4.5) continue;
    x.fillStyle=ink; x.fillRect(sx+3,y-.75,m?sw-6:hf?sw*.55:sw*.3,m?2:1.5);
    if(m&&i/10<HMAX){ x.fillStyle=hit; x.font='700 12px '+getComputedStyle(document.body).fontFamily; x.textAlign='right'; x.textBaseline='bottom'; x.fillText(String(i/10),sx+sw-4,y-2); } }
  // água
  x.fillStyle=`rgba(${wr},.32)`; x.fillRect(sx,yl,sw,Y(HMIN)+6-yl);
  // marcos à direita, sem sobreposição
  const ms=vgMarks(), gap=15; let ys=ms.map(m=>Y(m.h));
  for(let i=1;i<ys.length;i++) ys[i]=Math.max(ys[i],ys[i-1]+gap);
  const lim=H-6; if(ys.length&&ys[ys.length-1]>lim){ ys[ys.length-1]=lim; for(let i=ys.length-2;i>=0;i--) ys[i]=Math.min(ys[i],ys[i+1]-gap); }
  vgLabels=[]; x.textAlign='left'; x.textBaseline='middle';
  const font=getComputedStyle(document.body).fontFamily;
  ms.forEach((m,i)=>{ const y0=Y(m.h), y=ys[i], col=m.k==='hit'?hit:m.k==='quota'?obs:m.k==='freq'?muted:ink;
    x.globalAlpha=1;
    x.strokeStyle=col; x.lineWidth=1; x.beginPath(); x.moveTo(sx+sw,y0); x.lineTo(lx-6,y0); x.lineTo(lx-2,y); x.stroke();
    x.fillStyle=col; x.font=(m.k==='event'?'600 ':m.k==='freq'?'italic 400 ':'500 ')+'11.5px '+font;
    let t=(Math.round(m.h*100)/100).toLocaleString('pt-BR',{maximumFractionDigits:2})+' m · '+m.t, mw=W-lx-2;
    while(x.measureText(t).width>mw&&t.length>4) t=t.slice(0,-2)+'…';
    x.fillText(t,lx,y); x.globalAlpha=1; vgLabels.push({y,h:m.h}); });
  // nível atual
  x.fillStyle=ink; x.fillRect(0,yl-1,lx-4,2);
  x.beginPath(); x.arc(sx+sw/2,yl,7,0,7); x.fillStyle=ink; x.fill(); x.lineWidth=2.5; x.strokeStyle=plate; x.stroke();
}
let vdrag=false;
const fromY=e=>{ const r=vg.getBoundingClientRect(); return vgH(e.clientY-r.top,r.height)-R0; };
vg.addEventListener('pointerdown',e=>{ stop(); const r=vg.getBoundingClientRect(), px=e.clientX-r.left, py=e.clientY-r.top;
  if(px>56){ const m=vgLabels.find(l=>Math.abs(l.y-py)<8); if(m){ setLevel(m.h-R0,true); return; } }
  vdrag=true; vg.setPointerCapture(e.pointerId); setLevel(fromY(e)); });
vg.addEventListener('pointermove',e=>{ if(vdrag) setLevel(fromY(e)); });
vg.addEventListener('pointerup',()=>{ vdrag=false; });
vg.addEventListener('keydown',e=>{ if(/^(Arrow|Page|Home|End)/.test(e.key)){ e.preventDefault(); hc.dispatchEvent(new KeyboardEvent('keydown',{key:e.key})); } });
new ResizeObserver(()=>drawVG()).observe(vg);
"""
rep("new ResizeObserver(drawHist).observe(hc);", "new ResizeObserver(drawHist).observe(hc);\n" + JS)
open(p, 'w').write(s)
print('ok', p)
