const REPO = 'https://github.com/brunnojob/github-notification-autofix';
const copy = {
  en: {
    language: 'Language', source: 'Source code ↗', badge: 'Interactive demo', eyebrow: 'GITHUB NOTIFICATION AUTOFIX',
    title: 'From a failed check<br>to a <span>verified fix.</span>',
    lead: 'Follow one notification through diagnosis, a focused patch and independent verification. See why a fix is only finished when the checks agree.',
    noteTitle: 'Reproducible, not a live agent.', note: 'Replay of Python test scenarios. No login, tokens or changes to your repositories.',
    scenario: 'Scenario', scenarios: {success: 'Successful repair', pending: 'Checks still running', race: 'Branch changed during repair', permission: 'No write permission'},
    play: 'Play recording', pause: 'Pause', resume: 'Resume', reset: 'Reset', next: 'Next step', replay: 'Replay',
    pipeline: 'REPAIR WORKFLOW', ready: 'Ready', waiting: 'Waiting', success: 'Passed', blocked: 'Blocked',
    steps: {scan:'Read notification',diagnose:'Confirm the problem',repair:'Apply focused patch',test:'Run local tests',publish:'Publish change',verify:'Verify latest checks',done:'Mark notification Done'},
    local: 'Recorded fixture · GitHub and Codex are stubbed. No external writes.',
    notificationTitle: 'Python tests failed: incorrect checkout total', notificationNote: 'Fixture notification · 3 unit tests fail on the original function.',
    recorded: 'RECORDED FIXTURE', verified: 'DONE VERIFIED', open: 'KEPT OPEN',
    tabs: {diff:'Patch', before:'Before', after:'After'}, files:'1 file · 1 addition · 1 deletion',
    lockedTitle: 'The patch appears after the repair step.', locked: 'Start playback or advance one step at a time to inspect the recorded decision flow.',
    noPatchTitle: 'No repair attempted.', noPatch: 'The monitor rejected the target because write permission is missing. No patch was applied.',
    console: 'Execution transcript', replayLabel:'REPLAY', idle:'Ready to replay a recorded run. No Python or Codex process runs in this browser.',
    initialStatus:'Choose a scenario and start playback.', running:'Replaying recorded evidence…', paused:'Playback paused.',
    results: {done:'Latest checks passed. The fixture notification was marked Done.',awaiting_checks:'Checks are pending. The notification remains open.',retry:'The branch changed. Re-evaluation is required before Done.',blocked:'No write permission. Repair was blocked and the notification remains open.'},
    doneCalls:'Done calls', evidenceTitle:'What actually ran?',
    evidence:'The build executes the real Python monitor, its check evaluator and SQLite state handling. A small checkout-total program fails three tests, receives a deterministic fixture patch and passes the same tests. Four scenarios verify when Done is allowed. GitHub responses, the Codex repair and publishing are test doubles; no live agent repair is claimed.',
    run:'View verification run ↗', download:'Download evidence JSON ↓', implementation:'Inspect the recorder ↗', commit:'Source commit',
    installTitle:'Run the real monitor locally',install:'The real application uses your GitHub access and an authenticated Codex CLI. Start in read-only mode; use --apply to enable repairs. The current release targets the configured brunnojob account.',installLink:'Setup and requirements ↗',
    footer:'Open source · MIT · By BrunnoDev', footerNote:'A demo of the workflow, with inspectable evidence.',
    events:{notification_found:'Read a fixture CI notification for brunnojob/autofix-demo-fixture.',failure_confirmed:'Confirmed failing checks using the real monitor classifier.',fixture_patched:'Applied a deterministic test patch: replace addition with multiplication. Codex is stubbed.',tests_passed:'Executed the fixture tests again: 3 tests passed.',publish_stubbed:'Simulated publishing in the GitHub test adapter. No remote Git push occurred.',checks_green:'The real check evaluator accepted the latest successful fixture check.',checks_pending:'The real check evaluator found a check still running.',marked_done:'The real verified_done guard allowed one Done call to the fixture adapter.',kept_open:'Done was not called. The notification remains open.',permission_denied:'The real permission guard rejected the target before the repair step.',head_changed:'The latest branch SHA differs from the repaired SHA. Done was blocked.'},
    failedOutput:'ACTUAL FIXTURE TEST OUTPUT · BEFORE PATCH',passedOutput:'ACTUAL FIXTURE TEST OUTPUT · AFTER PATCH',monitorOutput:'ACTUAL MONITOR LOG',
  },
  pt: {
    language:'Idioma',source:'Código-fonte ↗',badge:'Demo interativa',eyebrow:'GITHUB NOTIFICATION AUTOFIX',
    title:'De um teste com falha<br>a uma <span>correção verificada.</span>',
    lead:'Acompanhe uma notificação pelo diagnóstico, uma correção focada e a verificação independente. Veja por que o trabalho só termina quando os checks confirmam o resultado.',
    noteTitle:'Reproduzível, sem agente ao vivo.',note:'Reprodução de cenários de teste em Python. Sem login, tokens ou alterações nos seus repositórios.',
    scenario:'Cenário',scenarios:{success:'Correção concluída',pending:'Checks ainda em execução',race:'Branch alterada durante a correção',permission:'Sem permissão de escrita'},
    play:'Reproduzir execução',pause:'Pausar',resume:'Continuar',reset:'Reiniciar',next:'Próxima etapa',replay:'Reproduzir novamente',pipeline:'FLUXO DA CORREÇÃO',ready:'Aguardando',waiting:'Pendente',success:'Aprovado',blocked:'Bloqueado',
    steps:{scan:'Ler notificação',diagnose:'Confirmar o problema',repair:'Aplicar correção focada',test:'Executar testes locais',publish:'Publicar alteração',verify:'Verificar checks atuais',done:'Marcar notificação Done'},
    local:'Cenário gravado · GitHub e Codex substituídos por componentes de teste. Sem escrita externa.',
    notificationTitle:'Testes Python falharam: total da compra incorreto',notificationNote:'Notificação de teste · 3 testes unitários falham na função original.',
    recorded:'CENÁRIO GRAVADO',verified:'DONE VERIFICADO',open:'MANTIDA ABERTA',tabs:{diff:'Alteração',before:'Antes',after:'Depois'},files:'1 arquivo · 1 adição · 1 remoção',
    lockedTitle:'A alteração aparece após a etapa de correção.',locked:'Reproduza a gravação ou avance uma etapa por vez para inspecionar as decisões registradas.',
    noPatchTitle:'Nenhuma correção tentada.',noPatch:'O monitor rejeitou o destino por falta de permissão de escrita. Nenhuma alteração foi aplicada.',
    console:'Registro da execução',replayLabel:'REPRODUÇÃO',idle:'Pronto para reproduzir uma execução gravada. Nenhum processo Python ou Codex roda neste navegador.',
    initialStatus:'Escolha um cenário e inicie a reprodução.',running:'Reproduzindo a evidência gravada…',paused:'Reprodução pausada.',
    results:{done:'Checks atuais aprovados. A notificação de teste foi marcada Done.',awaiting_checks:'Checks pendentes. A notificação permanece aberta.',retry:'A branch mudou. É preciso reavaliar antes de marcar Done.',blocked:'Sem permissão de escrita. Correção bloqueada e notificação aberta.'},doneCalls:'Chamadas Done',
    evidenceTitle:'O que foi executado de verdade?',evidence:'A publicação executa o monitor Python real, seu avaliador de checks e o estado em SQLite. Um programa de total de compras falha em três testes, recebe uma correção determinística de teste e passa nos mesmos testes. Quatro cenários verificam quando Done é permitido. Respostas do GitHub, reparo pelo Codex e publicação são substituídos por componentes de teste; não se trata de um reparo ao vivo pelo agente.',
    run:'Ver execução de verificação ↗',download:'Baixar evidência JSON ↓',implementation:'Inspecionar o gravador ↗',commit:'Commit do código',
    installTitle:'Execute o monitor real no computador',install:'O programa real usa seu acesso ao GitHub e o Codex CLI autenticado. Comece no modo de leitura; use --apply para ativar correções. A versão atual atende à conta brunnojob configurada.',installLink:'Instalação e requisitos ↗',
    footer:'Código aberto · MIT · Por BrunnoDev',footerNote:'Uma demonstração do fluxo, com evidência verificável.',
    events:{notification_found:'Leitura de uma notificação de CI de teste de brunnojob/autofix-demo-fixture.',failure_confirmed:'Checks com falha confirmados pelo classificador real do monitor.',fixture_patched:'Correção determinística de teste aplicada: trocar adição por multiplicação. Codex substituído por um componente de teste.',tests_passed:'Testes do programa executados novamente: 3 testes aprovados.',publish_stubbed:'Publicação simulada no adaptador de teste do GitHub. Nenhum push remoto ocorreu.',checks_green:'O avaliador real de checks aceitou o check de teste atual aprovado.',checks_pending:'O avaliador real encontrou um check ainda em execução.',marked_done:'A função real verified_done permitiu uma chamada Done ao adaptador de teste.',kept_open:'Done não foi chamado. A notificação permanece aberta.',permission_denied:'A validação real de permissões rejeitou o destino antes da correção.',head_changed:'O SHA atual da branch difere do SHA corrigido. Done foi bloqueado.'},
    failedOutput:'SAÍDA REAL DOS TESTES DO EXEMPLO · ANTES',passedOutput:'SAÍDA REAL DOS TESTES DO EXEMPLO · DEPOIS',monitorOutput:'LOG REAL DO MONITOR',
  }
};
const steps = ['scan','diagnose','repair','test','publish','verify','done'];
const app = document.querySelector('#app');
let lang = new URL(location.href).searchParams.get('lang') === 'pt' ? 'pt' : 'en';
let evidence;
let selected = 'success';
let index = -1;
let playing = false;
let timer;
let speed = 900;
let view = 'diff';
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const scenario = () => evidence.scenarios.find(s => s.id === selected);
const seen = () => scenario().events.slice(0, index + 1);
const finished = () => index >= scenario().events.length - 1;
const stop = () => { clearTimeout(timer); playing = false; };

