"""Régua do celular: régua de verdade deitada, faixa de frequência, leitura em palavras ("raro") e botões −/+.
Também acrescenta a mesma leitura na régua vertical do computador. Uso: python3 regua_celular.py site/index.html"""
import sys
p = sys.argv[1]
s = open(p).read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep("@media (prefers-reduced-motion: reduce)", r""".tl-read{display:flex;align-items:center;gap:8px;margin-top:6px;font-size:12.5px;line-height:1.3;color:var(--muted)}
.tl-read b,.vg-read b{color:var(--ink);font-weight:650}
.steps{margin-left:auto;display:flex;gap:6px;flex:none}
.steps button{width:34px;height:30px;border-radius:999px;background:var(--fill);color:var(--ink);font-size:18px;font-weight:600;line-height:1;display:grid;place-items:center}
.steps button:active{background:var(--fill-hover)}
.tl-key{margin:4px 0 0;font-size:11px;color:var(--muted)}
@media (min-width:821px){.tl-key{display:none}}
.vg-read{margin:0;font-size:12.5px;line-height:1.35;color:var(--muted)}
#hist{height:60px}
.ticks{display:none}
.vgauge{grid-template-rows:auto 1fr auto auto}
@media (prefers-reduced-motion: reduce)""")

rep('      <div class="ticks" id="ticks"></div>\n',
    '      <div class="ticks" id="ticks"></div>\n'
    '      <div class="tl-read"><span id="tlRead"></span><span class="steps"><button type="button" id="stepDn" aria-label="Descer 10 centímetros">−</button><button type="button" id="stepUp" aria-label="Subir 10 centímetros">+</button></span></div>\n'
    '      <p class="tl-key">Faixa azul: quanto mais escura, em mais anos o rio chegou àquela altura.</p>\n')
rep('    <p class="vg-key" id="vgKey"></p>', '    <p class="vg-read" id="vgRead"></p>\n    <p class="vg-key" id="vgKey"></p>')

# chips das cheias alinhados com a régua (margem de 6 px nos dois lados do desenho)
rep("""style="left:${((e.h-HMIN)/(HMAX-HMIN)*100).toFixed(2)}%\"""",
    """style="left:calc(6px + ${((e.h-HMIN)/(HMAX-HMIN)).toFixed(4)} * (100% - 12px))\"""")

a = s.index("function drawHist(){"); b = s.index("let raf=0;")
s = s[:a] + r"""/* régua do celular: a régua deitada, com a frequência por cima e a água entrando da esquerda */
const hX=(h,W)=>6+(h-HMIN)/(HMAX-HMIN)*(W-12);
function drawHist(){
  drawVG(); updateRead();
  const r=hc.getBoundingClientRect(), dpr=Math.min(2,devicePixelRatio||1); if(!r.width) return;
  hc.width=Math.round(r.width*dpr); hc.height=Math.round(r.height*dpr);
  const x=hc.getContext('2d'); x.scale(dpr,dpr); const W=r.width, H=r.height, X=h=>hX(h,W);
  const ink=css('--ink'), hit=css('--hit'), muted=css('--muted'), plate=css('--block'), wr=rgb(css('--water')).join(',');
  const font=getComputedStyle(document.body).fontFamily, fb=10, sy=fb+5, sh=H-sy-2, cur=gH(level), xl=X(cur);
  for(let h=HMIN;h<HMAX-1e-9;h+=.1){ const f=freq(h+.05).length/NY;
    x.fillStyle=`rgba(${wr},${(.05+.9*Math.pow(f,.55)).toFixed(3)})`; x.fillRect(X(h),0,X(h+.1)-X(h)+.6,fb); }
  x.fillStyle=plate; x.beginPath(); x.roundRect?x.roundRect(X(HMIN)-4,sy,X(HMAX)-X(HMIN)+8,sh,5):x.rect(X(HMIN)-4,sy,X(HMAX)-X(HMIN)+8,sh); x.fill();
  x.strokeStyle='rgba(0,0,0,.12)'; x.lineWidth=.5; x.stroke();
  for(let i=Math.ceil(HMIN*10);i<=Math.round(HMAX*10);i++){ const h=i/10, m=i%10===0, hf=i%5===0;
    if(!m&&!hf&&X(.1)-X(0)<4.5) continue;
    x.fillStyle=ink; x.fillRect(X(h)-.75,sy+2,m?2:1.5,m?sh-4:hf?sh*.5:sh*.3);
    if(m&&h<HMAX){ x.fillStyle=hit; x.font='700 12px '+font; x.textAlign='left'; x.textBaseline='alphabetic'; x.fillText(String(h),X(h)+3,sy+sh-5); } }
  x.fillStyle=muted; x.globalAlpha=.5; for(const e of EVENTS) x.fillRect(X(e.h)-.5,0,1,fb+3); x.globalAlpha=1;
  x.fillStyle=`rgba(${wr},.32)`; x.fillRect(X(HMIN)-4,sy,xl-X(HMIN)+4,sh);
  x.fillStyle=ink; x.fillRect(xl-1,0,2,H);
  x.beginPath(); x.arc(xl,sy+sh/2,7.5,0,7); x.fill(); x.lineWidth=2.5; x.strokeStyle=plate; x.stroke();
}
/* leitura em palavras: com que frequência o rio chegou a este nível */
function updateRead(){
  if(!D) return; const H=gH(level), n=freq(H).length, f=n/NY;
  const w=n===0?'Nunca medido':f>=1/3?'Comum':f>=.1?'Pouco comum':'Raro';
  const t=n?`<b>${w}</b> · o rio chegou aqui em ${n} de ${NY} anos`:`<b>${w}</b> · acima de tudo o que a régua mediu desde ${YEARS[0]}`;
  for(const id of ['tlRead','vgRead']){ const el=document.getElementById(id); if(el) el.innerHTML=t; }
}
""" + s[b:]

rep("const fromX=e=>{ const r=hc.getBoundingClientRect(); return LMIN+(e.clientX-r.left)/r.width*(LMAX-LMIN); };",
    "const fromX=e=>{ const r=hc.getBoundingClientRect(); return LMIN+(e.clientX-r.left-6)/(r.width-12)*(LMAX-LMIN); };\n"
    "const step=d=>{ stop(); setLevel(Math.round((gH(level)+d)*10)/10-R0,true); };\n"
    "document.getElementById('stepDn').addEventListener('click',()=>step(-.1));\n"
    "document.getElementById('stepUp').addEventListener('click',()=>step(.1));")
open(p, 'w').write(s)
print('ok', p)
