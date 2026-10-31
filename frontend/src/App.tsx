import { useEffect, useMemo, useState } from 'react'
import {
  Activity, ArrowUpRight, BookOpenText, CarFront, ChartNoAxesCombined,
  Check, CheckCircle2, ChevronRight, CircleAlert, ClipboardCopy, Clock3,
  Code2, Database, FileCode2, Gauge, GitMerge, Layers3, LoaderCircle,
  Play, RefreshCw, Search, ServerCog, ShieldCheck, Table2, Workflow,
  Wrench, X,
} from 'lucide-react'
import { Button } from './components/ui/button'
import { getCatalog, getState, prepareDb, runExercise } from './api'
import type { Catalog, DbState, Exercise, RunResult } from './types'

const iconMap = {
  simples: Search,
  joins: GitMerge,
  agregadas: ChartNoAxesCombined,
  vistas: Layers3,
  triggers: Workflow,
}
const topicMeta: Record<string,string> = {
  simples: 'Búsqueda y filtrado',
  joins: 'Tablas relacionadas',
  agregadas: 'Métricas y agrupación',
  vistas: 'Consultas reutilizables',
  triggers: 'Reglas automáticas',
}
const emptyStatus: DbState = {connected:false,ready:false,message:'Consultando el servidor…'}
function cell(value:unknown):string {
  if(value===null||value===undefined)return '—'
  if(typeof value==='boolean')return value?'Sí':'No'
  if(typeof value==='object')return JSON.stringify(value)
  return String(value)
}
export default function App() {
  const [catalog,setCatalog] = useState<Catalog|null>(null)
  const [status,setStatus] = useState<DbState>(emptyStatus)
  const [group,setGroup] = useState('simples')
  const [selected,setSelected] = useState('S01')
  const [search,setSearch] = useState('')
  const [params,setParams] = useState<Record<string,string|number>>({})
  const [result,setResult] = useState<RunResult|null>(null)
  const [busy,setBusy] = useState(false)
  const [preparing,setPreparing] = useState(false)
  const [error,setError] = useState('')
  const [message,setMessage] = useState('')
  const [copied,setCopied] = useState(false)
  const [showGuide,setShowGuide] = useState(false)

  useEffect(()=>{
    void getCatalog().then(setCatalog).catch(err=>setError(err instanceof Error?err.message:'Sin catálogo'))
    void getState().then(setStatus).catch(()=>setStatus({connected:false,ready:false,message:'No responde FastAPI'}))
  },[])
  const exercises = useMemo(()=>catalog?.exercises.filter(ex=>
    ex.group===group && `${ex.code} ${ex.title} ${ex.description}`.toLocaleLowerCase().includes(search.toLocaleLowerCase())
  )||[],[catalog,group,search])
  const active = catalog?.exercises.find(ex=>ex.group===group && ex.code===selected)
  const currentGroup = catalog?.groups.find(item=>item.id===group)
  function selectExercise(ex:Exercise){
    setSelected(ex.code)
    setParams(Object.fromEntries(ex.params.map(p=>[p.name,p.default])))
    setResult(null);setError('');setMessage('')
  }
  function changeGroup(id:string){
    setGroup(id);setSearch('')
    const next=catalog?.exercises.find(ex=>ex.group===id)
    if(next)selectExercise(next)
  }
  async function refresh(){
    try{setStatus(await getState())}
    catch{setStatus({connected:false,ready:false,message:'No responde FastAPI'})}
  }
  async function prepare(){
    if(!window.confirm('Se preparará únicamente la BD indicada por UNIT5_ALLOWED_DATABASE. Debe estar vacía o contener este laboratorio. ¿Continuar?'))return
    setPreparing(true);setError('');setMessage('')
    try{
      const data=await prepareDb()
      setMessage(data.created_now?'Esquema AutoGest creado e inicializado con datos ficticios.':data.message)
      await refresh()
    }catch(err){setError(err instanceof Error?err.message:'No fue posible preparar la BD')}
    finally{setPreparing(false)}
  }
  async function execute(){
    if(!active)return
    setBusy(true);setResult(null);setError('');setMessage('')
    try{setResult(await runExercise(active.code,params))}
    catch(err){setError(err instanceof Error?err.message:'Error al consultar la BD')}
    finally{setBusy(false)}
  }
  async function copySql(){
    if(!active)return
    try{await navigator.clipboard.writeText(active.sql);setCopied(true);window.setTimeout(()=>setCopied(false),1800)}
    catch{setError('No se pudo copiar el SQL desde el navegador.')}
  }

  return <div className="min-h-screen bg-[#F0F4F7]">
    <header className="relative z-10 border-b border-[#DFE8EE] bg-white px-5 py-4 md:px-7">
      <div className="mx-auto flex max-w-[1800px] items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#10283C] text-[#6EE0D7]"><CarFront size={25}/></div>
          <div><div className="font-display text-xl font-extrabold tracking-[-.045em] text-[#10283C]">Auto<span className="text-[#0A9291]">Gest</span><span className="ml-2 align-middle text-[9px] font-extrabold tracking-[.13em] text-[#8BA2B3] uppercase">LAB</span></div>
          <div className="text-[10px] font-semibold tracking-[.12em] text-[#8596A5] uppercase">Concesionaria · Unidad 5</div></div>
        </div>
        <div className="flex items-center gap-2 sm:gap-4">
          <div className={`hidden items-center gap-2 rounded-full px-3 py-2 text-xs font-bold sm:flex ${status.ready?'bg-[#E5F6EF] text-[#177A55]':status.connected?'bg-[#FFF3DF] text-[#956423]':'bg-[#FFF0EE] text-[#AE4843]'}`}>
            <span className={`h-2 w-2 rounded-full ${status.ready?'bg-[#22A46A]':status.connected?'bg-[#F0AE47]':'bg-[#D45A55]'}`}/>
            {status.ready?'Base preparada':status.connected?'Preparación pendiente':'Sin conexión'}
          </div>
          <Button variant="outline" size="sm" onClick={()=>void refresh()} title="Actualizar estado"><RefreshCw size={15}/><span className="hidden sm:inline">Actualizar</span></Button>
          <div className="rounded-lg bg-[#EDF5F7] px-3 py-2 text-xs font-extrabold tracking-wide text-[#2A6470]">U5 / 2026</div>
        </div>
      </div>
    </header>

    <div className="layout mx-auto max-w-[1800px]">
      <aside className="sidenav sidenav-glow px-4 py-6 sm:px-5">
        <div className="mb-7 px-2"><div className="text-[10px] font-bold tracking-[.24em] text-[#6BC3C6] uppercase">CENTRO DE APRENDIZAJE</div>
          <div className="font-display mt-2 text-xl font-bold leading-tight">Laboratorio<br/>PostgreSQL</div>
          <p className="mt-3 text-xs leading-5 text-[#A7C0CE]">Experimenta con el inventario, las ventas y las revisiones de la concesionaria.</p>
        </div>
        <div className="px-3 text-[10px] font-bold tracking-[.17em] text-[#91ACBB] uppercase">Módulos de práctica</div>
        <nav className="category-grid mt-3 space-y-1" aria-label="Unidades de la práctica">
          {catalog?.groups.map((section,i)=>{
            const Icon=iconMap[section.id as keyof typeof iconMap]||FileCode2
            return <button key={section.id} className={`category-btn ${group===section.id?'active':''}`} onClick={()=>changeGroup(section.id)}>
              <span className={`rounded-xl p-2 ${group===section.id?'bg-[#2C6874] text-[#6DE7D8]':'bg-[#1B394D] text-[#88A8BB]'}`}><Icon size={17}/></span>
              <span className="min-w-0 flex-1"><span className="block text-xs font-bold">5.{i+1} · {section.title}</span><span className="mt-1 block text-[10px] text-[#A4BCC9]">{section.target} ejercicios</span></span>
              <ChevronRight size={13} className="hidden text-[#84ACBA] xl:block"/>
            </button>
          })}
        </nav>
        <div className="my-6 h-px bg-[#29465A]"/>
        <div className="rounded-2xl border border-[#305568] bg-[#18394C] p-4">
          <div className="mb-2 flex items-center gap-2 text-xs font-bold text-[#DDF6F4]"><ServerCog size={17} className="text-[#5DDED2]"/> Base experimental</div>
          <p className="mb-3 break-all text-[11px] leading-5 text-[#A6C1CF]">{status.database||status.message}</p>
          <Button variant="accent" size="sm" className="w-full" onClick={()=>void prepare()} disabled={!status.connected||preparing}>
            {preparing?<LoaderCircle size={15} className="animate-spin"/>:<Database size={15}/>}
            {preparing?'Preparando…':status.ready?'Verificar objetos':'Preparar base demo'}
          </Button>
          <p className="mt-3 text-[10px] leading-4 text-[#A3BEC9]">Solo acepta una base de Unidad 5. No utiliza datos reales.</p>
        </div>
        <button className="mt-4 flex w-full items-center gap-2 rounded-xl px-3 py-3 text-xs font-semibold text-[#ACD4D8] hover:bg-white/5" onClick={()=>setShowGuide(true)}><BookOpenText size={16}/> Guía de uso <ArrowUpRight size={14} className="ml-auto"/></button>
        <div className="mt-6 flex gap-2 px-2 text-[10px] leading-5 text-[#82A5B6]"><ShieldCheck size={18} className="shrink-0 text-[#4BD2C0]"/> Consultas cerradas y ejemplos de triggers que revierten cambios.</div>
      </aside>

      <section className="catalog-panel px-4 py-6" aria-label="Ejercicios">
        <div className="mb-5 flex items-center justify-between"><div><div className="font-display text-lg font-extrabold text-[#173A4B]">Ejercicios</div><p className="mt-1 text-xs text-[#7C95A4]">{currentGroup?.title||'Cargando…'}</p></div><div className="rounded-xl bg-[#E4F1F4] px-3 py-2 text-sm font-extrabold text-[#187E86]">{currentGroup?.target||0}</div></div>
        <div className="relative mb-4"><Search size={16} className="absolute top-1/2 left-3 -translate-y-1/2 text-[#93AAB6]"/>
          <input aria-label="Buscar ejercicios" className="input-control pl-10 text-sm" placeholder="Buscar un ejercicio…" value={search} onChange={e=>setSearch(e.target.value)}/></div>
        <div className="max-h-[calc(100vh-245px)] space-y-1 overflow-y-auto pr-1">
          {exercises.map(ex=><button key={ex.code} className={`exercise-item ${selected===ex.code?'active':''}`} onClick={()=>selectExercise(ex)}>
            <div className="flex items-center gap-3"><span className={`w-11 shrink-0 rounded-lg px-2 py-2 text-center text-[11px] font-extrabold ${selected===ex.code?'bg-[#0D8C89] text-white':'bg-[#E6EFF4] text-[#587C8D]'}`}>{ex.code}</span>
              <div className="min-w-0"><div className="text-xs font-extrabold text-[#254656]">{ex.title}</div><div className="mt-1 line-clamp-2 text-[11px] leading-4 text-[#7E97A4]">{ex.description}</div></div></div>
          </button>)}
          {exercises.length===0&&<div className="rounded-xl border border-dashed border-[#D4E3E8] p-5 text-center text-xs text-[#8AA2AD]">No hay coincidencias.</div>}
        </div>
      </section>

      <main className="content-panel min-w-0 px-4 py-6 md:px-6 xl:px-8">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2 text-[11px] font-bold tracking-[.12em] text-[#7895A3] uppercase"><Gauge size={15}/> Panel de prácticas <ChevronRight size={14}/> <span className="text-[#0C9190]">{currentGroup?.title}</span></div>
          <div className="flex items-center gap-2 rounded-full border border-[#DAE8EF] bg-white px-3 py-2 text-[11px] text-[#607F90]"><Activity size={14} className="text-[#0D9D9A]"/> Sesión local · Solo demostración</div></div>
        <div className="mb-5 grid gap-3 sm:grid-cols-3">
          <div className="kpi"><div className="flex items-center justify-between"><span className="text-[10px] font-bold tracking-[.09em] text-[#7A96A5] uppercase">Ejercicios</span><Code2 size={18} className="text-[#1B9B99]"/></div><div className="font-display mt-2 text-3xl font-extrabold text-[#142D3F]">{catalog?.total||'—'}<span className="ml-2 text-xs font-semibold text-[#92A4AE]">totales</span></div></div>
          <div className="kpi"><div className="flex items-center justify-between"><span className="text-[10px] font-bold tracking-[.09em] text-[#7A96A5] uppercase">Esquema canónico</span><CarFront size={18} className="text-[#1B9B99]"/></div><div className="font-display mt-2 text-3xl font-extrabold text-[#142D3F]">6<span className="ml-2 text-xs font-semibold text-[#92A4AE]">tablas</span></div></div>
          <div className="kpi"><div className="flex items-center justify-between"><span className="text-[10px] font-bold tracking-[.09em] text-[#7A96A5] uppercase">Objetos SQL</span><Wrench size={18} className="text-[#E89C47]"/></div><div className="font-display mt-2 text-3xl font-extrabold text-[#142D3F]">15<span className="ml-2 text-xs font-semibold text-[#92A4AE]">5 vistas + 5 + 5</span></div></div>
        </div>

        {active?<>
          <section className="panel mb-5 overflow-hidden">
            <div className="h-1 bg-linear-to-r from-[#0E7F83] via-[#20B2AF] to-[#F0AE5A]"/>
            <div className="p-5 lg:p-6"><div className="mb-3 flex flex-wrap items-center gap-2"><span className="rounded-lg bg-[#123C4E] px-2.5 py-1.5 text-[11px] font-extrabold text-white">{active.code}</span><span className="rounded-lg bg-[#E9F3F5] px-2.5 py-1.5 text-[11px] font-bold text-[#36818B]">{topicMeta[active.group]}</span></div>
              <h1 className="font-display text-2xl font-extrabold tracking-[-.035em] text-[#143142] lg:text-3xl">{active.title}</h1>
              <p className="mt-2 max-w-[680px] text-sm leading-6 text-[#718998]">{active.description}</p>
              {active.group==='triggers'&&<div className="mt-4 flex gap-2 rounded-xl bg-[#FFF5E7] p-3 text-xs leading-5 text-[#885E28]"><ShieldCheck size={17} className="shrink-0"/> La demostración hace pruebas reales y revierte sus cambios automáticamente.</div>}
            </div>
          </section>
          <section className="panel mb-5 p-5 lg:p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2 text-sm font-extrabold text-[#294C5F]"><Code2 size={18} className="text-[#0E9791]"/> Código PostgreSQL</div><Button variant="outline" size="sm" onClick={()=>void copySql()}>{copied?<Check size={14}/>:<ClipboardCopy size={14}/>} {copied?'Copiado':'Copiar SQL'}</Button></div>
            <div className="sql-frame"><div className="sql-top"><i className="h-2 w-2 rounded-full bg-[#E47776]"/><i className="h-2 w-2 rounded-full bg-[#E9B85D]"/><i className="h-2 w-2 rounded-full bg-[#70C7B5]"/><span className="ml-3 text-[10px] tracking-wide text-[#9AB5C4]">{active.group==='triggers'?'function.sql / plpgsql':'consulta.sql / postgresql'}</span></div>
              <pre><code>{active.sql}</code></pre></div>
            {!!active.params.length&&<div className="mt-5"><div className="mb-3 text-[10px] font-extrabold tracking-[.12em] text-[#6E8A9A] uppercase">Parámetros</div><div className="grid gap-3 sm:grid-cols-2">{active.params.map(p=><label key={p.name} className="block"><span className="mb-2 block text-xs font-bold text-[#466478]">{p.label}</span><input className="input-control text-sm" type={p.kind==='date'?'date':p.kind==='float'||p.kind==='int'?'number':'text'} step={p.kind==='float'?'0.01':undefined} value={params[p.name]??p.default} onChange={e=>setParams(old=>({...old,[p.name]:e.target.value}))}/></label>)}</div></div>}
            <div className="mt-5 flex flex-wrap items-center justify-between gap-3"><span className="flex items-center gap-2 text-xs text-[#7F95A1]"><ShieldCheck size={15} className="text-[#0C9C93]"/> SQL predefinido · parámetros validados</span><Button size="lg" disabled={busy||!status.ready} onClick={()=>void execute()}>{busy?<LoaderCircle size={17} className="animate-spin"/>:<Play size={17} fill="currentColor"/>} {busy?'Ejecutando…':'Ejecutar consulta'}</Button></div>
          </section>
        </>:<section className="panel mb-5 p-8 text-sm text-[#74919F]">Selecciona un ejercicio del catálogo.</section>}

        {(error||message)&&<div role={error?'alert':'status'} className={`mb-5 flex gap-3 rounded-xl border p-4 text-sm ${error?'border-[#F4C8C3] bg-[#FFF1EF] text-[#AA4B41]':'border-[#BFE5D2] bg-[#EDF9F2] text-[#2C815C]'}`}>
          {error?<CircleAlert size={19} className="shrink-0"/>:<CheckCircle2 size={19} className="shrink-0"/>}{error||message}</div>}
        <section className="panel p-5 lg:p-6"><div className="mb-4 flex flex-wrap items-center justify-between gap-2"><div><div className="flex items-center gap-2 text-sm font-extrabold text-[#294C5F]"><Table2 size={19} className="text-[#0E9791]"/> Resultados de ejecución</div><p className="mt-1 text-xs text-[#8DA3AE]">Datos ficticios consultados en tiempo real desde Neon.</p></div>
          {result&&<div className="flex gap-3 text-xs font-semibold text-[#678494]"><span className="flex items-center gap-1"><Table2 size={14}/>{result.rows.length} filas</span><span className="flex items-center gap-1"><Clock3 size={14}/>{result.duration_ms.toFixed(1)} ms</span></div>}</div>
          {result?<><div className="overflow-x-auto rounded-xl border border-[#E2EAF0]"><table className="data-table"><thead><tr>{result.columns.map(name=><th key={name}>{name.replaceAll('_',' ')}</th>)}</tr></thead><tbody>{result.rows.map((row,i)=><tr key={i}>{result.columns.map(name=><td key={name}>{cell(row[name])}</td>)}</tr>)}</tbody></table>{!result.rows.length&&<p className="p-6 text-center text-sm text-[#8AA2B0]">La consulta no produjo filas.</p>}</div><p className="mt-3 flex items-center gap-2 text-xs text-[#38866E]"><CheckCircle2 size={15}/>{result.message}{result.truncated?' · Se muestran las primeras 100 filas.':''}</p></>
          :<div className="flex min-h-[185px] flex-col items-center justify-center rounded-xl border border-dashed border-[#D7E4EA] bg-[#FBFDFE] p-5 text-center"><div className="mb-3 rounded-2xl bg-[#E9F5F6] p-4 text-[#318F93]"><Database size={26}/></div><div className="text-sm font-extrabold text-[#4B6B7C]">Listo para explorar</div><p className="mt-1 max-w-[310px] text-xs leading-5 text-[#92A7B2]">Prepara la base experimental y ejecuta un ejercicio para mostrar resultados.</p></div>}
        </section>
        <footer className="mt-5 flex flex-wrap items-center justify-between gap-2 border-t border-[#D8E4EA] py-5 text-[11px] text-[#8CA2AC]"><span>AutoGest · Laboratorio académico · Unidad 5</span><span className="flex items-center gap-2"><ShieldCheck size={14}/> Sin autenticación comercial · Datos ficticios</span></footer>
      </main>
    </div>

    {showGuide&&<div className="fixed inset-0 z-40 flex items-center justify-center bg-[#0A1E2E]/65 p-4" role="dialog" aria-modal="true" aria-label="Guía de uso"><div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl"><div className="flex items-center justify-between"><h2 className="font-display text-xl font-extrabold text-[#173A4B]">Cómo utilizar AutoGest Lab</h2><button onClick={()=>setShowGuide(false)} className="rounded-lg p-2 hover:bg-[#EDF4F7]" aria-label="Cerrar"><X size={20}/></button></div><ol className="mt-4 list-inside list-decimal space-y-3 text-sm leading-6 text-[#607E8E]"><li>Crea una base de datos PostgreSQL exclusiva y vacía llamada <code>autogest_unidad5</code>.</li><li>Configura la URL de Neon en <code>backend/.env</code> y ejecuta FastAPI.</li><li>Pulsa <strong>Preparar base demo</strong> para instalar el esquema y los datos ficticios.</li><li>Explora los 65 ejercicios. Las consultas son de solo lectura; los cinco triggers se prueban en transacciones revertidas.</li></ol><Button className="mt-5 w-full" onClick={()=>setShowGuide(false)}>Entendido</Button></div></div>}
  </div>
}
