import React, { useMemo, useState } from "react";

/**
 * ============================================================
 * MAJD OFFICIAL PLATFORM
 * 08-MAJD-MEDIA-SOCIAL-LIVE.jsx
 * MEDIA + SOCIAL + LIVE + CINEMA + SERIES + EVENTS
 * ============================================================
 *
 * منظومة مجد الإعلامية والاجتماعية الموحدة.
 *
 * 07 = OWNER / ADVANCED CONTROL PANEL
 * 08 = USER MEDIA / SOCIAL / LIVE EXPERIENCE
 *
 * هذا الملف مستقل ولا يعدل 07.
 * البيانات التجريبية الحالية تستبدل لاحقاً ببيانات Backend الحقيقية.
 * ============================================================
 */

const NAV = [
  ["home", "♛", "الرئيسية"],
  ["discover", "✦", "لك / اكتشف"],
  ["following", "♟", "المتابعة"],
  ["stories", "◉", "القصص"],
  ["shorts", "◆", "Shorts"],
  ["videos", "▶", "الفيديوهات"],
  ["live", "●", "البث المباشر"],
  ["channels", "▣", "القنوات"],
  ["cinema", "▤", "السينما"],
  ["series", "▦", "المسلسلات"],
  ["events", "♜", "الفعاليات والبطولات"],
  ["games", "🎮", "الألعاب"],
  ["messages", "✉", "الرسائل"],
  ["groups", "♟", "المجموعات"],
  ["achievements", "♛", "الإنجازات"],
  ["saved", "◇", "المحفوظات"],
  ["notifications", "◌", "الإشعارات"],
  ["favorites", "★", "المفضلة"],
  ["settings", "⚙", "الإعدادات"],
  ["ai", "✦", "ذكاء مجد"],
];

const STORIES = [
  ["أنت", "♛", "إضافة قصة"],
  ["MAJD Official", "M", "رسمي"],
  ["Dragon Slayer", "D", "جديد"],
  ["HeroKSA", "H", "مباشر"],
  ["MAJD Gamer", "G", "Gaming"],
  ["محمد", "م", "قصة"],
];

const LIVE = [
  {
    id: 1,
    title: "MAJD Official Live",
    creator: "MAJD Official",
    viewers: "8.4K",
    tag: "فعاليات مجد العالمية",
    color: "live-a",
  },
  {
    id: 2,
    title: "HeroKSA Live",
    creator: "HeroKSA",
    viewers: "3.1K",
    tag: "تحديات مع المتابعين",
    color: "live-b",
  },
  {
    id: 3,
    title: "Dragon Slayer Live",
    creator: "Dragon Slayer",
    viewers: "2.7K",
    tag: "تحدي التنين الأسطوري",
    color: "live-c",
  },
  {
    id: 4,
    title: "MAJD Radio Live",
    creator: "MAJD Radio",
    viewers: "1.2K",
    tag: "إذاعة مجد 24/7",
    color: "live-d",
  },
];

const POSTS = [
  {
    id: 1,
    user: "Dragon Slayer",
    handle: "@dragon.slayer",
    avatar: "D",
    verified: true,
    time: "منذ ساعة",
    text: "🔥 أقوى لحظة في البطولة العالمية اليوم. من يتحدى التنين؟",
    tags: "#MAJD  #Tournament  #Victory",
    media: "dragon",
    likes: 2400,
    comments: 156,
    shares: 278,
    views: "24.5K",
  },
  {
    id: 2,
    user: "MAJD Official",
    handle: "@majd.official",
    avatar: "M",
    verified: true,
    time: "منذ ساعة",
    text: "✨ إعلان الموسم الرمضاني لمجد. مفاجآت وبطولات وأفلام ومسلسلات ومحتوى حصري.",
    tags: "#MAJD  #Official",
    media: "ramadan",
    likes: 5800,
    comments: 320,
    shares: 610,
    views: "58.1K",
  },
  {
    id: 3,
    user: "MAJD Gamer",
    handle: "@majd.gamer",
    avatar: "G",
    verified: true,
    time: "منذ ساعتين",
    text: "🏎️🔥 لقطة جديدة من عالم مجد للألعاب.",
    tags: "#Gaming  #MAJD",
    media: "racing",
    likes: 12400,
    comments: 312,
    shares: 851,
    views: "91K",
  },
];

const CONTENT = [
  ["أساطير مجد", "مسلسل", "9.0", "fantasy"],
  ["فرسان الصحراء", "فيلم", "8.4", "desert"],
  ["مدينة المستقبل", "مسلسل", "8.8", "future"],
  ["مملكة التنين", "فيلم", "9.1", "dragon"],
  ["رحلة الأبطال", "فيلم", "8.2", "heroes"],
  ["تاريخ مجد", "وثائقي", "8.6", "history"],
];

const TRENDING = [
  ["#بطولة_مجد_العالمية", "24.5K منشور"],
  ["#رمضان_في_مجد", "18.7K منشور"],
  ["#Dragon_Slayer", "12.5K منشور"],
  ["#MAJD_Gamer", "9.8K منشور"],
  ["#مجد_الملوك", "7.3K منشور"],
];

const CHANNELS = [
  ["MAJD TV", "@majd.tv", "1.2M"],
  ["Tech MAJD", "@tech.majd", "890K"],
  ["MAJD Sports", "@majd.sports", "760K"],
  ["MAJD Kids", "@majd.kids", "650K"],
];

const EVENTS = [
  ["بطولة مجد العالمية", "FINALS", "سجل الآن"],
  ["احتفال رمضان في مجد", "LIVE EVENT", "تذكير"],
  ["عرض فيلم مجد الجديد", "PREMIERE", "تذكير"],
];

