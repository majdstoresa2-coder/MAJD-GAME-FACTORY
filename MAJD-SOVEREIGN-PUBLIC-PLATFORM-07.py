#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-SOVEREIGN-PUBLIC-PLATFORM-07.py
====================================
OFFICIAL SOVEREIGN PUBLIC PLATFORM BUILDER
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
VERSION = "2.0.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp.replace(path)


def build_config() -> Dict[str, Any]:
    return {
        "platform": PLATFORM_NAME,
        "version": VERSION,
        "generated_at": utc_now(),
        "owner_panel": "/owner",
        "api": {
            "health": "/api/health",
            "status": "/api/status",
            "dashboard": "/api/dashboard",
        },
        "features": {
            "auth": False,
            "feed": False,
            "live": False,
            "games": False,
            "media": False,
            "ai": False,
        },
    }


def build_html() -> str:
    return r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#060b12">

<title>MAJD — المنصة الرسمية السيادية</title>

<style>
:root{
  --bg:#060b12;
  --panel:#0b1520;
  --panel2:#0f1b29;
  --line:#1d2a38;
  --text:#edf2f7;
  --muted:#8896a8;
  --gold:#c99a35;
  --gold2:#e0ba63;
  --gold3:#f1d58d;
  --red:#ff365f;
  --blue:#268cff;
}

*{box-sizing:border-box}

html,body{
  margin:0;
  min-height:100%;
  background:var(--bg);
  color:var(--text);
  font-family:"Segoe UI",Tahoma,Arial,sans-serif;
}

body{overflow-x:hidden}

button,input{font:inherit}
button{cursor:pointer}

.app{
  min-height:100vh;
  display:grid;
  grid-template-columns:235px minmax(0,1fr) 265px;
  gap:14px;
  padding:14px;
  direction:ltr;
}

.sidebar,.main,.rightbar{direction:rtl}