function mount() {
  const t = copy[lang];
  document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
  document.title = lang === 'pt' ? 'AutoFix — da notificação à correção verificada' : 'AutoFix — from notification to verified fix';
  document.querySelector('.skip').textContent = lang === 'pt' ? 'Pular para a demonstração' : 'Skip to demo';
  const sha = /^[a-f0-9]{40}$/.test(evidence.source_sha) ? evidence.source_sha : '';
  const runUrl = /^https:\/\/github\.com\/brunnojob\/github-notification-autofix\/actions\/runs\/\d+$/.test(evidence.workflow_url || '') ? evidence.workflow_url : `${REPO}/actions/workflows/pages.yml`;
  app.innerHTML = `<header class="site-header"><div class="shell header-inner"><a href="${REPO}" class="brand"><img src="./favicon.svg" alt="">AutoFix <small>${t.badge}</small></a><div class="header-actions"><a href="${REPO}">${t.source}</a><label class="language">${t.language}<select id="language" aria-label="${t.language}"><option value="en"${lang==='en'?' selected':''}>EN</option><option value="pt"${lang==='pt'?' selected':''}>PT</option></select></label></div></div></header>
  <main class="shell"><section class="intro"><div><div class="eyebrow">${t.eyebrow}</div><h1>${t.title}</h1><p>${t.lead}</p></div><p class="intro-note"><strong>${t.noteTitle}</strong>${t.note}</p></section>
  <section id="demo" aria-label="${t.badge}"><div class="toolbar"><label>${t.scenario}<select id="scenario" aria-label="${t.scenario}">${Object.entries(t.scenarios).map(([key,label])=>`<option value="${key}"${key===selected?' selected':''}>${label}</option>`).join('')}</select></label><div class="controls"><button id="play" class="btn primary">${t.play}</button><button id="next" class="btn">${t.next}</button><button id="reset" class="btn">${t.reset}</button><button id="speed" class="btn speed" aria-label="${lang==='pt'?'Velocidade da reprodução':'Playback speed'}">${speed===900?'1×':'4×'}</button></div></div>
  <div class="workspace"><aside class="timeline"><p class="label">${t.pipeline}</p><ol>${steps.map((key,i)=>`<li data-step="${key}"><span class="step-icon">${i+1}</span><div class="step-copy"><strong>${t.steps[key]}</strong><small>${t.ready}</small></div></li>`).join('')}</ol><p class="local-tag">${t.local}</p></aside>
  <div class="work-main"><div class="notification"><span class="notification-icon" aria-hidden="true">!</span><div><p>brunnojob / autofix-demo-fixture</p><h2>${t.notificationTitle}</h2><small>${t.notificationNote}</small></div><span id="outcome-tag" class="tag">${t.recorded}</span></div>
  <div class="tabs" role="tablist" aria-label="${lang==='pt'?'Visualização do código':'Code view'}">${Object.entries(t.tabs).map(([key,label])=>`<button class="tab" id="tab-${key}" role="tab" data-view="${key}" aria-controls="code" aria-selected="${view===key}" tabindex="${view===key?0:-1}">${label}</button>`).join('')}</div>
  <div id="code" class="code-area" role="tabpanel" tabindex="0"></div>
  <div class="console"><div class="console-head"><span>${t.console}</span><span>${t.replayLabel}</span></div><pre id="transcript" tabindex="0"></pre></div>
  <div class="status-bar"><strong id="status" role="status" aria-live="polite"></strong><span id="done-count" class="outcome"></span></div></div></div></section>
  <section class="evidence"><div><h2>${t.evidenceTitle}</h2><p>${t.evidence}</p><div class="evidence-links"><a href="${runUrl}" target="_blank" rel="noopener noreferrer">${t.run}</a><a href="./evidence.json" download="autofix-evidence.json">${t.download}</a><a href="${REPO}/blob/${sha||'main'}/demo/record.py" target="_blank" rel="noopener noreferrer">${t.implementation}</a></div><p class="metadata">${t.commit}: ${sha ? `<a href="${REPO}/commit/${sha}">${sha.slice(0,12)}</a>` : 'local'} · SHA-256: ${esc(evidence.source_hash.slice(0,16))}…</p></div><div class="local-use"><h2>${t.installTitle}</h2><p>${t.install}</p><code>python github_autofix.py --once\npython github_autofix.py --apply</code><div class="evidence-links"><a href="${REPO}#requirements">${t.installLink}</a></div></div></section>
  <footer class="footer"><a href="${REPO}">${t.footer}</a><span>${t.footerNote}</span></footer></main>`;
  document.querySelector('#language').addEventListener('change', e => {stop();lang=e.target.value;const url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(null,'',url);mount();});
  document.querySelector('#scenario').addEventListener('change', e => {stop();selected=e.target.value;index=-1;mount();});
  document.querySelector('#play').addEventListener('click', () => {if(playing){stop();update();return;}if(finished())index=-1;playing=true;advance();});
  document.querySelector('#next').addEventListener('click', () => {stop();advance();});
  document.querySelector('#reset').addEventListener('click', () => {stop();index=-1;update();});
  document.querySelector('#speed').addEventListener('click', () => {speed=speed===900?225:900;document.querySelector('#speed').textContent=speed===900?'1×':'4×';});
  document.querySelectorAll('[data-view]').forEach(button=>{
    button.addEventListener('click',()=>selectView(button.dataset.view));
    button.addEventListener('keydown',event=>{const keys=Object.keys(t.tabs);let offset=event.key==='ArrowRight'?1:event.key==='ArrowLeft'?-1:0;if(!offset)return;event.preventDefault();selectView(keys[(keys.indexOf(view)+offset+keys.length)%keys.length]);document.querySelector(`#tab-${view}`).focus();});
  });
  update();
}
function selectView(value){view=value;document.querySelectorAll('[data-view]').forEach(b=>{b.setAttribute('aria-selected',String(b.dataset.view===view));b.tabIndex=b.dataset.view===view?0:-1;});renderCode();}
function advance(){clearTimeout(timer);if(index<scenario().events.length-1)index++;if(finished())playing=false;update();if(playing)timer=setTimeout(advance,speed);}
function renderCode(){
  const t=copy[lang];const target=document.querySelector('#code');target.setAttribute('aria-labelledby',`tab-${view}`);
  const repaired=seen().some(e=>e.step==='repair');
  if(!repaired&&view!=='before'){const noPatch=finished()&&selected==='permission';target.innerHTML=`<div class="locked"><strong>${noPatch?t.noPatchTitle:t.lockedTitle}</strong>${noPatch?t.noPatch:t.locked}</div>`;return;}
  const content=view==='before'?evidence.before:view==='after'?evidence.after:evidence.diff;
  target.innerHTML=`<div class="code-header"><span>checkout_total.py</span><span>${view==='diff'?t.files:t.tabs[view]}</span></div><div class="code-lines">${content.trimEnd().split('\n').map((line,i)=>`<div class="code-line ${view==='diff'?(line.startsWith('+')&&!line.startsWith('+++')?'added':line.startsWith('-')&&!line.startsWith('---')?'removed':line.startsWith('@')?'meta':''):''}"><span class="line-number" aria-hidden="true">${i+1}</span><span>${esc(line)||' '}</span></div>`).join('')}</div>`;
}
function update(){
  const t=copy[lang];const current=seen();const last=current.at(-1);
  for(const key of steps){const item=document.querySelector(`[data-step="${key}"]`);const event=current.filter(e=>e.step===key).at(-1);item.className=event?.state||'';item.querySelector('.step-icon').textContent=event?(event.state==='success'?'✓':event.state==='waiting'?'…':'!'):String(steps.indexOf(key)+1);item.querySelector('small').textContent=event?t[event.state]:t.ready;}
  document.querySelector('#play').textContent=playing?t.pause:finished()?t.replay:index>=0?t.resume:t.play;
  document.querySelector('#next').disabled=finished();
  document.querySelector('#status').textContent=finished()?t.results[scenario().result]:playing?t.running:index<0?t.initialStatus:t.paused;
  document.querySelector('#done-count').textContent=`${t.doneCalls}: ${finished()?scenario().done_calls:0}`;
  const tag=document.querySelector('#outcome-tag');tag.textContent=finished()?(scenario().done_calls?t.verified:t.open):t.recorded;tag.className=`tag${finished()&&scenario().done_calls?' good':''}`;
  const lines=current.map((event,i)=>`[${String(i+1).padStart(2,'0')}] ${t.events[event.code]}`);
  if(current.some(e=>e.code==='failure_confirmed'))lines.push(`\n${t.failedOutput}\n${scenario().fixture.before}`);
  if(current.some(e=>e.code==='tests_passed'))lines.push(`\n${t.passedOutput}\n${scenario().fixture.after}`);
  if(finished()&&scenario().monitor_log.length)lines.push(`\n${t.monitorOutput}\n${scenario().monitor_log.join('\n')}`);
  document.querySelector('#transcript').textContent=lines.length?lines.join('\n'):t.idle;
  renderCode();
}
try{
  const response=await fetch('./evidence.json',{cache:'no-cache'});if(!response.ok)throw Error('Evidence unavailable');evidence=await response.json();
  if(evidence.schema!==1||!Array.isArray(evidence.scenarios)||evidence.scenarios.length!==4||!evidence.scenarios.every(s=>Array.isArray(s.events)&&s.events.length&&s.events.every(e=>steps.includes(e.step)&&['success','waiting','blocked'].includes(e.state))))throw Error('Invalid evidence');
  mount();
}catch(error){app.innerHTML=`<section class="failure"><h1>Evidence unavailable</h1><p>The recording could not be loaded. Reload the page or inspect the verification run.</p><a href="${REPO}/actions/workflows/pages.yml">Open GitHub Actions ↗</a><p>Nenhum reparo foi executado neste navegador.</p></section>`;}