export default function MajdMediaSocialLive() {
  const [page, setPage] = useState("home");
  const [sidebar, setSidebar] = useState(false);
  const [query, setQuery] = useState("");
  const [composer, setComposer] = useState("");
  const [toast, setToast] = useState("");
  const [notifications, setNotifications] = useState(12);
  const [liked, setLiked] = useState({});
  const [following, setFollowing] = useState({});
  const [activeStory, setActiveStory] = useState(null);
  const [activeLive, setActiveLive] = useState(null);
  const [aiOpen, setAiOpen] = useState(false);

  const current =
    NAV.find(([id]) => id === page)?.[2] || "الرئيسية";

  const filteredContent = useMemo(() => {
    const q = query.trim().toLowerCase();

    if (!q) return CONTENT;

    return CONTENT.filter((item) =>
      item.join(" ").toLowerCase().includes(q)
    );
  }, [query]);

  function notify(message) {
    setToast(message);
    window.setTimeout(() => setToast(""), 2500);
  }

  function toggleLike(id) {
    setLiked((state) => ({
      ...state,
      [id]: !state[id],
    }));
  }

  function publishPost() {
    if (!composer.trim()) {
      notify("اكتب محتوى المنشور أولاً");
      return;
    }

    notify("تم تجهيز المنشور للنشر");
    setComposer("");
  }

  function renderHome() {
    return (
      <>
        <section className="stories panel">
          <div className="section-title">
            <strong>القصص</strong>
            <button>عرض الكل</button>
          </div>

          <div className="stories-row">
            {STORIES.map(([name, avatar, state], index) => (
              <button
                className="story"
                key={name}
                onClick={() =>
                  setActiveStory({ name, avatar, state, index })
                }
              >
                <span className="story-ring">
                  <span>{avatar}</span>
                </span>
                <b>{name}</b>
                <small>{state}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="composer panel">
          <div className="avatar owner-avatar">♛</div>

          <div className="composer-main">
            <input
              value={composer}
              onChange={(e) => setComposer(e.target.value)}
              placeholder="بم تفكر يا MAJD KING؟"
            />

            <div className="composer-actions">
              <button onClick={() => notify("إضافة صورة")}>
                ▧ صورة
              </button>
              <button onClick={() => notify("إضافة فيديو")}>
                ▶ فيديو
              </button>
              <button onClick={() => notify("إضافة قصة")}>
                ◉ قصة
              </button>
              <button onClick={() => setPage("live")}>
                ● بث مباشر
              </button>
              <button className="publish" onClick={publishPost}>
                نشر
              </button>
            </div>
          </div>
        </section>

        <div className="feed-tabs panel">
          <button className="active">لك</button>
          <button>المتابعة</button>
          <button>الألعاب</button>
          <button>مقترح</button>
        </div>

        {POSTS.map((post) => (
          <Post
            key={post.id}
            post={post}
            liked={liked[post.id]}
            onLike={() => toggleLike(post.id)}
            onNotify={notify}
          />
        ))}

        <section className="panel recommendation">
          <div className="section-title">
            <strong>مقترح لك</strong>
            <div className="categories">
              <button className="active">الكل</button>
              <button>مسلسلات</button>
              <button>أفلام</button>
              <button>ألعاب</button>
              <button>تعليمي</button>
              <button>ترفيه</button>
            </div>
          </div>

          <div className="content-grid">
            {filteredContent.map((item) => (
              <ContentCard key={item[0]} item={item} />
            ))}
          </div>
        </section>
      </>
    );
  }

  function renderLive() {
    return (
      <>
        <PageHeader
          title="البث المباشر"
          subtitle="البثوث والفعاليات المباشرة في مجتمع مجد"
        >
          <button
            className="gold-button"
            onClick={() => notify("تم فتح إعداد بث جديد")}
          >
            ● بدء بث جديد
          </button>
        </PageHeader>

        <div className="live-page-grid">
          {LIVE.map((live) => (
            <button
              key={live.id}
              className="live-big-card panel"
              onClick={() => setActiveLive(live)}
            >
              <div className={`live-cover ${live.color}`}>
                <span className="live-badge">LIVE</span>
                <span className="play-circle">▶</span>
              </div>

              <div className="live-info">
                <div className="avatar">M</div>
                <div>
                  <strong>{live.title}</strong>
                  <span>{live.creator}</span>
                  <small>
                    {live.viewers} مشاهد • {live.tag}
                  </small>
                </div>
              </div>
            </button>
          ))}
        </div>
      </>
    );
  }

  function renderCinema() {
    return (
      <>
        <PageHeader
          title="سينما مجد"
          subtitle="الأفلام والعروض والمحتوى المرئي"
        />

        <section className="cinema-hero panel">
          <div>
            <span className="gold-label">MAJD ORIGINAL</span>
            <h1>مملكة التنين</h1>
            <p>
              تجربة سينمائية داخل عالم مجد تجمع المغامرة
              والسيادة والخيال.
            </p>
            <button
              className="gold-button"
              onClick={() => notify("تشغيل العرض")}
            >
              ▶ مشاهدة الآن
            </button>
          </div>
          <div className="cinema-symbol">♛</div>
        </section>

        <ContentSection
          title="أحدث الأفلام"
          items={CONTENT.filter((x) => x[1] === "فيلم")}
        />
        <ContentSection title="الأكثر مشاهدة" items={CONTENT} />
      </>
    );
  }

  function renderSeries() {
    return (
      <>
        <PageHeader
          title="مسلسلات مجد"
          subtitle="المواسم والحلقات والمحتوى الأصلي"
        />

        <ContentSection
          title="المسلسلات الشائعة"
          items={CONTENT.filter((x) => x[1] === "مسلسل")}
        />

        <section className="panel seasons">
          <div className="section-title">
            <strong>أساطير مجد</strong>
            <span>الموسم 2</span>
          </div>

          {[1, 2, 3, 4].map((episode) => (
            <div className="episode" key={episode}>
              <div className="episode-thumb">▶</div>
              <div>
                <strong>الحلقة {episode}</strong>
                <p>
                  فصل جديد من قصة المملكة والصراع على السيادة.
                </p>
              </div>
              <button>مشاهدة</button>
            </div>
          ))}
        </section>
      </>
    );
  }

  function renderShorts() {
    return (
      <>
        <PageHeader
          title="MAJD Shorts"
          subtitle="المقاطع القصيرة والترند"
        />

        <div className="shorts-grid">
          {POSTS.concat(POSTS).map((post, index) => (
            <article className="short-card panel" key={index}>
              <div className={`short-media media-${post.media}`}>
                <span className="play-circle">▶</span>
              </div>
              <strong>{post.user}</strong>
              <p>{post.text}</p>
              <div>
                ♥ {post.likes.toLocaleString()}　◌ {post.comments}
              </div>
            </article>
          ))}
        </div>
      </>
    );
  }

  function renderEvents() {
    return (
      <>
        <PageHeader
          title="الفعاليات والبطولات"
          subtitle="فعاليات مجتمع وألعاب مجد"
        />

        <div className="events-grid">
          {EVENTS.map(([title, type, action], index) => (
            <article className="event-card panel" key={title}>
              <div className={`event-art event-${index + 1}`}>
                ♛
              </div>
              <span>{type}</span>
              <h3>{title}</h3>
              <p>
                فعالية رسمية ضمن منظومة MAJD للألعاب والإعلام
                والمجتمع.
              </p>
              <button
                className="gold-button"
                onClick={() => notify(`${action}: ${title}`)}
              >
                {action}
              </button>
            </article>
          ))}
        </div>
      </>
    );
  }

  function renderAI() {
    return (
      <>
        <PageHeader
          title="ذكاء مجد الإعلامي"
          subtitle="مساعد صناعة وإدارة المحتوى"
        />

        <section className="ai-center panel">
          <div className="ai-orb">✦</div>
          <h2>MAJD MEDIA AI</h2>
          <p>
            مركز الذكاء الاصطناعي للمحتوى والتصميم والأفكار
            والتحليل وإدارة التجربة الإعلامية.
          </p>

          <div className="ai-tools">
            {[
              ["✎", "كتابة محتوى"],
              ["▧", "تصميم"],
              ["▶", "فيديو"],
              ["◉", "تحليل ترند"],
              ["✦", "اقتراح محتوى"],
              ["◆", "مراجعة المحتوى"],
            ].map(([icon, title]) => (
              <button
                key={title}
                onClick={() => notify(`تشغيل: ${title}`)}
              >
                <span>{icon}</span>
                <strong>{title}</strong>
              </button>
            ))}
          </div>

          <button
            className="gold-button ai-button"
            onClick={() => setAiOpen(true)}
          >
            ✦ اسأل ذكاء مجد
          </button>
        </section>
      </>
    );
  }

  function renderGeneric() {
    return (
      <>
        <PageHeader
          title={current}
          subtitle={`قسم ${current} في منصة مجد الرسمية`}
        />

        <section className="panel generic-page">
          <div className="generic-crown">♛</div>
          <h2>{current}</h2>
          <p>
            هذا القسم جزء من منظومة MAJD الموحدة، ويتم ربط بياناته
            الحية مع خدمات المنصة.
          </p>
          <button
            className="gold-button"
            onClick={() => notify(`فتح ${current}`)}
          >
            فتح المركز
          </button>
        </section>
      </>
    );
  }

  function renderPage() {
    switch (page) {
      case "home":
      case "discover":
      case "following":
        return renderHome();
      case "live":
        return renderLive();
      case "cinema":
        return renderCinema();
      case "series":
        return renderSeries();
      case "shorts":
        return renderShorts();
      case "events":
        return renderEvents();
      case "ai":
        return renderAI();
      default:
        return renderGeneric();
    }
  }

  return (
    <div className="majd-media" dir="rtl">
      <style>{CSS}</style>

      {sidebar && (
        <button
          className="overlay"
          aria-label="إغلاق"
          onClick={() => setSidebar(false)}
        />
      )}

      <aside className={`sidebar ${sidebar ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-crown">♛</div>
          <div>
            <strong>MAJD</strong>
            <span>MEDIA • SOCIAL • LIVE</span>
          </div>
        </div>

        <div className="profile-card">
          <div className="profile-avatar">♛</div>
          <div>
            <strong>MAJD KING ✓</strong>
            <span>@majd.king</span>
          </div>
          <b>99</b>
        </div>

        <nav>
          {NAV.map(([id, icon, label]) => (
            <button
              key={id}
              className={page === id ? "active" : ""}
              onClick={() => {
                setPage(id);
                setSidebar(false);
              }}
            >
              <span>{icon}</span>
              {label}
              {id === "notifications" && notifications > 0 && (
                <i>{notifications}</i>
              )}
              {id === "live" && <em>LIVE</em>}
            </button>
          ))}
        </nav>

        <div className="sidebar-games">
          <strong>ربط الألعاب بالمجتمع</strong>
          <div>
            <span>♜</span>
            <span>⚔</span>
            <span>🐉</span>
          </div>
        </div>
      </aside>

      <header className="topbar">
        <button
          className="mobile-menu"
          onClick={() => setSidebar(true)}
        >
          ☰
        </button>

        <div className="mobile-brand">♛ MAJD</div>

        <div className="search">
          <span>⌕</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="ابحث عن محتوى، قنوات، مستخدمين..."
          />
        </div>

        <div className="top-actions">
          <button
            className="create"
            onClick={() => notify("فتح مركز الإنشاء")}
          >
            + إنشاء
          </button>

          <button
            className="icon-button"
            onClick={() => {
              setNotifications(0);
              setPage("notifications");
            }}
          >
            ♧
            {notifications > 0 && <b>{notifications}</b>}
          </button>

          <button
            className="icon-button"
            onClick={() => setPage("messages")}
          >
            ✉
          </button>

          <div className="mini-user">
            <span>♛</span>
            <div>
              <strong>MAJD KING</strong>
              <small>SUPREME</small>
            </div>
          </div>
        </div>
      </header>

      <main>
        <div className="center">{renderPage()}</div>

        <aside className="rightbar">
          <RightBar
            live={LIVE}
            trending={TRENDING}
            channels={CHANNELS}
            events={EVENTS}
            following={following}
            setFollowing={setFollowing}
            setActiveLive={setActiveLive}
            notify={notify}
          />
        </aside>
      </main>

      <button
        className="floating-ai"
        onClick={() => setAiOpen(true)}
        aria-label="ذكاء مجد"
      >
        ✦
      </button>

      <nav className="bottom-nav">
        <button onClick={() => setPage("home")}>♛<span>الرئيسية</span></button>
        <button onClick={() => setPage("shorts")}>◆<span>Shorts</span></button>
        <button className="bottom-create" onClick={() => notify("إنشاء محتوى")}>+</button>
        <button onClick={() => setPage("notifications")}>◌<span>الإشعارات</span></button>
        <button onClick={() => setPage("saved")}>◇<span>المكتبة</span></button>
      </nav>

      {activeStory && (
        <Modal onClose={() => setActiveStory(null)}>
          <div className="story-view">
            <div className="story-avatar">{activeStory.avatar}</div>
            <h2>{activeStory.name}</h2>
            <p>{activeStory.state}</p>
            <div className="story-progress" />
          </div>
        </Modal>
      )}

      {activeLive && (
        <Modal onClose={() => setActiveLive(null)}>
          <div className="live-player">
            <div className={`player-screen ${activeLive.color}`}>
              <span className="live-badge">LIVE</span>
              <span className="player-logo">♛</span>
            </div>
            <h2>{activeLive.title}</h2>
            <p>
              {activeLive.viewers} مشاهد • {activeLive.tag}
            </p>
            <div className="live-chat">
              <strong>الدردشة المباشرة</strong>
              <span>MAJD Gamer: 🔥🔥🔥</span>
              <span>HeroKSA: كفو!</span>
              <span>Dragon: 👑 MAJD</span>
            </div>
          </div>
        </Modal>
      )}

      {aiOpen && (
        <Modal onClose={() => setAiOpen(false)}>
          <div className="ai-modal">
            <div className="ai-orb small">✦</div>
            <h2>ذكاء مجد الإعلامي</h2>
            <p>
              اكتب ما تريد إنشاءه أو تحليله داخل منظومة مجد.
            </p>
            <textarea placeholder="مثال: اقترح فعالية جديدة لمجتمع مجد..." />
            <button
              className="gold-button"
              onClick={() => notify("تم إرسال الطلب لذكاء مجد")}
            >
              إرسال
            </button>
          </div>
        </Modal>
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function PageHeader({ title, subtitle, children }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {children}
    </div>
  );
}

function Post({ post, liked, onLike, onNotify }) {
  return (
    <article className="post panel">
      <header>
        <div className="avatar">{post.avatar}</div>
        <div>
          <strong>
            {post.user} {post.verified && <span>✓</span>}
          </strong>
          <small>
            {post.handle} • {post.time}
          </small>
        </div>
        <button>•••</button>
      </header>

      <p className="post-text">{post.text}</p>
      <p className="tags">{post.tags}</p>

      <div className={`post-media media-${post.media}`}>
        <div className="media-scene">
          <div className="media-crown">♛</div>
          <strong>
            {post.media === "ramadan"
              ? "رمضان في مجد"
              : post.media === "racing"
              ? "MAJD RACING"
              : "DRAGON KINGDOM"}
          </strong>
          <button onClick={() => onNotify("تشغيل الفيديو")}>
            ▶
          </button>
        </div>
      </div>

      <footer>
        <button
          className={liked ? "liked" : ""}
          onClick={onLike}
        >
          ♥ {(post.likes + (liked ? 1 : 0)).toLocaleString()}
        </button>
        <button onClick={() => onNotify("فتح التعليقات")}>
          ◌ {post.comments}
        </button>
        <button onClick={() => onNotify("مشاركة المنشور")}>
          ↗ {post.shares}
        </button>
        <span>◉ {post.views}</span>
      </footer>
    </article>
  );
}

function ContentSection({ title, items }) {
  return (
    <section className="panel content-section">
      <div className="section-title">
        <strong>{title}</strong>
        <button>عرض الكل</button>
      </div>
      <div className="content-grid">
        {items.map((item) => (
          <ContentCard key={item[0]} item={item} />
        ))}
      </div>
    </section>
  );
}

function ContentCard({ item }) {
  const [title, type, rating, art] = item;

  return (
    <button className="content-card">
      <div className={`content-art art-${art}`}>
        <span>♛</span>
        <i>▶</i>
      </div>
      <strong>{title}</strong>
      <small>{type}</small>
      <b>★ {rating}</b>
    </button>
  );
}

function RightBar({
  live,
  trending,
  channels,
  events,
  following,
  setFollowing,
  setActiveLive,
  notify,
}) {
  return (
    <>
      <section className="side-panel">
        <div className="section-title">
          <strong>مباشر الآن</strong>
          <button>عرض الكل</button>
        </div>

        {live.map((item) => (
          <button
            className="side-live"
            key={item.id}
            onClick={() => setActiveLive(item)}
          >
            <div className={`side-thumb ${item.color}`}>
              <span>LIVE</span>
            </div>
            <div>
              <strong>{item.title}</strong>
              <small>● {item.viewers}</small>
            </div>
          </button>
        ))}
      </section>

      <section className="side-panel">
        <div className="section-title">
          <strong>المتداول الآن</strong>
          <button>عرض الكل</button>
        </div>

        <ol className="trending">
          {trending.map(([title, count]) => (
            <li key={title}>
              <div>
                <strong>{title}</strong>
                <small>{count}</small>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="side-panel">
        <div className="section-title">
          <strong>قنوات مقترحة</strong>
          <button>عرض الكل</button>
        </div>

        {channels.map(([name, handle, followers], index) => (
          <div className="channel" key={name}>
            <div className={`channel-logo channel-${index}`}>
              M
            </div>
            <div>
              <strong>{name} ✓</strong>
              <small>{handle} • {followers}</small>
            </div>
            <button
              className={following[name] ? "following" : ""}
              onClick={() =>
                setFollowing((state) => ({
                  ...state,
                  [name]: !state[name],
                }))
              }
            >
              {following[name] ? "متابَع" : "متابعة"}
            </button>
          </div>
        ))}
      </section>

      <section className="side-panel">
        <div className="section-title">
          <strong>الفعاليات القادمة</strong>
          <button>عرض الكل</button>
        </div>

        {events.map(([title, type, action], index) => (
          <button
            className={`side-event event-${index + 1}`}
            key={title}
            onClick={() => notify(`${action}: ${title}`)}
          >
            <span>{type}</span>
            <strong>{title}</strong>
            <small>{action}</small>
          </button>
        ))}
      </section>

      <section className="side-panel ai-side">
        <div className="mini-ai">✦</div>
        <strong>ذكاء مجد الإعلامي</strong>
        <p>
          صناعة المحتوى والتصميم والتحليل والمساعدة الذكية.
        </p>
      </section>
    </>
  );
}

function Modal({ children, onClose }) {
  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div
        className="modal"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose}>
          ×
        </button>
        {children}
      </div>
    </div>
  );
}

const CSS = `
:root{
  --bg:#050a11;
  --bg2:#08111c;
  --panel:#0b1521;
  --panel2:#0d1926;
  --line:rgba(255,255,255,.075);
  --text:#f4f7fb;
  --muted:#8491a3;
  --gold:#e9b84b;
  --gold2:#ffd97c;
  --blue:#2c91ff;
  --cyan:#43d8ff;
  --green:#32d583;
  --red:#ff4967;
  --purple:#8b5cf6;
}

*{box-sizing:border-box}

html,body,#root{
  margin:0;
  min-height:100%;
  background:var(--bg);
}

button,input,textarea{
  font:inherit;
}

button{
  -webkit-tap-highlight-color:transparent;
}

.majd-media{
  min-height:100vh;
  color:var(--text);
  background:
    radial-gradient(circle at 55% -10%,rgba(27,91,160,.15),transparent 27%),
    linear-gradient(180deg,#050a11,#07101a 55%,#050a11);
  font-family:"Tajawal","Noto Sans Arabic","Segoe UI",Arial,sans-serif;
}

.panel,.side-panel{
  border:1px solid var(--line);
  background:
    linear-gradient(145deg,rgba(13,25,38,.96),rgba(7,14,23,.96));
  box-shadow:0 18px 45px rgba(0,0,0,.2);
}

.sidebar{
  position:fixed;
  top:0;
  right:0;
  bottom:0;
  width:238px;
  z-index:60;
  padding:15px 12px;
  overflow:auto;
  background:rgba(5,10,17,.98);
  border-left:1px solid var(--line);
}

.brand{
  height:62px;
  display:flex;
  align-items:center;
  gap:10px;
  direction:ltr;
  border-bottom:1px solid var(--line);
  margin-bottom:14px;
}

.brand-crown{
  width:43px;
  height:43px;
  border-radius:12px;
  display:grid;
  place-items:center;
  color:#171006;
  font-size:24px;
  background:linear-gradient(145deg,#fff0a5,#d79a2e);
  box-shadow:0 0 25px rgba(233,184,75,.18);
}

.brand strong{
  display:block;
  color:var(--gold2);
  letter-spacing:4px;
  font-family:Georgia,serif;
  font-size:19px;
}

.brand span{
  display:block;
  color:#647386;
  font-size:7px;
  letter-spacing:1px;
  margin-top:3px;
}

.profile-card{
  display:grid;
  grid-template-columns:42px 1fr auto;
  align-items:center;
  gap:9px;
  padding:11px;
  margin-bottom:14px;
  border:1px solid rgba(233,184,75,.16);
  border-radius:13px;
  background:rgba(233,184,75,.035);
}

.profile-avatar{
  width:40px;
  height:40px;
  border-radius:50%;
  display:grid;
  place-items:center;
  color:var(--gold);
  border:2px solid var(--gold);
  background:#111927;
}

.profile-card strong{
  display:block;
  font-size:10px;
}

.profile-card span{
  color:var(--muted);
  font-size:8px;
}

.profile-card b{
  color:var(--gold);
  font-size:10px;
}

.sidebar nav{
  display:flex;
  flex-direction:column;
  gap:3px;
}

.sidebar nav button{
  position:relative;
  min-height:40px;
  display:flex;
  align-items:center;
  gap:10px;
  border:1px solid transparent;
  border-radius:10px;
  padding:0 11px;
  color:#aab5c3;
  background:transparent;
  cursor:pointer;
  text-align:right;
  font-size:10px;
}

.sidebar nav button>span{
  width:21px;
  text-align:center;
  color:#8999ad;
  font-size:14px;
}

.sidebar nav button:hover,
.sidebar nav button.active{
  color:var(--gold2);
  border-color:rgba(233,184,75,.15);
  background:linear-gradient(90deg,rgba(233,184,75,.13),transparent);
}

.sidebar nav button.active>span{
  color:var(--gold);
}

.sidebar nav i,
.sidebar nav em{
  margin-right:auto;
  font-style:normal;
  font-size:7px;
  padding:3px 5px;
  border-radius:999px;
  background:var(--red);
  color:white;
}

.sidebar-games{
  margin-top:17px;
  padding:12px;
  border-radius:12px;
  border:1px solid var(--line);
  background:rgba(255,255,255,.018);
}

.sidebar-games strong{
  font-size:9px;
}

.sidebar-games div{
  display:flex;
  gap:5px;
  margin-top:9px;
}

.sidebar-games span{
  flex:1;
  height:37px;
  display:grid;
  place-items:center;
  border-radius:8px;
  background:#101c2b;
}

.topbar{
  position:fixed;
  top:0;
  right:238px;
  left:0;
  z-index:50;
  height:66px;
  padding:0 22px;
  display:flex;
  align-items:center;
  gap:18px;
  background:rgba(5,10,17,.88);
  border-bottom:1px solid var(--line);
  backdrop-filter:blur(20px);
}

.mobile-menu,.mobile-brand{
  display:none;
}

.search{
  max-width:520px;
  flex:1;
  height:38px;
  display:flex;
  align-items:center;
  gap:8px;
  padding:0 12px;
  border:1px solid var(--line);
  border-radius:10px;
  background:#09121d;
}

.search span{
  color:#7e8da0;
}

.search input{
  width:100%;
  border:0;
  outline:0;
  color:white;
  background:transparent;
  font-size:10px;
}

.search input::placeholder{
  color:#627083;
}

.top-actions{
  margin-right:auto;
  display:flex;
  align-items:center;
  gap:8px;
}

.create,.gold-button{
  border:1px solid rgba(255,217,124,.35);
  color:#171005;
  font-weight:900;
  cursor:pointer;
  background:linear-gradient(135deg,#ffe391,#d99b2d);
  box-shadow:0 8px 25px rgba(233,184,75,.12);
}

.create{
  height:37px;
  border-radius:9px;
  padding:0 14px;
  font-size:10px;
}

.icon-button{
  position:relative;
  width:37px;
  height:37px;
  border-radius:9px;
  border:1px solid var(--line);
  color:#c4cedb;
  background:#09121d;
  cursor:pointer;
}

.icon-button b{
  position:absolute;
  top:-4px;
  left:-4px;
  min-width:16px;
  height:16px;
  display:grid;
  place-items:center;
  border-radius:50%;
  background:var(--red);
  color:white;
  font-size:7px;
}

.mini-user{
  display:flex;
  align-items:center;
  gap:7px;
  margin-right:5px;
}

.mini-user>span{
  width:34px;
  height:34px;
  display:grid;
  place-items:center;
  border-radius:50%;
  border:1px solid var(--gold);
  color:var(--gold);
}

.mini-user strong,.mini-user small{
  display:block;
}

.mini-user strong{font-size:8px}
.mini-user small{font-size:7px;color:var(--gold)}

main{
  margin-right:238px;
  padding:82px 18px 90px;
  display:grid;
  grid-template-columns:minmax(0,1fr) 275px;
  gap:16px;
  max-width:1500px;
}

.center{
  min-width:0;
}

.rightbar{
  min-width:0;
}

.stories{
  border-radius:15px;
  padding:15px;
  margin-bottom:12px;
}

.section-title{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin-bottom:12px;
}

.section-title strong{
  font-size:12px;
}

.section-title button{
  border:0;
  color:#4da0ff;
  background:transparent;
  cursor:pointer;
  font-size:8px;
}

.stories-row{
  display:flex;
  gap:15px;
  overflow-x:auto;
  padding-bottom:4px;
}

.story{
  width:69px;
  flex:0 0 69px;
  border:0;
  color:white;
  background:transparent;
  cursor:pointer;
}

.story-ring{
  width:57px;
  height:57px;
  margin:auto;
  padding:2px;
  display:grid;
  place-items:center;
  border-radius:50%;
  background:linear-gradient(135deg,var(--gold),var(--red),var(--purple),var(--blue));
}

.story-ring>span{
  width:51px;
  height:51px;
  display:grid;
  place-items:center;
  border:3px solid #08111c;
  border-radius:50%;
  background:#172234;
  font-weight:900;
}

.story b,.story small{
  display:block;
  overflow:hidden;
  white-space:nowrap;
  text-overflow:ellipsis;
}

.story b{
  margin-top:6px;
  font-size:8px;
}

.story small{
  margin-top:2px;
  color:#77869a;
  font-size:7px;
}

.composer{
  border-radius:15px;
  padding:14px;
  display:flex;
  gap:11px;
  margin-bottom:12px;
}

.avatar{
  width:39px;
  height:39px;
  flex:0 0 39px;
  display:grid;
  place-items:center;
  border-radius:50%;
  color:var(--gold2);
  background:linear-gradient(145deg,#182638,#0b111b);
  border:1px solid rgba(233,184,75,.28);
  font-weight:900;
}

.composer-main{flex:1}

.composer input{
  width:100%;
  height:40px;
  padding:0 13px;
  border:1px solid var(--line);
  border-radius:10px;
  outline:0;
  color:white;
  background:#101a28;
  font-size:10px;
}

.composer-actions{
  display:flex;
  align-items:center;
  gap:5px;
  margin-top:9px;
  flex-wrap:wrap;
}

.composer-actions button{
  border:0;
  color:#8f9bad;
  background:transparent;
  padding:5px 8px;
  cursor:pointer;
  font-size:8px;
}

.composer-actions .publish{
  margin-right:auto;
  padding:6px 15px;
  border-radius:8px;
  color:#171005;
  background:linear-gradient(135deg,#ffe391,#d99b2d);
  font-weight:900;
}

.feed-tabs{
  height:46px;
  border-radius:13px;
  padding:0 12px;
  margin-bottom:12px;
  display:flex;
  align-items:center;
  gap:20px;
}

.feed-tabs button{
  height:100%;
  border:0;
  border-bottom:2px solid transparent;
  color:#758397;
  background:transparent;
  cursor:pointer;
  font-size:9px;
}

.feed-tabs button.active{
  color:white;
  border-bottom-color:var(--gold);
}

.post{
  border-radius:15px;
  overflow:hidden;
  margin-bottom:12px;
}

.post header{
  display:flex;
  align-items:center;
  gap:9px;
  padding:14px 15px 8px;
}

.post header>div:nth-child(2){
  flex:1;
}

.post header strong{
  display:block;
  font-size:10px;
}

.post header strong span{
  color:#3c9cff;
}

.post header small{
  color:#718095;
  font-size:8px;
}

.post header button{
  border:0;
  color:#7c899b;
  background:transparent;
}

.post-text,.tags{
  margin:5px 15px;
  font-size:10px;
  line-height:1.8;
}

.tags{color:#4d9cff}

.post-media{
  position:relative;
  margin:11px 15px;
  height:330px;
  overflow:hidden;
  border-radius:12px;
  border:1px solid rgba(255,255,255,.08);
}

.media-scene{
  position:absolute;
  inset:0;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  overflow:hidden;
}

.media-scene::before,
.content-art::before,
.live-cover::before{
  content:"";
  position:absolute;
  inset:-20%;
  background:
    radial-gradient(circle at 50% 40%,rgba(47,140,255,.38),transparent 25%),
    radial-gradient(circle at 20% 80%,rgba(233,184,75,.18),transparent 22%);
  animation:mediaMove 8s ease-in-out infinite alternate;
}

@keyframes mediaMove{
  to{transform:scale(1.15) translate(-2%,2%)}
}

.media-dragon{
  background:
    radial-gradient(circle at 75% 60%,#a94510 0 4%,transparent 18%),
    linear-gradient(135deg,#090e15,#2b1b13 55%,#0d1826);
}

.media-ramadan{
  background:
    radial-gradient(circle at 50% 25%,rgba(245,193,66,.3),transparent 20%),
    linear-gradient(135deg,#071630,#102451,#1b1028);
}

.media-racing{
  background:
    linear-gradient(135deg,#050a10,#142b4a,#350c33);
}

.media-crown{
  position:relative;
  z-index:2;
  font-size:72px;
  color:var(--gold);
  filter:drop-shadow(0 0 20px rgba(233,184,75,.2));
}

.media-scene strong{
  position:relative;
  z-index:2;
  margin-top:10px;
  font-family:Georgia,serif;
  letter-spacing:4px;
  color:var(--gold2);
  font-size:22px;
}

.media-scene button,.play-circle{
  position:relative;
  z-index:3;
  width:53px;
  height:53px;
  margin-top:15px;
  display:grid;
  place-items:center;
  border-radius:50%;
  border:1px solid rgba(255,255,255,.55);
  color:white;
  background:rgba(0,0,0,.45);
  cursor:pointer;
}

.post footer{
  min-height:47px;
  display:flex;
  align-items:center;
  gap:20px;
  padding:0 16px;
  border-top:1px solid var(--line);
}

.post footer button{
  border:0;
  color:#7f8da0;
  background:transparent;
  cursor:pointer;
  font-size:9px;
}

.post footer button.liked{color:var(--red)}

.post footer span{
  margin-right:auto;
  color:#718095;
  font-size:8px;
}

.recommendation,.content-section{
  padding:16px;
  border-radius:15px;
  margin-bottom:12px;
}

.categories{
  display:flex;
  gap:5px;
  overflow:auto;
}

.categories button{
  color:#7f8da0;
  padding:5px 9px;
  border:0;
  border-radius:999px;
  background:transparent;
}

.categories button.active{
  color:#161006;
  background:var(--gold);
}

.content-grid{
  display:grid;
  grid-template-columns:repeat(6,1fr);
  gap:9px;
}

.content-card{
  min-width:0;
  border:0;
  padding:0;
  text-align:right;
  color:white;
  background:transparent;
  cursor:pointer;
}

.content-art{
  position:relative;
  height:150px;
  display:grid;
  place-items:center;
  overflow:hidden;
  border-radius:10px;
  margin-bottom:7px;
  background:linear-gradient(145deg,#15253b,#26182d);
}

.content-art>span{
  position:relative;
  z-index:2;
  font-size:40px;
  color:rgba(233,184,75,.75);
}

.content-art i{
  position:absolute;
  z-index:3;
  left:8px;
  bottom:8px;
  width:25px;
  height:25px;
  display:grid;
  place-items:center;
  border-radius:50%;
  background:rgba(0,0,0,.6);
  font-style:normal;
  font-size:8px;
}

.art-desert{background:linear-gradient(145deg,#3d2514,#bd6e2b)}
.art-future{background:linear-gradient(145deg,#071425,#145a85)}
.art-dragon{background:linear-gradient(145deg,#180d12,#5c1b20)}
.art-heroes{background:linear-gradient(145deg,#162b45,#b2782d)}
.art-history{background:linear-gradient(145deg,#282017,#66502b)}

.content-card strong,.content-card small,.content-card b{
  display:block;
  overflow:hidden;
  white-space:nowrap;
  text-overflow:ellipsis;
}

.content-card strong{font-size:9px}
.content-card small{color:#718095;font-size:7px;margin-top:3px}
.content-card b{color:var(--gold);font-size:8px;margin-top:3px}

.side-panel{
  border-radius:14px;
  padding:13px;
  margin-bottom:12px;
}

.side-live{
  width:100%;
  display:flex;
  align-items:center;
  gap:8px;
  border:0;
  border-bottom:1px solid var(--line);
  padding:8px 0;
  color:white;
  background:transparent;
  cursor:pointer;
  text-align:right;
}

.side-live:last-child{border-bottom:0}

.side-thumb{
  width:76px;
  height:47px;
  flex:0 0 76px;
  display:flex;
  align-items:flex-end;
  padding:5px;
  border-radius:8px;
  background:linear-gradient(135deg,#26122d,#103a61);
}

.live-a{background:linear-gradient(135deg,#51172b,#ee6238,#30135c)}
.live-b{background:linear-gradient(135deg,#0c2d5e,#7239c5,#d6427c)}
.live-c{background:linear-gradient(135deg,#26150d,#9d4d15,#152b47)}
.live-d{background:linear-gradient(135deg,#171820,#414456,#151b26)}

.side-thumb span,.live-badge{
  padding:2px 4px;
  border-radius:4px;
  background:var(--red);
  color:white;
  font-size:6px;
}

.side-live strong,.side-live small{
  display:block;
}

.side-live strong{font-size:8px}
.side-live small{color:#8491a3;font-size:7px;margin-top:4px}

.trending{
  margin:0;
  padding-right:22px;
}

.trending li{
  padding:6px 3px;
  color:#65758a;
}

.trending strong,.trending small{
  display:block;
}

.trending strong{color:#dce3ec;font-size:8px}
.trending small{font-size:7px;margin-top:2px}

.channel{
  display:grid;
  grid-template-columns:35px 1fr auto;
  align-items:center;
  gap:7px;
  padding:7px 0;
}

.channel-logo{
  width:34px;
  height:34px;
  display:grid;
  place-items:center;
  border-radius:50%;
  border:2px solid #2c91ff;
  background:#14243a;
  font-weight:900;
}

.channel-1{border-color:#e34bd1}
.channel-2{border-color:#ff9c35}
.channel-3{border-color:#39d2ff}

.channel strong,.channel small{
  display:block;
}

.channel strong{font-size:8px}
.channel small{color:#718095;font-size:6px;margin-top:2px}

.channel button{
  padding:5px 8px;
  border:1px solid rgba(233,184,75,.4);
  border-radius:6px;
  color:var(--gold);
  background:transparent;
  cursor:pointer;
  font-size:7px;
}

.channel button.following{
  color:var(--green);
  border-color:rgba(50,213,131,.35);
}

.side-event{
  width:100%;
  min-height:70px;
  margin-bottom:7px;
  padding:9px;
  display:flex;
  flex-direction:column;
  align-items:flex-start;
  justify-content:flex-end;
  border:1px solid var(--line);
  border-radius:9px;
  color:white;
  background:linear-gradient(135deg,#34201b,#161d2a);
  cursor:pointer;
  text-align:right;
}

.side-event span{color:var(--gold);font-size:6px}
.side-event strong{font-size:8px;margin:3px 0}
.side-event small{color:#a7b1bf;font-size:7px}

.event-2{background:linear-gradient(135deg,#131b3d,#37214c)}
.event-3{background:linear-gradient(135deg,#16283a,#53391d)}

.ai-side{text-align:center}

.mini-ai{
  width:55px;
  height:55px;
  margin:5px auto 10px;
  display:grid;
  place-items:center;
  border-radius:50%;
  color:white;
  font-size:24px;
  background:
    radial-gradient(circle,#3edcff,#3753d9 45%,#762ad0);
  box-shadow:0 0 30px rgba(65,121,255,.25);
}

.ai-side strong{color:var(--gold);font-size:10px}
.ai-side p{color:#7d8a9b;font-size:8px;line-height:1.7}

.page-header{
  min-height:70px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom:13px;
}

.page-header h1{
  margin:0;
  font-size:22px;
}

.page-header p{
  margin:5px 0 0;
  color:var(--muted);
  font-size:9px;
}

.gold-button{
  padding:10px 15px;
  border-radius:9px;
  font-size:9px;
}

.live-page-grid,.events-grid{
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:12px;
}

.live-big-card{
  padding:0;
  border-radius:14px;
  overflow:hidden;
  color:white;
  cursor:pointer;
  text-align:right;
}

.live-cover{
  position:relative;
  height:220px;
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
}

.live-cover .live-badge{
  position:absolute;
  top:12px;
  right:12px;
}

.live-info{
  padding:12px;
  display:flex;
  gap:9px;
}

.live-info strong,.live-info span,.live-info small{
  display:block;
}

.live-info strong{font-size:10px}
.live-info span{color:#8b98aa;font-size:8px;margin-top:3px}
.live-info small{color:#6e7d91;font-size:7px;margin-top:4px}

.cinema-hero{
  position:relative;
  min-height:330px;
  display:flex;
  align-items:center;
  padding:40px;
  border-radius:18px;
  overflow:hidden;
  margin-bottom:13px;
  background:
    radial-gradient(circle at 75% 50%,rgba(34,116,209,.3),transparent 25%),
    linear-gradient(110deg,#07101b,#101b2d,#20140d);
}

.cinema-hero>div:first-child{
  position:relative;
  z-index:3;
  max-width:500px;
}

.gold-label{
  color:var(--gold);
  font-size:8px;
  letter-spacing:2px;
}

.cinema-hero h1{
  font-size:42px;
  margin:10px 0;
}

.cinema-hero p{
  color:#a6b0bf;
  line-height:1.9;
  font-size:10px;
}

.cinema-symbol{
  position:absolute;
  left:10%;
  font-size:180px;
  color:rgba(233,184,75,.15);
  animation:crownFloat 5s ease-in-out infinite alternate;
}

@keyframes crownFloat{
  to{transform:translateY(-12px) rotate(-3deg)}
}

.seasons{
  padding:16px;
  border-radius:15px;
}

.episode{
  display:grid;
  grid-template-columns:90px 1fr auto;
  align-items:center;
  gap:12px;
  padding:10px 0;
  border-bottom:1px solid var(--line);
}

.episode-thumb{
  height:55px;
  display:grid;
  place-items:center;
  border-radius:8px;
  background:linear-gradient(135deg,#18263b,#482333);
}

.episode strong{font-size:9px}
.episode p{color:#748297;font-size:8px;margin:4px 0}
.episode button{
  border:1px solid var(--line);
  border-radius:7px;
  color:var(--gold);
  background:transparent;
  padding:6px 9px;
  font-size:8px;
}

.shorts-grid{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:12px;
}

.short-card{
  border-radius:14px;
  overflow:hidden;
  padding-bottom:12px;
}

.short-media{
  height:390px;
  display:flex;
  align-items:center;
  justify-content:center;
  background:linear-gradient(145deg,#12233b,#351832);
}

.short-card>strong,.short-card>p,.short-card>div:last-child{
  display:block;
  margin:8px 11px 0;
}

.short-card>strong{font-size:9px}
.short-card>p{color:#9aa6b6;font-size:8px;line-height:1.7}
.short-card>div:last-child{color:#78869a;font-size:8px}

.event-card{
  padding:13px;
  border-radius:15px;
}

.event-art{
  height:180px;
  display:grid;
  place-items:center;
  border-radius:10px;
  font-size:60px;
  color:rgba(255,217,124,.75);
  background:linear-gradient(145deg,#1b2433,#47221c);
}

.event-card>span{
  display:block;
  color:var(--gold);
  margin-top:10px;
  font-size:7px;
}

.event-card h3{font-size:13px;margin:5px 0}
.event-card p{color:#7f8da0;font-size:8px;line-height:1.8}

.ai-center{
  min-height:570px;
  padding:45px;
  border-radius:18px;
  text-align:center;
}

.ai-orb{
  width:110px;
  height:110px;
  margin:10px auto 20px;
  display:grid;
  place-items:center;
  border-radius:50%;
  font-size:48px;
  background:
    radial-gradient(circle at 40% 35%,#78eaff,#3264e8 45%,#6719aa);
  box-shadow:
    0 0 55px rgba(47,140,255,.28),
    inset 0 0 25px rgba(255,255,255,.2);
  animation:aiPulse 3s ease-in-out infinite alternate;
}

.ai-orb.small{
  width:70px;
  height:70px;
  font-size:30px;
}

@keyframes aiPulse{
  to{transform:scale(1.06);box-shadow:0 0 80px rgba(47,140,255,.4)}
}

.ai-center h2{color:var(--gold2)}
.ai-center>p{color:#8592a4;font-size:10px}

.ai-tools{
  max-width:650px;
  margin:30px auto;
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:10px;
}

.ai-tools button{
  min-height:100px;
  border:1px solid var(--line);
  border-radius:12px;
  color:white;
  background:rgba(255,255,255,.02);
  cursor:pointer;
}

.ai-tools span,.ai-tools strong{display:block}
.ai-tools span{color:#4dcfff;font-size:22px;margin-bottom:8px}
.ai-tools strong{font-size:9px}

.ai-button{min-width:160px}

.generic-page{
  min-height:500px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  border-radius:18px;
  text-align:center;
}

.generic-crown{
  font-size:80px;
  color:var(--gold);
}

.generic-page h2{font-size:25px}
.generic-page p{
  max-width:500px;
  color:#8190a3;
  font-size:10px;
  line-height:1.9;
}

.floating-ai{
  position:fixed;
  left:25px;
  bottom:25px;
  z-index:70;
  width:54px;
  height:54px;
  border:1px solid rgba(93,216,255,.4);
  border-radius:50%;
  color:white;
  font-size:22px;
  cursor:pointer;
  background:radial-gradient(circle,#3edcff,#3158d7 55%,#5d1b9b);
  box-shadow:0 0 35px rgba(47,140,255,.3);
}

.modal-backdrop{
  position:fixed;
  inset:0;
  z-index:200;
  display:grid;
  place-items:center;
  padding:20px;
  background:rgba(0,0,0,.78);
  backdrop-filter:blur(8px);
}

.modal{
  position:relative;
  width:min(680px,100%);
  max-height:90vh;
  overflow:auto;
  padding:20px;
  border:1px solid rgba(233,184,75,.18);
  border-radius:17px;
  background:#09131f;
  box-shadow:0 30px 100px rgba(0,0,0,.6);
}

.modal-close{
  position:absolute;
  top:10px;
  left:10px;
  z-index:5;
  width:32px;
  height:32px;
  border:1px solid var(--line);
  border-radius:8px;
  color:white;
  background:#111c2a;
  cursor:pointer;
}

.story-view{
  min-height:550px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  text-align:center;
  background:
    radial-gradient(circle,#153c69,#15172d 55%,#080d14);
  border-radius:12px;
}

.story-avatar{
  width:100px;
  height:100px;
  display:grid;
  place-items:center;
  border:3px solid var(--gold);
  border-radius:50%;
  font-size:45px;
}

.story-view p{color:#8b99aa}

.story-progress{
  position:absolute;
  top:18px;
  right:20px;
  left:20px;
  height:3px;
  background:linear-gradient(90deg,var(--gold) 70%,rgba(255,255,255,.15) 70%);
}

.player-screen{
  height:380px;
  position:relative;
  display:grid;
  place-items:center;
  border-radius:12px;
}

.player-screen .live-badge{
  position:absolute;
  top:12px;
  right:12px;
}

.player-logo{
  font-size:100px;
  color:var(--gold);
}

.live-player h2{font-size:18px}
.live-player p{color:#8290a2;font-size:9px}

.live-chat{
  padding:12px;
  border:1px solid var(--line);
  border-radius:10px;
  background:#07101a;
}

.live-chat strong,.live-chat span{
  display:block;
  margin:6px 0;
  font-size:9px;
}

.live-chat span{color:#9aa6b5}

.ai-modal{text-align:center;padding:20px}

.ai-modal p{color:#8593a6;font-size:9px}

.ai-modal textarea{
  width:100%;
  min-height:130px;
  resize:vertical;
  padding:12px;
  margin:10px 0;
  border:1px solid var(--line);
  border-radius:10px;
  outline:0;
  color:white;
  background:#07101a;
  font-size:10px;
}

.toast{
  position:fixed;
  left:25px;
  bottom:90px;
  z-index:300;
  padding:11px 15px;
  border:1px solid rgba(50,213,131,.25);
  border-radius:10px;
  color:#d9f8e9;
  background:rgba(8,34,24,.97);
  box-shadow:0 20px 50px rgba(0,0,0,.4);
  font-size:9px;
}

.overlay,.bottom-nav{display:none}

@media(max-width:1200px){
  main{grid-template-columns:minmax(0,1fr) 245px}
  .content-grid{grid-template-columns:repeat(3,1fr)}
}

@media(max-width:980px){
  .sidebar{
    transform:translateX(105%);
    transition:.25s ease;
  }

  .sidebar.open{transform:translateX(0)}

  .overlay{
    display:block;
    position:fixed;
    inset:0;
    z-index:55;
    border:0;
    background:rgba(0,0,0,.6);
  }

  .topbar{right:0}

  .mobile-menu{
    display:block;
    width:36px;
    height:36px;
    border:1px solid var(--line);
    border-radius:8px;
    color:white;
    background:#09121d;
  }

  .mobile-brand{
    display:block;
    color:var(--gold);
    font-family:Georgia,serif;
    white-space:nowrap;
  }

  main{
    margin-right:0;
    grid-template-columns:1fr;
  }

  .rightbar{display:none}
}

@media(max-width:680px){
  .topbar{
    height:60px;
    padding:0 10px;
    gap:7px;
  }

  .mobile-brand{display:none}
  .mini-user{display:none}
  .top-actions .icon-button:nth-of-type(2){display:none}

  .search{
    height:35px;
    padding:0 8px;
  }

  .create{
    padding:0 9px;
  }

  main{
    padding:72px 9px 90px;
  }

  .stories{
    padding:12px 9px;
  }

  .story{
    width:61px;
    flex-basis:61px;
  }

  .story-ring{
    width:51px;
    height:51px;
  }

  .story-ring>span{
    width:45px;
    height:45px;
  }

  .post-media{
    height:270px;
    margin:8px;
  }

  .post header{padding:11px 10px 7px}
  .post-text,.tags{margin-right:10px;margin-left:10px}

  .media-crown{font-size:55px}
  .media-scene strong{font-size:16px}

  .content-grid{
    grid-template-columns:repeat(2,1fr);
  }

  .content-art{height:180px}

  .live-page-grid,.events-grid{
    grid-template-columns:1fr;
  }

  .shorts-grid{
    grid-template-columns:repeat(2,1fr);
  }

  .short-media{height:330px}

  .cinema-hero{
    min-height:380px;
    padding:25px;
  }

  .cinema-hero h1{font-size:31px}
  .cinema-symbol{font-size:120px;opacity:.55}

  .ai-center{padding:25px 12px}
  .ai-tools{grid-template-columns:repeat(2,1fr)}

  .episode{
    grid-template-columns:70px 1fr;
  }

  .episode>button{
    grid-column:2;
    width:max-content;
  }

  .floating-ai{
    bottom:75px;
    left:14px;
    width:48px;
    height:48px;
  }

  .bottom-nav{
    position:fixed;
    right:0;
    left:0;
    bottom:0;
    z-index:80;
    height:62px;
    display:flex;
    align-items:center;
    justify-content:space-around;
    background:rgba(5,10,17,.96);
    border-top:1px solid var(--line);
    backdrop-filter:blur(18px);
  }

  .bottom-nav button{
    min-width:55px;
    border:0;
    color:#8491a3;
    background:transparent;
    font-size:15px;
  }

  .bottom-nav button span{
    display:block;
    font-size:7px;
    margin-top:3px;
  }

  .bottom-nav .bottom-create{
    width:44px;
    height:44px;
    min-width:44px;
    border:1px solid #75869b;
    border-radius:50%;
    color:white;
    font-size:25px;
  }

  .modal{padding:13px}
  .player-screen{height:260px}
  .story-view{min-height:500px}
}

@media(max-width:420px){
  .shorts-grid{grid-template-columns:1fr 1fr}
  .short-media{height:280px}
  .content-art{height:145px}
  .composer-actions button{padding:5px}
  .post footer{gap:10px}
}

@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms!important;
    animation-iteration-count:1!important;
  }
}
`;
