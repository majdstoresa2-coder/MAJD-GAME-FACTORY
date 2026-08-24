#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-SOVEREIGN-PUBLIC-PLATFORM-07.py
====================================
SOVEREIGN PUBLIC PLATFORM BUILDER
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent
PUBLIC_ROOT = ROOT_DIR / "public-platform"
INDEX_FILE = PUBLIC_ROOT / "index.html"
CONFIG_FILE = PUBLIC_ROOT / "majd-public-config.json"

PLATFORM_NAME = "MAJD"
VERSION = "1.0.0"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)

def build_config() -> Dict[str, Any]:
    return {
        "platform": "MAJD",
        "version": VERSION,
        "generated_at": utc_now(),
        "roles": {
            "owner": "SUPREME_OWNER",
            "user": "USER",
            "player": "PLAYER"
        },
        "api": {
            "health": "/api/health",
            "auth_me": "/api/auth/me",
            "login": "/api/auth/login",
            "logout": "/api/auth/logout",
            "feed": "/api/feed",
            "live": "/api/live",
            "games": "/api/games",
            "ai": "/api/ai",
            "owner_panel": "/owner"
        }
    }

def build_html() -> str:
    return """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#050b14">
<title>منصة مجد الرسمية السيادية</title>
<style>
:root{
  --bg:#050b14;--panel:#0c1724;--panel2:#101d2b;--line:rgba(255,255,255,.08);
  --text:#f6f8fb;--muted:#91a4b7;--gold:#ddb253;--gold2:#f2d27f;--ok:#22c55e;
}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:Arial,Tahoma,sans-serif;background:
radial-gradient(circle at 80% 0,rgba(221,178,83,.12),transparent 30%),var(--bg);color:var(--text)}
button,input{font:inherit}
.shell{min-height:100vh;display:grid;grid-template-columns:270px minmax(0,1fr) 300px;gap:16px;padding:16px}
.side,.right,.card,.hero,.media,.post{background:linear-gradient(180deg,rgba(16,29,43,.97),rgba(8,17,28,.97));border:1px solid var(--line)}
.side,.right{position:sticky;top:16px;height:calc(100vh - 32px);overflow:auto;border-radius:22px;padding:15px}
.brand{display:flex;gap:12px;align-items:center;padding:6px 4px 16px;border-bottom:1px solid var(--line);margin-bottom:12px}
.logo{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#8b651b,var(--gold2));color:#111;font-weight:900;font-size:23px}
.brand h1{margin:0;color:var(--gold2);font-size:19px}.brand small{color:var(--muted)}
.nav{display:grid;gap:5px}.nav button{border:0;background:transparent;color:#dce5ee;padding:11px 12px;border-radius:13px;cursor:pointer;text-align:right}
.nav button:hover,.nav button.active{background:rgba(221,178,83,.13);color:#fff}.owner-only{display:none}.is-owner .owner-only{display:block}
main{min-width:0}.topbar{position:sticky;top:0;z-index:20;background:rgba(5,11,20,.82);backdrop-filter:blur(14px);display:flex;gap:10px;padding:8px 0 14px}
.search{flex:1;display:flex;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:0 13px}
.search input{width:100%;border:0;outline:0;background:transparent;color:#fff;padding:13px}
.btn{border:0;border-radius:999px;padding:11px 18px;cursor:pointer;background:linear-gradient(90deg,#b78323,var(--gold2));color:#111;font-weight:800}
.avatar{width:43px;height:43px;border-radius:50%;display:grid;place-items:center;background:#183046;border:2px solid rgba(221,178,83,.5);cursor:pointer}
.hero{min-height:235px;border-radius:23px;padding:28px;display:flex;align-items:end;position:relative;overflow:hidden;background:
linear-gradient(90deg,rgba(2,7,12,.94),rgba(2,7,12,.15)),radial-gradient(circle at 78% 34%,rgba(221,178,83,.35),transparent 20%),linear-gradient(135deg,#0d2332,#382b15)}
.hero:after{content:"👑";position:absolute;left:8%;top:3%;font-size:140px;opacity:.14}.hero>div{position:relative;z-index:2;max-width:650px}
.hero h2{margin:0 0 8px;color:var(--gold2);font-size:31px}.hero p{margin:0 0 18px;color:#d1d9e2;line-height:1.8}
.section{margin-top:20px}.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:11px}.section-head h3{margin:0}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.media{border-radius:17px;overflow:hidden}.thumb{aspect-ratio:16/9;display:grid;place-items:center;font-size:50px;background:linear-gradient(135deg,#132b3c,#3c2d16)}.info{padding:11px}.info small{color:var(--muted)}
.composer{margin-top:16px;border-radius:17px;padding:13px;display:flex;gap:10px}.composer input{flex:1;background:#07111c;border:1px solid var(--line);border-radius:13px;color:#fff;padding:12px}
.feed{display:grid;gap:12px}.post{border-radius:17px;padding:15px}.post p{line-height:1.8}.muted{color:var(--muted)}.status-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--ok)}
.empty{grid-column:1/-1;border:1px dashed rgba(255,255,255,.14);border-radius:15px;padding:22px;text-align:center;color:var(--muted)}
.modal{display:none;position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.72);align-items:center;justify-content:center;padding:20px}.modal.open{display:flex}
.login{width:min(92vw,450px);background:#0a1522;border:1px solid var(--line);border-radius:21px;padding:22px}.login input{width:100%;margin:6px 0;padding:12px;border-radius:12px;border:1px solid var(--line);background:#07111c;color:#fff}
.toast{display:none;position:fixed;left:20px;bottom:20px;z-index:200;background:#0b1522;border:1px solid var(--line);border-radius:13px;padding:12px 15px}.toast.show{display:block}
@media(max-width:1100px){.shell{grid-template-columns:220px minmax(0,1fr)}.right{display:none}}
@media(max-width:760px){.shell{display:block;padding:10px}.side{position:relative;top:0;height:auto;margin-bottom:10px}.nav{grid-template-columns:repeat(4,1fr)}.nav button{font-size:0;text-align:center}.nav button:before{font-size:19px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
</head>
<body>
<div class="shell">
<aside class="side">
  <div class="brand"><div class="logo">M</div><div><h1>MAJD</h1><small>المنصة الرسمية السيادية</small></div></div>
  <div class="nav">
    <button class="active">⌂ الرئيسية</button>
    <button>✦ المنشورات</button>
    <button>● البث المباشر</button>
    <button>▶ Shorts</button>
    <button>▣ الفيديوهات</button>
    <button>🎬 الأفلام</button>
    <button>▤ المسلسلات</button>
    <button id="gamesNav">🎮 الألعاب</button>
    <button>🏆 البطولات والفعاليات</button>
    <button>✉ الرسائل</button>
    <button>👥 المجموعات</button>
    <button>🔔 الإشعارات</button>
    <button>◎ الملف الشخصي</button>
    <button>✧ ذكاء مجد</button>
    <button id="ownerCenter" class="owner-only">👑 مركز المالك</button>
  </div>
</aside>

<main>
  <div class="topbar">
    <div class="search">⌕<input placeholder="ابحث في مجد..."></div>
    <button class="btn" id="loginBtn">تسجيل الدخول</button>
    <div class="avatar" id="accountBtn">م</div>
  </div>

  <section class="hero">
    <div>
      <h2>مرحباً بك في مجد</h2>
      <p>منصة اجتماعية وترفيهية وألعاب سيادية تجمع المحتوى والبث والألعاب والذكاء الاصطناعي في مكان واحد.</p>
      <button class="btn" id="exploreGames">استكشف الألعاب</button>
    </div>
  </section>

  <section class="card composer">
    <div class="avatar">م</div>
    <input id="composer" placeholder="شارك مجتمع مجد...">
    <button class="btn" id="publishPost">نشر</button>
  </section>

  <section class="section">
    <div class="section-head"><h3>البث المباشر</h3><span class="muted">الآن</span></div>
    <div class="grid" id="liveGrid"></div>
  </section>

  <section class="section" id="gamesSection">
    <div class="section-head"><h3>أفضل الألعاب</h3><span class="muted">ألعاب مجد المنشورة</span></div>
    <div class="grid" id="gamesGrid"></div>
  </section>

  <section class="section">
    <div class="section-head"><h3>آخر المنشورات</h3><span class="muted">المجتمع</span></div>
    <div class="feed" id="feed"></div>
  </section>
</main>

<aside class="right">
  <h4>حالة مجد</h4>
  <p><span class="status-dot"></span> <span id="health">جاري الاتصال...</span></p>
  <hr style="border-color:var(--line)">
  <h4>اقتراحات لك</h4>
  <p class="muted">المبدعون والقنوات المقترحة ستظهر هنا من البيانات الحقيقية.</p>
  <hr style="border-color:var(--line)">
  <h4>ذكاء مجد</h4>
  <p class="muted">مساعد مجد السيادي مربوط بالخدمات الخلفية.</p>
</aside>
</div>

<div class="modal" id="loginModal">
  <div class="login">
    <h3>تسجيل الدخول إلى مجد</h3>
    <input id="email" type="email" placeholder="البريد الإلكتروني">
    <input id="password" type="password" placeholder="كلمة المرور">
    <button class="btn" style="width:100%;margin-top:8px" id="doLogin">دخول</button>
    <button style="width:100%;margin-top:8px;background:transparent;color:#aaa;border:0" id="closeLogin">إلغاء</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const API={health:'/api/health',me:'/api/auth/me',login:'/api/auth/login',logout:'/api/auth/logout',feed:'/api/feed',live:'/api/live',games:'/api/games',owner:'/owner'};
const state={user:null,games:[],feed:[],live:[]};
const $=s=>document.querySelector(s);

function toast(msg){const t=$('#toast');t.textContent=msg;t.classList.add('show');clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove('show'),2500)}
async function req(url,opt={}){const r=await fetch(url,{credentials:'include',headers:{'Content-Type':'application/json',...(opt.headers||{})},...opt});let b=null;try{b=await r.json()}catch{}if(!r.ok)throw new Error(b?.message||b?.error||`HTTP ${r.status}`);return b}
function arr(v){if(Array.isArray(v))return v;for(const k of ['items','data','games','posts','streams'])if(Array.isArray(v?.[k]))return v[k];return[]}
function esc(v=''){return String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'","&#039;")}

async function health(){try{await req(API.health);$('#health').textContent='متصل بالخدمات الحقيقية'}catch{$('#health').textContent='الخدمة غير متاحة'}}
async function session(){try{const d=await req(API.me);state.user=d.user||d}catch{state.user=null}applyRole()}
function applyRole(){const role=String(state.user?.role||'').toUpperCase();document.body.classList.toggle('is-owner',role==='SUPREME_OWNER');$('#loginBtn').textContent=state.user?'تسجيل الخروج':'تسجيل الدخول';$('#accountBtn').textContent=(state.user?.name||'م').slice(0,1)}

async function loadGames(){try{state.games=arr(await req(API.games))}catch{state.games=[]}renderGames()}
function renderGames(){const root=$('#gamesGrid');root.innerHTML='';if(!state.games.length){root.innerHTML='<div class="empty">لا توجد ألعاب منشورة حالياً.</div>';return}
state.games.slice(0,9).forEach(g=>{const url=g.public_url||g.game_path||g.url||'';const e=document.createElement('article');e.className='media';e.innerHTML=`<div class="thumb">🎮</div><div class="info"><strong>${esc(g.name||g.game_name||'لعبة مجد')}</strong><br><small>${esc(g.status||g.genre||'جاهزة')}</small><div style="margin-top:10px"><button class="btn play" ${url?'':'disabled'}>تشغيل</button></div></div>`;e.querySelector('.play')?.addEventListener('click',()=>{if(url)location.href=url});root.appendChild(e)})}

async function loadFeed(){try{state.feed=arr(await req(API.feed))}catch{state.feed=[]}renderFeed()}
function renderFeed(){const root=$('#feed');root.innerHTML='';if(!state.feed.length){root.innerHTML='<div class="empty">لا توجد منشورات حقيقية حتى الآن.</div>';return}
state.feed.slice(0,8).forEach(p=>{const e=document.createElement('article');e.className='post';e.innerHTML=`<strong>${esc(p.author_name||p.author||'مستخدم مجد')}</strong><p>${esc(p.text||p.content||'')}</p><span class="muted">♡ ${Number(p.likes||0)} &nbsp; 💬 ${Number(p.comments||0)}</span>`;root.appendChild(e)})}

async function loadLive(){try{state.live=arr(await req(API.live))}catch{state.live=[]}const root=$('#liveGrid');root.innerHTML='';if(!state.live.length){root.innerHTML='<div class="empty">لا يوجد بث مباشر الآن.</div>';return}
state.live.slice(0,3).forEach(x=>{const e=document.createElement('article');e.className='media';e.innerHTML=`<div class="thumb">🔴</div><div class="info"><strong>${esc(x.title||'بث مباشر')}</strong><br><small>${esc(x.creator||x.author||'')}</small></div>`;root.appendChild(e)})}

$('#loginBtn').onclick=async()=>{if(state.user){try{await req(API.logout,{method:'POST'})}catch{}state.user=null;applyRole();return}$('#loginModal').classList.add('open')}
$('#closeLogin').onclick=()=>$('#loginModal').classList.remove('open')
$('#doLogin').onclick=async()=>{try{const d=await req(API.login,{method:'POST',body:JSON.stringify({email:$('#email').value.trim(),password:$('#password').value})});state.user=d.user||d;applyRole();$('#loginModal').classList.remove('open');toast('تم تسجيل الدخول')}catch(e){toast(e.message)}}
$('#ownerCenter').onclick=()=>{if(String(state.user?.role||'').toUpperCase()==='SUPREME_OWNER')location.href=API.owner}
$('#exploreGames').onclick=$('#gamesNav').onclick=()=>$('#gamesSection').scrollIntoView({behavior:'smooth'})
$('#publishPost').onclick=async()=>{if(!state.user){$('#loginModal').classList.add('open');return}const text=$('#composer').value.trim();if(!text)return;try{await req(API.feed,{method:'POST',body:JSON.stringify({text})});$('#composer').value='';await loadFeed();toast('تم النشر')}catch(e){toast(e.message)}}

async function boot(){await Promise.allSettled([health(),session(),loadGames(),loadFeed(),loadLive()])}
boot()
</script>
</body>
</html>"""

def build() -> Dict[str, Any]:
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(CONFIG_FILE, build_config())
    write_text(INDEX_FILE, build_html())
    return {
        "success": INDEX_FILE.exists() and INDEX_FILE.stat().st_size > 0,
        "status": "PUBLIC_PLATFORM_BUILT",
        "file": str(INDEX_FILE),
        "config": str(CONFIG_FILE),
        "generated_at": utc_now()
    }

def main() -> int:
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1

if __name__ == "__main__":
    raise SystemExit(main())
  