.sidebar,.rightbar{
  background:linear-gradient(180deg,#0a131e,#08111a);
  border:1px solid var(--line);
  border-radius:16px;
}

.sidebar{
  position:sticky;
  top:14px;
  height:calc(100vh - 28px);
  overflow:auto;
  padding:12px;
}

.rightbar{
  position:sticky;
  top:14px;
  height:calc(100vh - 28px);
  overflow:auto;
  padding:12px;
}

.main{min-width:0}

.brand{
  display:flex;
  align-items:center;
  gap:9px;
  padding:4px 4px 12px;
  border-bottom:1px solid var(--line);
}

.crown{font-size:20px;color:var(--gold2)}

.brand-name{
  color:var(--gold3);
  font-size:20px;
  font-weight:900;
  letter-spacing:1px;
}

.profile{
  margin-top:12px;
  padding:10px;
  border:1px solid var(--line);
  border-radius:14px;
  background:#0c1723;
}

.profile-top{
  display:flex;
  align-items:center;
  gap:10px;
}

.avatar{
  width:44px;
  height:44px;
  border-radius:50%;
  display:grid;
  place-items:center;
  background:linear-gradient(135deg,#1d2b3a,#4a3512);
  border:2px solid rgba(224,186,99,.55);
  font-weight:900;
}

.profile-info strong{
  display:block;
  font-size:13px;
}

.profile-info small{
  color:var(--muted);
  font-size:11px;
}

.level{
  margin-top:9px;
  height:7px;
  border-radius:999px;
  overflow:hidden;
  background:#08111b;
  border:1px solid #172331;
}

.level span{
  display:block;
  width:78%;
  height:100%;
  background:linear-gradient(90deg,var(--gold),var(--gold3));
}

.level-info{
  margin-top:5px;
  display:flex;
  justify-content:space-between;
  color:var(--muted);
  font-size:10px;
}

.nav{
  margin-top:12px;
  display:grid;
  gap:3px;
}

.nav button{
  width:100%;
  border:0;
  background:transparent;
  color:#c9d2dc;
  padding:9px 10px;
  border-radius:10px;
  text-align:right;
  font-size:13px;
}

.nav button:hover,.nav button.active{
  background:linear-gradient(90deg,rgba(201,154,53,.19),rgba(201,154,53,.05));
  color:var(--gold3);
}

.icon{
  display:inline-block;
  width:25px;
  text-align:center;
}

.badge{
  float:left;
  background:#ca1640;
  color:white;
  border-radius:999px;
  padding:1px 6px;
  font-size:8px;
}

.owner{color:var(--gold2)!important}

.topbar{
  position:sticky;
  top:14px;
  z-index:30;
  height:48px;
  display:flex;
  align-items:center;
  gap:10px;
  padding:7px 10px;
  background:rgba(10,19,30,.94);
  backdrop-filter:blur(14px);
  border:1px solid var(--line);
  border-radius:14px;
}

.search{
  flex:1;
  display:flex;
  align-items:center;
  gap:8px;
  background:#08111a;
  border:1px solid var(--line);
  border-radius:999px;
  padding:0 12px;
}

.search input{
  width:100%;
  background:transparent;
  border:0;
  outline:0;
  color:white;
  padding:8px 0;
  font-size:12px;
}

.create{
  border:0;
  border-radius:10px;
  background:linear-gradient(135deg,#b68124,#e4bd63);
  color:#0a0f15;
  font-weight:900;
  padding:8px 13px;
}

.top-icon{
  width:34px;
  height:34px;
  border-radius:9px;
  border:1px solid var(--line);
  background:#0c1723;
  color:#cfd7e0;
}

.stories{
  margin-top:12px;
  display:flex;
  gap:10px;
  overflow:auto;
  padding:10px;
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:14px;
}

.story{
  min-width:60px;
  text-align:center;
}

.story-ring{
  width:52px;
  height:52px;
  margin:auto;
  padding:2px;
  border-radius:50%;
  background:linear-gradient(135deg,#d5a338,#8047ff,#ff3768);
}

.story-inner{
  width:100%;
  height:100%;
  border-radius:50%;
  display:grid;
  place-items:center;
  background:#142333;
  border:2px solid #08111a;
}

.story small{
  display:block;
  margin-top:5px;
  color:#c6d0da;
  font-size:9px;
  white-space:nowrap;
}

.composer{
  margin-top:12px;
  padding:10px;
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:14px;
}

.composer-main{
  display:flex;
  align-items:center;
  gap:8px;
}

.composer-input{
  flex:1;
  padding:10px 13px;
  background:#08111a;
  border:1px solid var(--line);
  border-radius:999px;
  color:#77869a;
  font-size:12px;
}

.composer-actions{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  gap:5px;
  margin-top:9px;
  padding-top:9px;
  border-top:1px solid var(--line);
}

.composer-actions button{
  border:0;
  background:transparent;
  color:#aeb8c3;
  font-size:10px;
}

.tabs{
  display:flex;
  gap:20px;
  margin:12px 0 8px;
  padding:0 6px;
  color:#8897a8;
  font-size:11px;
}

.tabs .active{
  color:var(--gold2);
  padding-bottom:7px;
  border-bottom:2px solid var(--gold2);
}

.post{
  margin-bottom:12px;
  overflow:hidden;
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:14px;
}

.post-header{
  display:flex;
  align-items:center;
  gap:8px;
  padding:10px;
}

.post-user{flex:1}

.post-user strong{
  display:block;
  font-size:12px;
}

.post-user small{
  color:var(--muted);
  font-size:10px;
}

.post-text{
  padding:0 10px 10px;
  color:#d7dee7;
  font-size:12px;
  line-height:1.7;
}

.post-media{
  min-height:300px;
  display:grid;
  place-items:center;
  background:
    radial-gradient(circle at 72% 48%,rgba(255,105,30,.48),transparent 19%),
    linear-gradient(135deg,#07111b,#23140c 55%,#4a220f);
}

.post-media.ramadan{
  background:
    radial-gradient(circle,rgba(243,196,92,.35),transparent 30%),
    linear-gradient(135deg,#07111b,#3a2b13);
}

.post-media.car{
  background:
    radial-gradient(circle at 50% 70%,rgba(39,133,222,.3),transparent 28%),
    linear-gradient(180deg,#09131e,#131d27,#0c0f15);
}

.play{
  width:58px;
  height:58px;
  border-radius:50%;
  border:2px solid white;
  background:rgba(0,0,0,.4);
  color:white;
  font-size:22px;
}

.media-title{
  color:#f0d99b;
  font-size:32px;
  font-weight:900;
}

.post-actions{
  display:flex;
  gap:18px;
  padding:9px 11px;
  border-top:1px solid var(--line);
  color:#8b98a8;
  font-size:11px;
}

.shelf{
  margin-top:12px;
  padding:10px;
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:14px;
}

.shelf-title{
  display:flex;
  justify-content:space-between;
  margin-bottom:8px;
}

.shelf-title strong{font-size:13px}

.shelf-title span{
  color:#5da8ff;
  font-size:10px;
}

.media-row{
  display:grid;
  grid-template-columns:repeat(5,minmax(0,1fr));
  gap:8px;
}

.media-card{
  overflow:hidden;
  background:#0d1824;
  border:1px solid var(--line);
  border-radius:10px;
}

.media-thumb{
  aspect-ratio:16/9;
  display:grid;
  place-items:center;
  font-size:28px;
  background:linear-gradient(135deg,#15273a,#4a3014);
}

.media-info{padding:7px}

.media-info strong{
  display:block;
  font-size:10px;
}

.media-info small{
  color:var(--muted);
  font-size:9px;
}

.right-section{
  padding-bottom:12px;
  margin-bottom:12px;
  border-bottom:1px solid var(--line);
}

.right-section h3{
  margin:0 0 9px;
  font-size:13px;
}

.live-item,.channel,.event{
  display:flex;
  align-items:center;
  gap:8px;
  margin:8px 0;
}

.live-thumb{
  width:72px;
  height:44px;
  border-radius:8px;
  display:grid;
  place-items:center;
  background:linear-gradient(135deg,#3b1b15,#d05235);
}

.item-info{flex:1}

.item-info strong{
  display:block;
  font-size:10px;
}

.item-info small{
  color:var(--muted);
  font-size:9px;
}

.live-label{
  background:#d9284d;
  color:white;
  border-radius:4px;
  padding:2px 5px;
  font-size:8px;
}

.trend{
  display:flex;
  gap:8px;
  margin:7px 0;
  color:#b9c4cf;
  font-size:10px;
}

.trend b{color:var(--gold2)}

.channel-avatar{
  width:34px;
  height:34px;
  border-radius:50%;
  display:grid;
  place-items:center;
  background:#162638;
  border:1px solid #2b3d50;
}

.follow{
  margin-right:auto;
  border:1px solid #856523;
  border-radius:7px;
  background:transparent;
  color:var(--gold2);
  padding:4px 7px;
  font-size:9px;
}

.ai{
  padding:14px;
  text-align:center;
  background:
    radial-gradient(circle at 50% 30%,rgba(73,143,255,.2),transparent 30%),
    var(--panel);
  border:1px solid var(--line);
  border-radius:14px;
}

.ai-orb{
  width:64px;
  height:64px;
  margin:0 auto 10px;
  border-radius:50%;
  background:radial-gradient(circle,#7ed5ff 0 18%,#5b5cff 36%,#11193b 65%);
  box-shadow:0 0 22px rgba(91,92,255,.45);
}

.ai button{
  border:0;
  border-radius:8px;
  padding:8px 12px;
  background:linear-gradient(135deg,#b68124,#e4bd63);
  font-weight:900;
}

.mobile-nav{display:none}

@media(max-width:1150px){
  .app{grid-template-columns:210px minmax(0,1fr)}
  .rightbar{display:none}
}

@media(max-width:760px){
  body{padding-bottom:65px}
  .app{display:block;padding:8px}
  .sidebar{display:none}
  .topbar{top:8px}
  .media-row{grid-template-columns:repeat(2,minmax(0,1fr))}
  .post-media{min-height:240px}

  .mobile-nav{
    position:fixed;
    left:0;
    right:0;
    bottom:0;
    z-index:100;
    display:grid;
    grid-template-columns:repeat(5,1fr);
    background:#08111a;
    border-top:1px solid var(--line);
    padding:7px 8px calc(7px + env(safe-area-inset-bottom));
  }

  .mobile-nav button{
    border:0;
    background:transparent;
    color:#9ba8b7;
    font-size:10px;
  }

  .mobile-nav button.active{color:var(--gold2)}
}
</style>
</head>

<body>

<div class="app">

<aside class="sidebar">

<div class="brand">
<span class="crown">♛</span>
<span class="brand-name">MAJD</span>
</div>

<div class="profile">
<div class="profile-top">
<div class="avatar">م</div>
<div class="profile-info">
<strong>MAJD KING</strong>
<small>@majd.king</small>
</div>
</div>

<div class="level"><span></span></div>

<div class="level-info">
<span>المستوى 99</span>
<span>78,540 / 100,000 XP</span>
</div>
</div>

<nav class="nav">

<button class="active"><span class="icon">⌂</span>الرئيسية</button>
<button><span class="icon">◌</span>For You</button>
<button><span class="icon">♧</span>المتابعة</button>
<button><span class="icon">◉</span>القصص <span class="badge">NEW</span></button>
<button><span class="icon">S</span>Shorts</button>
<button><span class="icon">▣</span>الفيديوهات</button>
<button><span class="icon">●</span>البث المباشر <span class="badge">LIVE</span></button>
<button><span class="icon">▤</span>القنوات</button>
<button><span class="icon">◫</span>الأفلام <span class="badge">NEW</span></button>
<button><span class="icon">▥</span>المسلسلات</button>
<button><span class="icon">🏆</span>الفعاليات</button>
<button><span class="icon">🎮</span>الألعاب</button>
<button><span class="icon">✉</span>الرسائل</button>
<button><span class="icon">👥</span>المجموعات</button>
<button><span class="icon">🏅</span>الإنجازات</button>
<button><span class="icon">♡</span>المحفوظات</button>
<button><span class="icon">🔔</span>الإشعارات <span class="badge">12</span></button>
<button><span class="icon">☻</span>المحفظة</button>
<button><span class="icon">⚙</span>الإعدادات</button>

<button class="owner" id="ownerCenter">
<span class="icon">♛</span>
مركز المالك
</button>

</nav>
</aside>

<main class="main">

<header class="topbar">
<div class="search">
<span>⌕</span>
<input placeholder="ابحث عن محتوى، قنوات، مستخدمين...">
</div>

<button class="create">+ إنشاء</button>
<button class="top-icon">🔔</button>
<button class="top-icon">✉</button>
<div class="avatar" style="width:34px;height:34px">م</div>
</header>

<section class="stories">

<div class="story">
<div class="story-ring"><div class="story-inner">＋</div></div>
<small>إنشاء قصة</small>
</div>

<div class="story">
<div class="story-ring"><div class="story-inner">م</div></div>
<small>أنت</small>
</div>

<div class="story">
<div class="story-ring"><div class="story-inner">♛</div></div>
<small>MAJD Official</small>
</div>

<div class="story">
<div class="story-ring"><div class="story-inner">🐉</div></div>
<small>Dragon Slayer</small>
</div>

<div class="story">
<div class="story-ring"><div class="story-inner">H</div></div>
<small>HeroKSA</small>
</div>

<div class="story">
<div class="story-ring"><div class="story-inner">🎮</div></div>
<small>MAJD Gamer</small>
</div>

<div class="story">
<div class="story-ring"><div class="story-inner">م</div></div>
<small>محمد</small>
</div>

</section>

<section class="composer">
<div class="composer-main">
<div class="avatar" style="width:38px;height:38px">م</div>
<div class="composer-input">ما الذي تفكر فيه يا MAJD KING؟</div>
</div>

<div class="composer-actions">
<button>✎ منشور</button>
<button>● بث مباشر</button>
<button>▣ قصة</button>
<button>▶ فيديو</button>
<button>▧ صورة</button>
</div>
</section>

<div class="tabs">
<span class="active">لك</span>
<span>المتابعة</span>
<span>الألعاب</span>
<span>مقترح</span>
</div>

<article class="post">

<div class="post-header">
<div class="avatar">🐉</div>
<div class="post-user">
<strong>Dragon Slayer</strong>
<small>@dragon.slayer · الآن</small>
</div>
</div>

<div class="post-text">
أقوى لحظة في المعركة العالمية اليوم 🔥
</div>

<div class="post-media">
<button class="play">▶</button>
</div>

<div class="post-actions">
<span>♥ 2.4K</span>
<span>💬 156</span>
<span>↗ 278</span>
<span>⇩ 24.5K</span>
</div>

</article>

<article class="post">

<div class="post-header">
<div class="avatar">♛</div>
<div class="post-user">
<strong>MAJD Official</strong>
<small>@majd.official · منذ ساعة</small>
</div>
</div>

<div class="post-text">
إعلان الموسم الرمضاني لمجد ✨
فعاليات وبطولات وأفلام ومسلسلات حصرية.
</div>

<div class="post-media ramadan">
<div class="media-title">رمضان مجد</div>
</div>

<div class="post-actions">
<span>♥ 5.8K</span>
<span>💬 320</span>
<span>↗ 610</span>
<span>⇩ 58.1K</span>
</div>

</article>

<article class="post">

<div class="post-header">
<div class="avatar">🎮</div>
<div class="post-user">
<strong>MAJD Gamer</strong>
<small>@majd.gamer · منذ ساعة</small>
</div>
</div>

<div class="post-text">ليلة خرافية مع الشباب 🔥</div>

<div class="post-media car">
<div class="media-title">🏎️</div>
</div>

<div class="post-actions">
<span>♥ 12.4K</span>
<span>💬 312</span>
<span>↗ 851</span>
</div>

</article>

<section class="shelf">

<div class="shelf-title">
<strong>مقترح لك</strong>
<span>عرض الكل</span>
</div>

<div class="media-row">

<div class="media-card">
<div class="media-thumb">🏙️</div>
<div class="media-info">
<strong>خريطة الهلال</strong>
<small>MAJD Pro</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">⚔️</div>
<div class="media-info">
<strong>الأغنية الرسمية</strong>
<small>MAJD Music</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🐉</div>
<div class="media-info">
<strong>أقوى 10 لحظات</strong>
<small>MAJD Top</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🧙</div>
<div class="media-info">
<strong>مغامرة خيالية</strong>
<small>Pro Player</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🏹</div>
<div class="media-info">
<strong>أساطير مجد</strong>
<small>الموسم 2</small>
</div>
</div>

</div>
</section>

<section class="shelf">

<div class="shelf-title">
<strong>أحدث الأفلام</strong>
<span>عرض الكل</span>
</div>

<div class="media-row">

<div class="media-card">
<div class="media-thumb">⚔️</div>
<div class="media-info">
<strong>قلب الملك</strong>
<small>أكشن</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🦅</div>
<div class="media-info">
<strong>صقور الأبطال</strong>
<small>مغامرات</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🐲</div>
<div class="media-info">
<strong>مملكة التنين</strong>
<small>خيال</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🛡️</div>
<div class="media-info">
<strong>أسطورة مجد</strong>
<small>الموسم 2</small>
</div>
</div>

<div class="media-card">
<div class="media-thumb">🏜️</div>
<div class="media-info">
<strong>فرسان الصحراء</strong>
<small>الموسم 1</small>
</div>
</div>

</div>
</section>

</main>

<aside class="rightbar">

<section class="right-section">
<h3>مباشر الآن</h3>

<div class="live-item">
<div class="live-thumb">🏆</div>
<div class="item-info">
<strong>MAJD Official Live</strong>
<small>8.4K مشاهد</small>
</div>
<span class="live-label">LIVE</span>
</div>

<div class="live-item">
<div class="live-thumb">🎮</div>
<div class="item-info">
<strong>HeroKSA</strong>
<small>3.1K مشاهد</small>
</div>
<span class="live-label">LIVE</span>
</div>

<div class="live-item">
<div class="live-thumb">🐉</div>
<div class="item-info">
<strong>Dragon Slayer</strong>
<small>2.7K مشاهد</small>
</div>
<span class="live-label">LIVE</span>
</div>

<div class="live-item">
<div class="live-thumb">🎧</div>
<div class="item-info">
<strong>MAJD Radio</strong>
<small>1.2K مشاهد</small>
</div>
<span class="live-label">LIVE</span>
</div>

</section>

<section class="right-section">

<h3>المتداول الآن</h3>

<div class="trend"><b>1</b><span>#بطولة_مجد_العالمية</span></div>
<div class="trend"><b>2</b><span>#رمضان_في_مجد</span></div>
<div class="trend"><b>3</b><span>#Dragon_Slayer</span></div>
<div class="trend"><b>4</b><span>#MAJD_Gamer</span></div>
<div class="trend"><b>5</b><span>#فجر_الملوك</span></div>

</section>

<section class="right-section">

<h3>قنوات مقترحة</h3>

<div class="channel">
<div class="channel-avatar">M</div>
<div class="item-info">
<strong>MAJD TV</strong>
<small>@majd.tv</small>
</div>
<button class="follow">متابعة</button>
</div>

<div class="channel">
<div class="channel-avatar">T</div>
<div class="item-info">
<strong>Tech MAJD</strong>
<small>@tech.majd</small>
</div>
<button class="follow">متابعة</button>
</div>

<div class="channel">
<div class="channel-avatar">S</div>
<div class="item-info">
<strong>MAJD Sports</strong>
<small>@majd.sports</small>
</div>
<button class="follow">متابعة</button>
</div>

<div class="channel">
<div class="channel-avatar">K</div>
<div class="item-info">
<strong>MAJD Kids</strong>
<small>@majd.kids</small>
</div>
<button class="follow">متابعة</button>
</div>

</section>

<section class="right-section">

<h3>الفعاليات القادمة</h3>

<div class="event">
<div class="live-thumb">🏆</div>
<div class="item-info">
<strong>بطولة مجد العالمية</strong>
<small>قريباً</small>
</div>
</div>

<div class="event">
<div class="live-thumb">🌙</div>
<div class="item-info">
<strong>حفل رمضان في مجد</strong>
<small>قريباً</small>
</div>
</div>

<div class="event">
<div class="live-thumb">🎬</div>
<div class="item-info">
<strong>عرض فيلم جديد</strong>
<small>قريباً</small>
</div>
</div>

</section>

<section class="ai">

<div class="ai-orb"></div>

<strong>ذكاء مجد الإبداعي</strong>

<p style="color:var(--muted);font-size:10px;line-height:1.7;">
مساعدك الذكي داخل منصة مجد
</p>

<button id="aiButton">
اسأل ذكاء مجد
</button>

</section>

</aside>

</div>

<nav class="mobile-nav">

<button class="active">
⌂
<br>
الرئيسية
</button>

<button>Shorts</button>

<button>＋</button>

<button>
▣
<br>
الاشتراكات
</button>

<button>
☰
<br>
المكتبة
</button>

</nav>

<script>

const API = {
    health: "/api/health",
    status: "/api/status",
    dashboard: "/api/dashboard",
    owner: "/owner"
};

async function api(url){

    const response = await fetch(
        url,
        {
            credentials:"include"
        }
    );

    let body = null;

    try{
        body = await response.json();
    }catch(_){}

    if(!response.ok){
        throw new Error(
            body?.message ||
            body?.error ||
            `HTTP ${response.status}`
        );
    }

    return body;
}

document
.getElementById("ownerCenter")
.addEventListener(
    "click",
    () => {
        location.href = API.owner;
    }
);

document
.getElementById("aiButton")
.addEventListener(
    "click",
    () => {
        alert(
            "واجهة ذكاء مجد جاهزة للربط بالخدمة الخلفية."
        );
    }
);

async function boot(){

    try{

        await api(API.health);

        document
        .documentElement
        .dataset
        .health = "online";

    }catch(_){

        document
        .documentElement
        .dataset
        .health = "offline";

    }
}

boot();

</script>

</body>
</html>'''


def build() -> Dict[str, Any]:

    PUBLIC_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_json(
        CONFIG_FILE,
        build_config(),
    )

    write_text(
        INDEX_FILE,
        build_html(),
    )

    return {
        "success":
            INDEX_FILE.exists()
            and INDEX_FILE.stat().st_size > 0,

        "status":
            "OFFICIAL_PUBLIC_PLATFORM_BUILT",

        "platform":
            PLATFORM_NAME,

        "version":
            VERSION,

        "file":
            str(INDEX_FILE),

        "config":
            str(CONFIG_FILE),

        "generated_at":
            utc_now(),
    }


def main() -> int:

    result = build()

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )

    return (
        0
        if result.get("success")
        else 1
    )


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
