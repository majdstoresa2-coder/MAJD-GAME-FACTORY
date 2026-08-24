#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-SOVEREIGN-PUBLIC-PLATFORM-07.py
====================================
OFFICIAL MAJD PUBLIC PLATFORM
REFERENCE-LOCKED UI BUILD
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
VERSION = "3.0.0"


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
        "ui": {
            "reference_locked": True,
            "direction": "rtl",
            "desktop_columns": 3,
            "theme": "majd-dark-gold",
        },
    }


def build_html() -> str:
    return r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#050a0f">
<title>MAJD — منصة مجد</title>

<style>
:root{
  --bg:#050a0f;
  --surface:#08131d;
  --surface2:#0a1722;
  --surface3:#0d1b27;
  --border:#182a39;
  --border2:#203646;
  --text:#eef3f7;
  --soft:#b6c0cb;
  --muted:#718090;
  --gold:#d5a73f;
  --gold2:#f0cb6c;
  --red:#e72954;
  --blue:#3a9cff;
  --green:#2ecf91;
  --purple:#ad50ff;
  --cyan:#21c9c3;
}

*{box-sizing:border-box}

html,body{
  margin:0;
  padding:0;
  min-height:100%;
  background:
    radial-gradient(circle at 50% -20%,#112331 0,transparent 28%),
    var(--bg);
  color:var(--text);
  font-family:"Segoe UI",Tahoma,Arial,sans-serif;
}

body{
  overflow-x:hidden;
}

button,input{
  font:inherit;
}

button{
  cursor:pointer;
}

a{
  color:inherit;
  text-decoration:none;
}

/* =========================================================
   MAIN DESKTOP FRAME
   ========================================================= */

.majd{
  width:min(100%,1540px);
  margin:0 auto;
  padding:12px 14px 76px;
  display:grid;
  grid-template-columns:252px minmax(560px,1fr) 272px;
  gap:12px;
  direction:ltr;
}

.sidebar,
.center,
.rightbar{
  direction:rtl;
}

.panel{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:13px;
}

/* =========================================================
   LEFT SIDEBAR
   ========================================================= */

.sidebar{
  min-width:0;
}

.sidebar-inner{
  position:sticky;
  top:12px;
}

.sidebar-main{
  padding:14px 12px 11px;
}

.logo{
  height:55px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:9px;
  border-bottom:1px solid var(--border);
  margin-bottom:12px;
}

.logo-crown{
  color:var(--gold2);
  font-size:25px;
}

.logo-word{
  color:#f1d078;
  font-family:Georgia,serif;
  font-weight:800;
  font-size:25px;
  letter-spacing:2px;
}

.profile{
  padding:12px;
  border:1px solid var(--border2);
  border-radius:13px;
  background:#091621;
  margin-bottom:11px;
}

.profile-head{
  display:flex;
  align-items:center;
  gap:10px;
}

.avatar{
  width:44px;
  height:44px;
  flex:0 0 44px;
  border-radius:50%;
  display:grid;
  place-items:center;
  color:#fff;
  background:linear-gradient(135deg,#172532,#493716);
  border:2px solid #8d7033;
  font-weight:900;
}

.profile-copy{
  min-width:0;
  flex:1;
}

.profile-copy strong{
  display:block;
  font-size:12px;
  line-height:1.4;
}

.profile-copy small{
  display:block;
  margin-top:2px;
  color:var(--muted);
  font-size:10px;
}

.level-row{
  margin-top:10px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  font-size:9px;
  color:var(--muted);
}

.level-label{
  color:var(--gold2);
}

.level-track{
  height:6px;
  background:#071018;
  border:1px solid #1d2c39;
  border-radius:99px;
  margin-top:6px;
  overflow:hidden;
}

.level-track span{
  display:block;
  width:78%;
  height:100%;
  background:linear-gradient(90deg,#b98320,#f0d17b);
}

.menu{
  display:grid;
  gap:2px;
}

.menu button{
  position:relative;
  width:100%;
  height:37px;
  border:0;
  border-radius:8px;
  padding:0 10px;
  background:transparent;
  color:#c7d0da;
  display:flex;
  align-items:center;
  gap:10px;
  text-align:right;
  font-size:11px;
}

.menu button:hover,
.menu button.active{
  color:#f1d27d;
  background:linear-gradient(90deg,rgba(211,165,61,.18),rgba(211,165,61,.06));
}

.menu-icon{
  width:22px;
  color:#a9b5c1;
  text-align:center;
  font-size:13px;
}

.menu button.active .menu-icon{
  color:var(--gold2);
}

.menu-badge{
  margin-right:auto;
  padding:2px 6px;
  min-width:23px;
  border-radius:20px;
  background:var(--red);
  color:white;
  text-align:center;
  font-size:7px;
  font-weight:800;
}

.owner-button{
  color:var(--gold2)!important;
}

.community{
  margin-top:10px;
  padding:10px;
}

.community h3{
  font-size:10px;
  margin:0 0 8px;
}

.game-mini-row{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:5px;
}

.game-mini{
  aspect-ratio:1.35;
  border-radius:6px;
  overflow:hidden;
  display:grid;
  place-items:center;
  background:
    radial-gradient(circle at 70% 25%,#ad7641,transparent 30%),
    linear-gradient(135deg,#234d75,#1a2632);
  font-size:22px;
}

.community a{
  display:inline-block;
  margin-top:7px;
  color:#4d9ee9;
  font-size:9px;
}

/* =========================================================
   TOPBAR
   ========================================================= */

.center{
  min-width:0;
}

.topbar{
  position:sticky;
  top:8px;
  z-index:50;
  height:52px;
  padding:7px 10px;
  display:flex;
  align-items:center;
  gap:8px;
  background:rgba(7,16,24,.96);
  backdrop-filter:blur(15px);
  border:1px solid var(--border);
  border-radius:13px;
}

.search{
  min-width:0;
  flex:1;
  height:35px;
  border:1px solid var(--border2);
  background:#07111a;
  border-radius:8px;
  display:flex;
  align-items:center;
  gap:8px;
  padding:0 11px;
}

.search-icon{
  color:#9aa7b5;
}

.search input{
  min-width:0;
  flex:1;
  border:0;
  outline:0;
  background:transparent;
  color:#e8eef4;
  font-size:10px;
}

.create{
  height:36px;
  min-width:79px;
  border:0;
  border-radius:7px;
  color:#161109;
  background:linear-gradient(135deg,#bd8a29,#efc966);
  font-size:11px;
  font-weight:900;
}

.top-button{
  width:36px;
  height:36px;
  padding:0;
  border:1px solid var(--border2);
  border-radius:8px;
  color:#d7e0e8;
  background:#0a1722;
  display:grid;
  place-items:center;
}

/* =========================================================
   STORIES
   ========================================================= */

.stories{
  margin-top:10px;
  min-height:103px;
  padding:11px 12px 8px;
}

.section-mini-head{
  display:flex;
  justify-content:space-between;
  margin-bottom:7px;
  font-size:8px;
}

.section-mini-head a{
  color:#489de9;
}

.story-list{
  display:flex;
  justify-content:space-around;
  gap:8px;
  overflow:hidden;
}

.story{
  width:65px;
  flex:0 0 65px;
  text-align:center;
}

.story-ring{
  width:51px;
  height:51px;
  margin:auto;
  padding:2px;
  border-radius:50%;
  background:linear-gradient(145deg,#e79d3c,#a239e7,#168fff);
}

.story-inner{
  width:100%;
  height:100%;
  display:grid;
  place-items:center;
  border-radius:50%;
  background:#11202d;
  border:2px solid #08131d;
  font-size:20px;
}

.story-name{
  display:block;
  margin-top:4px;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  color:#b9c4ce;
  font-size:8px;
}

/* =========================================================
   COMPOSER
   ========================================================= */

.composer{
  margin-top:10px;
  padding:10px 12px 8px;
}

.composer-line{
  display:flex;
  gap:8px;
  align-items:center;
}

.composer .avatar{
  width:36px;
  height:36px;
  flex-basis:36px;
}

.composer-box{
  flex:1;
  height:35px;
  padding:0 13px;
  display:flex;
  align-items:center;
  border-radius:18px;
  background:#09141e;
  border:1px solid #192b3a;
  color:#738293;
  font-size:10px;
}

.composer-actions{
  margin-top:9px;
  padding-top:8px;
  border-top:1px solid var(--border);
  display:grid;
  grid-template-columns:repeat(5,1fr);
}

.composer-actions button{
  border:0;
  background:transparent;
  color:#8d9ba8;
  font-size:9px;
}

.composer-actions button:nth-child(1){color:#4199e6}
.composer-actions button:nth-child(2){color:#ef4662}
.composer-actions button:nth-child(3){color:#39c493}
.composer-actions button:nth-child(4){color:#28b7b1}
.composer-actions button:nth-child(5){color:#bd62e4}

/* =========================================================
   FEED TABS
   ========================================================= */

.feed-tabs{
  height:43px;
  display:flex;
  align-items:end;
  gap:28px;
  padding:0 18px;
  color:#7d8b99;
  font-size:9px;
}

.feed-tab{
  height:31px;
  display:flex;
  align-items:center;
}

.feed-tab.active{
  color:#e9c76b;
  border-bottom:2px solid var(--gold);
}

/* =========================================================
   POSTS
   ========================================================= */

.post{
  margin-bottom:10px;
  overflow:hidden;
}

.post-head{
  min-height:53px;
  padding:9px 10px 6px;
  display:flex;
  align-items:flex-start;
  gap:8px;
}

.post-head .avatar{
  width:35px;
  height:35px;
  flex-basis:35px;
  font-size:14px;
}

.post-author{
  flex:1;
  min-width:0;
}

.post-author strong{
  font-size:10px;
}

.verified{
  color:#269cff;
  font-size:9px;
}

.post-author small{
  display:block;
  color:#6f7d8b;
  margin-top:1px;
  font-size:8px;
}

.more{
  color:#81909f;
  font-size:16px;
}

.post-text{
  padding:0 12px 8px;
  font-size:10px;
  line-height:1.65;
  color:#d5dce3;
}

.tags{
  color:#3f93d7;
}

.post-media{
  position:relative;
  width:calc(100% - 20px);
  margin:0 10px;
  min-height:285px;
  overflow:hidden;
  border-radius:7px;
  border:1px solid #1b2a37;
  display:grid;
  place-items:center;
}

/* Dragon reference image-like surface */
.dragon-media{
  background:
    radial-gradient(circle at 82% 50%,rgba(255,112,20,.95) 0,rgba(184,60,9,.48) 13%,transparent 30%),
    radial-gradient(circle at 63% 40%,rgba(255,181,62,.28),transparent 20%),
    linear-gradient(120deg,#071018 0%,#101014 45%,#3d180a 72%,#180b06 100%);
}

.dragon-media::before{
  content:"⚔";
  position:absolute;
  left:25%;
  bottom:18%;
  font-size:115px;
  color:#181a1d;
  text-shadow:0 0 18px rgba(255,126,32,.3);
  transform:rotate(-18deg);
}

.dragon-media::after{
  content:"🐉";
  position:absolute;
  right:17%;
  top:16%;
  font-size:110px;
  filter:saturate(.65) brightness(.75);
  opacity:.8;
}

.play-button{
  position:relative;
  z-index:5;
  width:57px;
  height:57px;
  padding:0 0 0 4px;
  display:grid;
  place-items:center;
  border:2px solid white;
  border-radius:50%;
  background:rgba(0,0,0,.42);
  color:#fff;
  font-size:21px;
}

.duration{
  position:absolute;
  bottom:6px;
  left:6px;
  padding:2px 4px;
  border-radius:3px;
  background:rgba(0,0,0,.8);
  color:#fff;
  font-size:7px;
}

.ramadan-media{
  min-height:268px;
  border-color:#725820;
  background:
    radial-gradient(circle at 50% 48%,rgba(218,168,61,.42),transparent 25%),
    radial-gradient(circle at 13% 50%,rgba(226,176,74,.14),transparent 22%),
    linear-gradient(110deg,#06101a,#15202b 42%,#2c210e);
}

.ramadan-media::before,
.ramadan-media::after{
  content:"🏮";
  position:absolute;
  top:30px;
  font-size:60px;
  opacity:.7;
}

.ramadan-media::before{right:30px}
.ramadan-media::after{left:30px}

.ramadan-title{
  position:relative;
  z-index:2;
  color:#f3cf6b;
  text-align:center;
  font-family:Georgia,"Times New Roman",serif;
  font-size:44px;
  font-weight:900;
  text-shadow:0 0 20px rgba(231,181,70,.35);
}

.ramadan-title small{
  display:block;
  font-size:17px;
  margin-top:2px;
}

.car-media{
  min-height:365px;
  width:68%;
  margin-left:auto;
  margin-right:auto;
  background:
    radial-gradient(circle at 50% 55%,rgba(26,105,188,.35),transparent 23%),
    linear-gradient(180deg,#08111a,#0b1824 52%,#050709);
}

.car-image{
  font-size:88px;
  filter:drop-shadow(0 0 24px rgba(44,139,234,.25));
}

.music-label{
  position:absolute;
  bottom:9px;
  right:9px;
  background:rgba(0,0,0,.76);
  border:1px solid #414a53;
  border-radius:5px;
  padding:5px 7px;
  font-size:8px;
}

.post-actions{
  height:37px;
  padding:0 13px;
  display:flex;
  align-items:center;
  gap:28px;
  border-top:1px solid var(--border);
  color:#7c8a98;
  font-size:9px;
}

.like-hot{
  color:#e93057;
}

/* =========================================================
   SHELVES
   ========================================================= */

.shelf{
  margin-top:11px;
  padding:11px;
}

.shelf-head{
  height:27px;
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
}

.shelf-head h3{
  margin:0;
  font-size:12px;
}

.shelf-head a{
  color:#4d9ce0;
  font-size:8px;
}

.category-tabs{
  display:flex;
  gap:17px;
  color:#7f8c99;
  font-size:8px;
}

.category-tabs .active{
  color:#15110a;
  background:#d8a941;
  border-radius:12px;
  padding:3px 10px;
}

.cards{
  display:grid;
  grid-template-columns:repeat(5,minmax(0,1fr));
  gap:7px;
}

.card{
  min-width:0;
  overflow:hidden;
  border:1px solid var(--border);
  border-radius:8px;
  background:#0a1621;
}

.card-cover{
  position:relative;
  aspect-ratio:1.48;
  display:grid;
  place-items:center;
  font-size:35px;
  background:
    radial-gradient(circle at 70% 25%,rgba(213,151,58,.45),transparent 30%),
    linear-gradient(135deg,#18334a,#3d2b17);
}

.card-copy{
  padding:6px;
}

.card-copy strong{
  display:block;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  font-size:8px;
}

.card-copy small{
  display:block;
  color:#71808e;
  margin-top:3px;
  font-size:7px;
}

.movie-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
  margin-top:11px;
}

.movie-panel{
  padding:11px;
}

.movie-list{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:7px;
}

.poster{
  overflow:hidden;
  border:1px solid var(--border);
  border-radius:8px;
  background:#0b1722;
}

.poster-art{
  aspect-ratio:.72;
  display:grid;
  place-items:center;
  font-size:42px;
  background:
    radial-gradient(circle at 50% 28%,rgba(220,160,62,.32),transparent 25%),
    linear-gradient(145deg,#142838,#402417);
}

.poster-info{
  padding:6px;
}

.poster-info strong{
  display:block;
  font-size:8px;
}

.poster-info small{
  display:block;
  color:#748290;
  font-size:7px;
  margin-top:3px;
}

.rating{
  color:#e3b443!important;
}

/* =========================================================
   RIGHTBAR
   ========================================================= */

.rightbar-inner{
  position:sticky;
  top:12px;
}

.right-section{
  padding:11px;
  margin-bottom:9px;
}

.right-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:9px;
}

.right-head h3{
  margin:0;
  font-size:12px;
}

.right-head a{
  color:#4c9ae0;
  font-size:8px;
}

.live{
  display:flex;
  align-items:center;
  gap:7px;
  margin-bottom:8px;
}

.live-thumb{
  position:relative;
  width:68px;
  height:45px;
  flex:0 0 68px;
  overflow:hidden;
  border-radius:6px;
  display:grid;
  place-items:center;
  background:
    radial-gradient(circle at 70% 30%,#e13d63,transparent 35%),
    linear-gradient(135deg,#552119,#172b3b);
  font-size:20px;
}

.live-badge{
  position:absolute;
  bottom:3px;
  right:3px;
  background:#e4264c;
  color:#fff;
  border-radius:3px;
  padding:2px 4px;
  font-size:6px;
}

.live-copy{
  flex:1;
  min-width:0;
}

.live-copy strong{
  display:block;
  font-size:8px;
}

.live-copy small{
  display:block;
  margin-top:3px;
  color:#73818e;
  font-size:7px;
}

.trending{
  display:grid;
  gap:9px;
}

.trend{
  display:grid;
  grid-template-columns:20px 1fr;
  gap:6px;
}

.trend-number{
  color:#c9d1da;
  font-size:9px;
  font-weight:900;
}

.trend strong{
  display:block;
  font-size:8px;
}

.trend small{
  color:#657481;
  font-size:7px;
}

.channel{
  display:flex;
  align-items:center;
  gap:7px;
  margin-bottom:9px;
}

.channel-avatar{
  width:34px;
  height:34px;
  flex:0 0 34px;
  display:grid;
  place-items:center;
  border-radius:50%;
  border:2px solid #3767c8;
  background:#162434;
  font-weight:900;
}

.channel-info{
  flex:1;
  min-width:0;
}

.channel-info strong{
  display:block;
  font-size:8px;
}

.channel-info small{
  display:block;
  color:#71808d;
  font-size:7px;
}

.follow{
  border:1px solid #9a7431;
  border-radius:5px;
  background:transparent;
  color:#d7ac52;
  padding:4px 8px;
  font-size:7px;
}

.event{
  position:relative;
  height:75px;
  margin-bottom:7px;
  padding:9px;
  overflow:hidden;
  border-radius:7px;
  display:flex;
  align-items:flex-end;
  background:
    linear-gradient(90deg,rgba(5,10,15,.2),rgba(5,10,15,.9)),
    radial-gradient(circle at 20% 50%,#b86e2c,transparent 32%),
    #172535;
}

.event strong{
  font-size:8px;
}

.event small{
  display:block;
  margin-top:3px;
  color:#b9c2ca;
  font-size:7px;
}

.ai-box{
  padding:15px 12px;
  text-align:center;
  background:
    radial-gradient(circle at 50% 42%,rgba(23,107,255,.2),transparent 30%),
    #08131d;
}

.ai-title{
  color:#e0b755;
  font-size:11px;
}

.ai-robot{
  width:110px;
  height:110px;
  margin:7px auto;
  position:relative;
  display:grid;
  place-items:center;
}

.ai-orbit{
  position:absolute;
  width:105px;
  height:48px;
  border:2px solid #3174d7;
  border-radius:50%;
  transform:rotate(-15deg);
  box-shadow:0 0 13px rgba(35,119,255,.4);
}

.ai-orbit.two{
  transform:rotate(25deg);
}

.ai-face{
  position:relative;
  z-index:3;
  width:62px;
  height:52px;
  border-radius:42% 42% 48% 48%;
  border:3px solid #4d8fff;
  background:#07152b;
  box-shadow:
    0 0 20px rgba(48,113,255,.6),
    inset 0 0 14px rgba(45,108,255,.35);
}

.ai-face::before{
  content:"•  •";
  color:#72d9ff;
  font-size:23px;
  line-height:39px;
}

.ai-box p{
  color:#8795a3;
  font-size:8px;
  line-height:1.6;
}

.ai-button{
  width:100%;
  border:0;
  border-radius:6px;
  padding:7px;
  background:linear-gradient(90deg,#c6922d,#efc762);
  color:#161109;
  font-size:8px;
  font-weight:900;
}

/* =========================================================
   BOTTOM NAV
   ========================================================= */

.bottom-nav{
  position:fixed;
  left:0;
  right:0;
  bottom:0;
  z-index:100;
  height:61px;
  display:grid;
  grid-template-columns:repeat(5,1fr);
  background:rgba(7,16,24,.98);
  border-top:1px solid #192b39;
}

.bottom-nav button{
  border:0;
  background:transparent;
  color:#788694;
  font-size:9px;
}

.bottom-nav .active{
  color:#e0b44e;
}

.bottom-plus{
  width:37px;
  height:37px;
  margin:auto;
  display:grid;
  place-items:center;
  border:1px solid #87929d!important;
  border-radius:50%;
  color:#d8e0e7!important;
  font-size:22px!important;
}

.copyright{
  grid-column:1/-1;
  text-align:center;
  color:#73808d;
  font-size:7px;
  padding:7px;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media(max-width:1200px){
  .majd{
    grid-template-columns:235px minmax(500px,1fr);
  }

  .rightbar{
    display:none;
  }
}

@media(max-width:800px){
  .majd{
    width:100%;
    display:block;
    padding:8px 8px 70px;
  }

  .sidebar{
    display:none;
  }

  .topbar{
    top:5px;
  }

  .stories{
    overflow:hidden;
  }

  .story-list{
    justify-content:flex-start;
    overflow-x:auto;
  }

  .post-media{
    min-height:230px;
  }

  .car-media{
    width:75%;
    min-height:330px;
  }

  .cards{
    grid-template-columns:repeat(5,145px);
    overflow-x:auto;
  }

  .movie-grid{
    grid-template-columns:1fr;
  }
}

@media(max-width:500px){
  .topbar{
    height:49px;
  }

  .top-button{
    display:none;
  }

  .create{
    min-width:68px;
  }

  .composer-actions{
    overflow-x:auto;
  }

  .post-media{
    width:100%;
    margin:0;
    border-left:0;
    border-right:0;
    border-radius:0;
  }

  .car-media{
    width:82%;
    margin:auto;
    border:1px solid #1b2a37;
    border-radius:7px;
  }
}
</style>
</head>

<body>

<div class="majd">

<!-- =========================================================
     LEFT SIDEBAR
     ========================================================= -->

<aside class="sidebar">
<div class="sidebar-inner">

<section class="panel sidebar-main">

<div class="logo">
  <span class="logo-crown">♛</span>
  <span class="logo-word">MAJD</span>
</div>

<div class="profile">
  <div class="profile-head">
    <div class="avatar">م</div>
    <div class="profile-copy">
      <strong>MAJD KING <span class="verified">●</span></strong>
      <small>@majd.king</small>
    </div>
  </div>

  <div class="level-row">
    <span class="level-label">المستوى 99</span>
    <span>78,540 / 100,000 XP</span>
  </div>

  <div class="level-track"><span></span></div>
</div>

<nav class="menu">
  <button class="active"><span class="menu-icon">⌂</span>الرئيسية</button>
  <button><span class="menu-icon">◉</span>For You</button>
  <button><span class="menu-icon">♧</span>المتابعة</button>
  <button><span class="menu-icon">◉</span>القصص <span class="menu-badge">NEW</span></button>
  <button><span class="menu-icon">S</span>Shorts</button>
  <button><span class="menu-icon">▣</span>الفيديوهات</button>
  <button><span class="menu-icon">●</span>البث المباشر <span class="menu-badge">LIVE</span></button>
  <button><span class="menu-icon">▤</span>القنوات</button>
  <button><span class="menu-icon">▣</span>الأفلام <span class="menu-badge">NEW</span></button>
  <button><span class="menu-icon">▥</span>المسلسلات</button>
  <button><span class="menu-icon">🏆</span>الفعاليات</button>
  <button><span class="menu-icon">🎮</span>الألعاب</button>
  <button><span class="menu-icon">▢</span>الرسائل</button>
  <button><span class="menu-icon">♧</span>المجموعات</button>
  <button><span class="menu-icon">🏆</span>الإنجازات</button>
  <button><span class="menu-icon">◷</span>المحفوظات</button>
  <button><span class="menu-icon">♧</span>الإشعارات <span class="menu-badge">12</span></button>
  <button><span class="menu-icon">☆</span>المفضلة</button>
  <button><span class="menu-icon">⚙</span>الإعدادات</button>
  <button class="owner-button" id="ownerCenter"><span class="menu-icon">♛</span>مركز المالك</button>
</nav>

</section>

<section class="panel community">
  <h3>ربط الألعاب بالمجتمع</h3>
  <div class="game-mini-row">
    <div class="game-mini">✈️</div>
    <div class="game-mini">⚔️</div>
    <div class="game-mini">🐉</div>
  </div>
  <a href="#">عرض الكل</a>
</section>

</div>
</aside>

<!-- =========================================================
     CENTER
     ========================================================= -->

<main class="center">

<header class="topbar">

  <div class="search">
    <span class="search-icon">⌕</span>
    <input placeholder="ابحث عن محتوى، قنوات، مستخدمين...">
  </div>

  <button class="create">+ إنشاء</button>
  <button class="top-button">♧</button>
  <button class="top-button">✉</button>
  <div class="avatar" style="width:35px;height:35px;flex-basis:35px">م</div>

</header>

<section class="panel stories">

  <div class="section-mini-head">
    <span></span>
    <a href="#">عرض الكل</a>
  </div>

  <div class="story-list">

    <div class="story">
      <div class="story-ring"><div class="story-inner">＋</div></div>
      <span class="story-name">إنشاء قصة</span>
    </div>

    <div class="story">
      <div class="story-ring"><div class="story-inner">م</div></div>
      <span class="story-name">أنت</span>
    </div>

    <div class="story">
      <div class="story-ring"><div class="story-inner">♛</div></div>
      <span class="story-name">MAJD Official</span>
    </div>

    <div class="story">
      <div class="story-ring"><div class="story-inner">🐉</div></div>
      <span class="story-name">Dragon Slayer</span>
    </div>

    <div class="story">
      <div class="story-ring"><div class="story-inner">H</div></div>
      <span class="story-name">HeroKSA</span>
    </div>

    <div class="story">
      <div class="story-ring"><div class="story-inner">🎮</div></div>
      <span class="story-name">MAJD Gamer</span>
    </div>

    <div class="story">
      <div class="story-ring"><div class="story-inner">م</div></div>
      <span class="story-name">محمد</span>
    </div>

  </div>

</section>

<section class="panel composer">

  <div class="composer-line">
    <div class="avatar">م</div>
    <div class="composer-box">بم تفكر يا MAJD KING؟</div>
  </div>

  <div class="composer-actions">
    <button>▧ منشور</button>
    <button>● بث مباشر</button>
    <button>▣ قصة</button>
    <button>▶ فيديو</button>
    <button>▧ صورة</button>
  </div>

</section>

<div class="feed-tabs">
  <div class="feed-tab active">لك</div>
  <div class="feed-tab">المتابعة</div>
  <div class="feed-tab">الألعاب</div>
  <div class="feed-tab">مقترح</div>
</div>

<!-- DRAGON POST -->

<article class="panel post">

  <div class="post-head">
    <div class="avatar">🐉</div>

    <div class="post-author">
      <strong>Dragon Slayer <span class="verified">●</span></strong>
      <small>@dragon.slayer · الآن</small>
    </div>

    <span class="more">•••</span>
  </div>

  <div class="post-text">
    أقوى لحظة في المعركة العالمية اليوم 🔥<br>
    من قلب المعركة إلى النصر<br>
    <span class="tags">#MAJD #Tournament #Victory</span>
  </div>

  <div class="post-media dragon-media">
    <button class="play-button">▶</button>
    <span class="duration">1:25</span>
  </div>

  <div class="post-actions">
    <span class="like-hot">♥ 2.4K</span>
    <span>◯ 156</span>
    <span>↗ 278</span>
    <span>⇩ 24.5K</span>
  </div>

</article>

<!-- RAMADAN POST -->

<article class="panel post">

  <div class="post-head">
    <div class="avatar">♛</div>

    <div class="post-author">
      <strong>MAJD Official <span class="verified">●</span></strong>
      <small>@majd.official · منذ ساعة</small>
    </div>

    <span class="more">•••</span>
  </div>

  <div class="post-text">
    ✨ إعلان الموسم الرمضاني لمجد 2025 ✨<br>
    مفاجآت، بطولات، أفلام ومسلسلات حصرية!<br>
    🌙 كل عام وأنتم بخير
  </div>

  <div class="post-media ramadan-media">
    <div class="ramadan-title">
      رمضان مجد
      <small>2025</small>
    </div>
  </div>

  <div class="post-actions">
    <span>♡ 5.8K</span>
    <span>◯ 320</span>
    <span>↗ 610</span>
    <span>⇩ 58.1K</span>
  </div>

</article>

<!-- CAR POST -->

<article class="panel post">

  <div class="post-head">
    <div class="avatar">🎮</div>

    <div class="post-author">
      <strong>MAJD Gamer <span class="verified">●</span></strong>
      <small>@majd.gamer · منذ ساعة</small>
    </div>

    <span class="more">•••</span>
  </div>

  <div class="post-text">
    ليلة خرافية مع الشباب 🔥😱
  </div>

  <div class="post-media car-media">
    <div class="car-image">🏎️</div>
    <span class="music-label">♫ الصوت - MAJD Gamer</span>
  </div>

  <div class="post-actions">
    <span>♥ 12.4K</span>
    <span>● 312</span>
    <span>↗ 851</span>
  </div>

</article>

<!-- RECOMMENDED -->

<section class="panel shelf">

  <div class="shelf-head">
    <h3>مقترح لك</h3>

    <div class="category-tabs">
      <span class="active">الكل</span>
      <span>ألعاب</span>
      <span>موسيقى</span>
      <span>ترفيه</span>
      <span>تعليمي</span>
      <span>أفلام</span>
      <span>مسلسلات</span>
    </div>
  </div>

  <div class="cards">

    <div class="card">
      <div class="card-cover">🏙️</div>
      <div class="card-copy">
        <strong>خريطة الهلال في كروك</strong>
        <small>🔥 Builder Pro · 5.2K مشاهدة</small>
      </div>
    </div>

    <div class="card">
      <div class="card-cover">⚔️</div>
      <div class="card-copy">
        <strong>الأغنية الرسمية للموسم</strong>
        <small>MAJD Music · 1.8M مشاهدة</small>
      </div>
    </div>

    <div class="card">
      <div class="card-cover">🐉</div>
      <div class="card-copy">
        <strong>أقوى 10 لحظات في تاريخ مجد</strong>
        <small>MAJD Top · 950K مشاهدة</small>
      </div>
    </div>

    <div class="card">
      <div class="card-cover">🧙</div>
      <div class="card-copy">
        <strong>شرح احتراف يومياً</strong>
        <small>Pro Player · 720K مشاهدة</small>
      </div>
    </div>

    <div class="card">
      <div class="card-cover">🏹</div>
      <div class="card-copy">
        <strong>مسلسل أساطير مجد</strong>
        <small>الموسم 2 · 450K مشاهدة</small>
      </div>
    </div>

  </div>

</section>

<div class="movie-grid">

<section class="panel movie-panel">

  <div class="shelf-head">
    <h3>أحدث الأفلام</h3>
  </div>

  <div class="movie-list">

    <div class="poster">
      <div class="poster-art">⚔️</div>
      <div class="poster-info">
        <strong>قلب الملك</strong>
        <small>أكشن · خيال</small>
        <small class="rating">★ 8.6</small>
      </div>
    </div>

    <div class="poster">
      <div class="poster-art">🦅</div>
      <div class="poster-info">
        <strong>رحلة الأبطال</strong>
        <small>مغامرات</small>
        <small class="rating">★ 8.2</small>
      </div>
    </div>

    <div class="poster">
      <div class="poster-art">🐲</div>
      <div class="poster-info">
        <strong>مملكة التنين</strong>
        <small>أكشن · خيال</small>
        <small class="rating">★ 9.1</small>
      </div>
    </div>

  </div>

</section>

<section class="panel movie-panel">

  <div class="shelf-head">
    <h3>المسلسلات الشائعة</h3>
  </div>

  <div class="movie-list">

    <div class="poster">
      <div class="poster-art">👑</div>
      <div class="poster-info">
        <strong>أساطير مجد</strong>
        <small>الموسم 2</small>
        <small class="rating">★ 9.0</small>
      </div>
    </div>

    <div class="poster">
      <div class="poster-art">🏍️</div>
      <div class="poster-info">
        <strong>فرسان الصحراء</strong>
        <small>الموسم 1</small>
        <small class="rating">★ 8.4</small>
      </div>
    </div>

    <div class="poster">
      <div class="poster-art">👩</div>
      <div class="poster-info">
        <strong>مدينة المستقبل</strong>
        <small>الموسم 1</small>
        <small class="rating">★ 7.8</small>
      </div>
    </div>

  </div>

</section>

</div>

</main>

<!-- =========================================================
     RIGHT SIDEBAR
     ========================================================= -->

<aside class="rightbar">

<div class="rightbar-inner">

<section class="panel right-section">

  <div class="right-head">
    <h3>مباشر الآن</h3>
    <a href="#">عرض الكل</a>
  </div>

  <div class="live">
    <div class="live-thumb">🏆<span class="live-badge">مباشر</span></div>
    <div class="live-copy">
      <strong>MAJD Official Live <span class="verified">●</span></strong>
      <small>👤 8.4K</small>
      <small>تغطية بطولة مجد العالمية</small>
    </div>
  </div>

  <div class="live">
    <div class="live-thumb">🎮<span class="live-badge">مباشر</span></div>
    <div class="live-copy">
      <strong>HeroKSA <span class="verified">●</span></strong>
      <small>👤 3.1K</small>
      <small>تحديات مع المتابعين</small>
    </div>
  </div>

  <div class="live">
    <div class="live-thumb">🐉<span class="live-badge">مباشر</span></div>
    <div class="live-copy">
      <strong>Dragon Slayer <span class="verified">●</span></strong>
      <small>👤 2.7K</small>
      <small>جلد التنين الأسطوري</small>
    </div>
  </div>

  <div class="live">
    <div class="live-thumb">🎧<span class="live-badge">مباشر</span></div>
    <div class="live-copy">
      <strong>MAJD Radio <span class="verified">●</span></strong>
      <small>👤 1.2K</small>
      <small>إذاعة مجد 24/7</small>
    </div>
  </div>

</section>

<section class="panel right-section">

  <div class="right-head">
    <h3>المتداول الآن</h3>
  </div>

  <div class="trending">

    <div class="trend">
      <span class="trend-number">1</span>
      <div><strong>#بطولة_مجد_العالمية</strong><small>24.5K منشور</small></div>
    </div>

    <div class="trend">
      <span class="trend-number">2</span>
      <div><strong>#رمضان_في_مجد</strong><small>18.7K منشور</small></div>
    </div>

    <div class="trend">
      <span class="trend-number">3</span>
      <div><strong>#Dragon_Slayer</strong><small>12.9K منشور</small></div>
    </div>

    <div class="trend">
      <span class="trend-number">4</span>
      <div><strong>#MAJD_Gamer</strong><small>9.8K منشور</small></div>
    </div>

    <div class="trend">
      <span class="trend-number">5</span>
      <div><strong>#مجد_الملوك</strong><small>7.3K منشور</small></div>
    </div>

  </div>

  <a href="#" style="display:block;margin-top:10px;color:#4c9ae0;font-size:8px">عرض المزيد</a>

</section>

<section class="panel right-section">

  <div class="right-head">
    <h3>قنوات مقترحة</h3>
    <a href="#">عرض الكل</a>
  </div>

  <div class="channel">
    <div class="channel-avatar">◉</div>
    <div class="channel-info">
      <strong>MAJD TV <span class="verified">●</span></strong>
      <small>@majd.tv</small>
      <small>1.2M مشترك</small>
    </div>
    <button class="follow">متابعة</button>
  </div>

  <div class="channel">
    <div class="channel-avatar">C</div>
    <div class="channel-info">
      <strong>Tech MAJD <span class="verified">●</span></strong>
      <small>@tech.majd</small>
      <small>890K مشترك</small>
    </div>
    <button class="follow">متابعة</button>
  </div>

  <div class="channel">
    <div class="channel-avatar">🔥</div>
    <div class="channel-info">
      <strong>MAJD Sports <span class="verified">●</span></strong>
      <small>@majd.sports</small>
      <small>760K مشترك</small>
    </div>
    <button class="follow">متابعة</button>
  </div>

  <div class="channel">
    <div class="channel-avatar">🌈</div>
    <div class="channel-info">
      <strong>MAJD Kids <span class="verified">●</span></strong>
      <small>@majd.kids</small>
      <small>650K مشترك</small>
    </div>
    <button class="follow">متابعة</button>
  </div>

</section>

<section class="panel right-section">

  <div class="right-head">
    <h3>الفعاليات القادمة</h3>
    <a href="#">عرض الكل</a>
  </div>

  <div class="event">
    <div>
      <strong>بطولة مجد العالمية FINALS</strong>
      <small>10 أكتوبر 2025 · 20:00</small>
    </div>
  </div>

  <div class="event">
    <div>
      <strong>حفل رمضان في مجد</strong>
      <small>10 مارس 2025 · 21:00</small>
    </div>
  </div>

  <div class="event">
    <div>
      <strong>عرض فيلم جديد — الجندي الأسطوري</strong>
      <small>15 مارس · 720K مهتم</small>
    </div>
  </div>

</section>

<section class="panel ai-box">

  <div class="ai-title">ذكاء مجد الإبداعي ✨</div>

  <div class="ai-robot">
    <div class="ai-orbit"></div>
    <div class="ai-orbit two"></div>
    <div class="ai-face"></div>
  </div>

  <p>
    اسألني عن المحتوى، ساعدني في إنشاء محتوى
    وتحسين تجربتك وزيادة تفاعل جمهورك
  </p>

  <button class="ai-button" id="aiButton">اسأل ذكاء مجد</button>

</section>

</div>

</aside>

</div>

<!-- =========================================================
     BOTTOM NAVIGATION
     ========================================================= -->

<nav class="bottom-nav">

  <button class="active">⌂<br>الرئيسية</button>
  <button>Shorts<br>◉</button>
  <button><span class="bottom-plus">＋</span></button>
  <button>▣<br>الاشتراكات</button>
  <button>▤<br>المكتبة</button>

</nav>

<script>
const API = {
  health: "/api/health",
  status: "/api/status",
  dashboard: "/api/dashboard",
  owner: "/owner"
};

async function api(url) {
  const response = await fetch(url, {
    credentials: "include"
  });

  let body = null;

  try {
    body = await response.json();
  } catch (_) {}

  if (!response.ok) {
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
  .addEventListener("click", () => {
    location.href = API.owner;
  });

document
  .getElementById("aiButton")
  .addEventListener("click", () => {
    alert("ذكاء مجد");
  });

document.querySelectorAll(".menu button").forEach(button => {
  button.addEventListener("click", function () {
    if (this.id === "ownerCenter") return;

    document.querySelectorAll(".menu button")
      .forEach(item => item.classList.remove("active"));

    this.classList.add("active");
  });
});

document.querySelectorAll(".feed-tab").forEach(tab => {
  tab.addEventListener("click", function () {
    document.querySelectorAll(".feed-tab")
      .forEach(item => item.classList.remove("active"));

    this.classList.add("active");
  });
});

document.querySelectorAll(".follow").forEach(button => {
  button.addEventListener("click", function () {
    const following = this.dataset.following === "true";

    this.dataset.following = following ? "false" : "true";
    this.textContent = following ? "متابعة" : "متابَع";
  });
});

async function boot() {
  try {
    await api(API.health);
    document.documentElement.dataset.health = "online";
  } catch (_) {
    document.documentElement.dataset.health = "offline";
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
            "OFFICIAL_MAJD_REFERENCE_UI_BUILT",

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

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
