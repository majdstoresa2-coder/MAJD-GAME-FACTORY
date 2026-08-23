import React, { useEffect, useMemo, useState } from "react";

/**
 * ============================================================
 * MAJD GAMES
 * 07-MAJD-ADVANCED-CONTROL-PANEL.jsx
 * Advanced Owner Control Panel
 * ============================================================
 *
 * لوحة تحكم موحدة ومتجاوبة.
 * لا تحتاج مكتبات UI خارجية.
 *
 * يمكن لاحقاً ربط apiBase بمسارات الـ Backend الحقيقية.
 * ============================================================
 */

const API_BASE =
  typeof window !== "undefined" && window.MAJD_API_BASE
    ? window.MAJD_API_BASE
    : "/api";

const NAV_ITEMS = [
  { id: "overview", icon: "♛", label: "الرئيسية" },
  { id: "ai", icon: "✦", label: "الذكاء الاصطناعي" },
  { id: "games", icon: "🎮", label: "الألعاب" },
  { id: "users", icon: "♟", label: "المستخدمون" },
  { id: "wallets", icon: "◈", label: "المحافظ والمدفوعات" },
  { id: "ads", icon: "◎", label: "الإعلانات" },
  { id: "deploy", icon: "▲", label: "البناء والنشر" },
  { id: "monitor", icon: "◉", label: "المراقبة" },
  { id: "security", icon: "◆", label: "الأمان" },
  { id: "logs", icon: "≡", label: "السجلات" },
  { id: "settings", icon: "⚙", label: "الإعدادات" },
];

const INITIAL_GAMES = [
  {
    id: "game-001",
    name: "Winter Sovereignty",
    status: "جاهزة",
    platform: "Web / Mobile",
    players: 0,
    build: "Production",
  },
  {
    id: "game-002",
    name: "Majd Kingdom",
    status: "تجهيز",
    platform: "Web / PC",
    players: 0,
    build: "Preparing",
  },
];

const INITIAL_LOGS = [
  {
    id: 1,
    type: "success",
    title: "لوحة التحكم",
    message: "تم تشغيل مركز التحكم المتقدم.",
    time: "الآن",
  },
  {
    id: 2,
    type: "success",
    title: "النظام",
    message: "واجهة MAJD GAMES جاهزة.",
    time: "الآن",
  },
  {
    id: 3,
    type: "info",
    title: "المراقبة",
    message: "بانتظار بيانات الخدمات الحية من الخادم.",
    time: "الآن",
  },
];

function safeNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();

  if (
    value.includes("online") ||
    value.includes("ready") ||
    value.includes("active") ||
    value.includes("جاهز") ||
    value.includes("نشط")
  ) {
    return "success";
  }

  if (
    value.includes("error") ||
    value.includes("failed") ||
    value.includes("offline") ||
    value.includes("خطأ") ||
    value.includes("متوقف")
  ) {
    return "danger";
  }

  return "warning";
}

async function requestJSON(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 7000);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
      signal: controller.signal,
    });

    const text = await response.text();
    let body = {};

    try {
      body = text ? JSON.parse(text) : {};
    } catch {
      body = { message: text };
    }

    if (!response.ok) {
      throw new Error(
        body?.message || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return body;
  } finally {
    clearTimeout(timeout);
  }
}

function MajdLogo() {
  return (
    <div className="majd-logo" aria-label="MAJD GAMES">
      <div className="crown">♛</div>
      <div>
        <strong>MAJD</strong>
        <span>GAMES</span>
      </div>
    </div>
  );
}

function StatusDot({ status = "success" }) {
  return <span className={`status-dot ${status}`} />;
}

function StatCard({ icon, title, value, subtitle, status = "success" }) {
  return (
    <article className="stat-card glass">
      <div className={`stat-icon ${status}`}>{icon}</div>
      <div className="stat-copy">
        <span>{title}</span>
        <strong>{value}</strong>
        <small>{subtitle}</small>
      </div>
    </article>
  );
}

function SectionHeader({ title, subtitle, children }) {
  return (
    <div className="section-header">
      <div>
        <h2>{title}</h2>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {children ? <div className="section-actions">{children}</div> : null}
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="empty-state">
      <div>♛</div>
      <strong>{text}</strong>
    </div>
  );
}

function Toggle({ checked, onChange, disabled = false }) {
  return (
    <button
      type="button"
      className={`toggle ${checked ? "on" : ""}`}
      onClick={() => !disabled && onChange(!checked)}
      disabled={disabled}
      aria-pressed={checked}
    >
      <span />
    </button>
  );
}

export default function MajdAdvancedControlPanel() {
  const [activePage, setActivePage] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [commandBusy, setCommandBusy] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const [platform, setPlatform] = useState({
    status: "online",
    environment: "production",
    version: "7.0",
    domain: "majd.shop",
    uptime: "—",
  });

  const [ai, setAI] = useState({
    status: "ready",
    mode: "Autonomous",
    activeJobs: 0,
    completedJobs: 0,
    failedJobs: 0,
  });

  const [metrics, setMetrics] = useState({
    users: 0,
    onlineUsers: 0,
    games: INITIAL_GAMES.length,
    revenue: 0,
    deposits: 0,
    transactions: 0,
    alerts: 0,
  });

  const [services, setServices] = useState([
    { name: "Frontend", status: "online", detail: "MAJD GAMES" },
    { name: "Backend API", status: "checking", detail: "جاري الفحص" },
    { name: "Database", status: "checking", detail: "جاري الفحص" },
    { name: "Payment", status: "checking", detail: "جاري الفحص" },
    { name: "AI Engine", status: "checking", detail: "جاري الفحص" },
    { name: "Deployment", status: "checking", detail: "جاري الفحص" },
  ]);

  const [games, setGames] = useState(INITIAL_GAMES);
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [notice, setNotice] = useState(null);

  const [automation, setAutomation] = useState({
    autoBuild: true,
    autoTest: true,
    autoRepair: true,
    autoDeploy: false,
    maintenanceMode: false,
  });

  const currentPage =
    NAV_ITEMS.find((item) => item.id === activePage)?.label || "الرئيسية";

  const healthyServices = useMemo(
    () =>
      services.filter(
        (service) => statusClass(service.status) === "success"
      ).length,
    [services]
  );

  function addLog(type, title, message) {
    setLogs((current) => [
      {
        id: Date.now() + Math.random(),
        type,
        title,
        message,
        time: new Date().toLocaleTimeString("ar-SA", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
      ...current,
    ].slice(0, 100));
  }

  function showNotice(message, type = "success") {
    setNotice({ message, type });

    window.clearTimeout(window.__majdNoticeTimer);
    window.__majdNoticeTimer = window.setTimeout(() => {
      setNotice(null);
    }, 3500);
  }

  async function loadDashboard(silent = false) {
    if (!silent) setLoading(true);

    const nextServices = [
      { name: "Frontend", status: "online", detail: "MAJD GAMES" },
    ];

    try {
      const health = await requestJSON("/health");

      setPlatform((current) => ({
        ...current,
        status: health.status || "online",
        uptime: health.uptime || current.uptime,
        version: health.version || current.version,
      }));

      nextServices.push({
        name: "Backend API",
        status: "online",
        detail: "متصل",
      });
    } catch {
      nextServices.push({
        name: "Backend API",
        status: "warning",
        detail: "لم يرجع /api/health",
      });
    }

    try {
      const aiStatus = await requestJSON("/ai/status");

      setAI((current) => ({
        ...current,
        ...aiStatus,
        activeJobs: safeNumber(
          aiStatus.activeJobs ?? aiStatus.active_jobs,
          current.activeJobs
        ),
        completedJobs: safeNumber(
          aiStatus.completedJobs ?? aiStatus.completed_jobs,
          current.completedJobs
        ),
        failedJobs: safeNumber(
          aiStatus.failedJobs ?? aiStatus.failed_jobs,
          current.failedJobs
        ),
      }));

      nextServices.push({
        name: "AI Engine",
        status: aiStatus.status || "online",
        detail: aiStatus.message || "متصل",
      });
    } catch {
      nextServices.push({
        name: "AI Engine",
        status: "warning",
        detail: "بانتظار مسار AI",
      });
    }

    try {
      const dashboard = await requestJSON("/admin/dashboard");

      setMetrics((current) => ({
        users: safeNumber(
          dashboard.users ?? dashboard.totalUsers,
          current.users
        ),
        onlineUsers: safeNumber(
          dashboard.onlineUsers,
          current.onlineUsers
        ),
        games: safeNumber(
          dashboard.games ?? dashboard.totalGames,
          current.games
        ),
        revenue: safeNumber(
          dashboard.revenue ?? dashboard.totalRevenue,
          current.revenue
        ),
        deposits: safeNumber(
          dashboard.deposits,
          current.deposits
        ),
        transactions: safeNumber(
          dashboard.transactions ?? dashboard.totalTransactions,
          current.transactions
        ),
        alerts: safeNumber(dashboard.alerts, current.alerts),
      }));

      if (Array.isArray(dashboard.games)) {
        setGames(dashboard.games);
      }

      if (dashboard.database) {
        nextServices.push({
          name: "Database",
          status: dashboard.database.status || "online",
          detail: dashboard.database.message || "متصلة",
        });
      }
    } catch {
      nextServices.push({
        name: "Database",
        status: "warning",
        detail: "بانتظار بيانات الإدارة",
      });
    }

    try {
      const payment = await requestJSON("/payment/status");

      nextServices.push({
        name: "Payment",
        status: payment.status || "online",
        detail: payment.provider || "متصل",
      });
    } catch {
      nextServices.push({
        name: "Payment",
        status: "warning",
        detail: "بانتظار مسار الدفع",
      });
    }

    nextServices.push({
      name: "Deployment",
      status: "ready",
      detail: "Production",
    });

    const unique = [];
    const names = new Set();

    for (const service of nextServices) {
      if (!names.has(service.name)) {
        names.add(service.name);
        unique.push(service);
      }
    }

    setServices(unique);
    setLastRefresh(new Date());
    setLoading(false);
  }

  useEffect(() => {
    loadDashboard();

    const interval = window.setInterval(() => {
      loadDashboard(true);
    }, 60000);

    return () => window.clearInterval(interval);
  }, []);

  async function executeOwnerCommand(command, label) {
    if (commandBusy) return;

    setCommandBusy(true);
    addLog("info", "أمر المالك", `بدء تنفيذ: ${label}`);

    try {
      const result = await requestJSON("/ai/owner-command", {
        method: "POST",
        body: JSON.stringify({
          command,
          source: "07-MAJD-ADVANCED-CONTROL-PANEL",
          requestedAt: new Date().toISOString(),
        }),
      });

      addLog(
        "success",
        "أمر المالك",
        result.message || `تم تنفيذ: ${label}`
      );

      showNotice(result.message || `تم تنفيذ ${label}`);
      await loadDashboard(true);
    } catch (error) {
      addLog(
        "warning",
        "أمر المالك",
        `${label}: ${error.message}`
      );

      showNotice(
        `مسار التنفيذ الحي غير متصل بعد: ${label}`,
        "warning"
      );
    } finally {
      setCommandBusy(false);
    }
  }

  function updateAutomation(key, value) {
    setAutomation((current) => ({
      ...current,
      [key]: value,
    }));

    addLog(
      "info",
      "الأتمتة",
      `${key} = ${value ? "ON" : "OFF"}`
    );
  }

  function renderOverview() {
    return (
      <>
        <section className="hero glass">
          <div className="hero-background" />
          <div className="stars" />
          <div className="hero-glow glow-one" />
          <div className="hero-glow glow-two" />

          <div className="hero-content">
            <div className="hero-kicker">
              <StatusDot status="success" />
              OWNER CONTROL CENTER
            </div>

            <h1>
              مملكة <span>مجد</span> الرقمية
            </h1>

            <p>
              مركز القيادة المتقدم لإدارة منصة MAJD GAMES والألعاب
              والذكاء الاصطناعي والتشغيل من مكان واحد.
            </p>

            <div className="hero-buttons">
              <button
                className="primary-btn"
                onClick={() =>
                  executeOwnerCommand(
                    "RUN_FULL_SYSTEM_CHECK",
                    "فحص المنصة بالكامل"
                  )
                }
                disabled={commandBusy}
              >
                ♛ فحص المنصة
              </button>

              <button
                className="secondary-btn"
                onClick={() => setActivePage("ai")}
              >
                ✦ مركز الذكاء الاصطناعي
              </button>
            </div>
          </div>

          <div className="royal-emblem" aria-hidden="true">
            <div className="emblem-crown">♛</div>
            <div className="emblem-shield">M</div>
            <div className="emblem-name">MAJD</div>
            <div className="emblem-sub">GAMES</div>
          </div>
        </section>

        <section className="stats-grid">
          <StatCard
            icon="◉"
            title="حالة المنصة"
            value={
              statusClass(platform.status) === "success"
                ? "تعمل"
                : "تحتاج فحص"
            }
            subtitle={platform.environment}
            status={statusClass(platform.status)}
          />

          <StatCard
            icon="✦"
            title="الذكاء الاصطناعي"
            value={
              statusClass(ai.status) === "success"
                ? "جاهز"
                : ai.status
            }
            subtitle={ai.mode || "Autonomous"}
            status={statusClass(ai.status)}
          />

          <StatCard
            icon="🎮"
            title="الألعاب"
            value={metrics.games}
            subtitle="المسجلة في النظام"
          />

          <StatCard
            icon="♟"
            title="المستخدمون"
            value={metrics.users.toLocaleString("ar-SA")}
            subtitle={`${metrics.onlineUsers.toLocaleString(
              "ar-SA"
            )} متصل الآن`}
          />

          <StatCard
            icon="◈"
            title="الإيرادات"
            value={`${metrics.revenue.toLocaleString("ar-SA")} ر.س`}
            subtitle={`${metrics.transactions.toLocaleString(
              "ar-SA"
            )} عملية`}
          />

          <StatCard
            icon="◆"
            title="الخدمات"
            value={`${healthyServices}/${services.length}`}
            subtitle="خدمات سليمة"
            status={
              healthyServices === services.length
                ? "success"
                : "warning"
            }
          />
        </section>

        <div className="dashboard-columns">
          <section className="panel glass">
            <SectionHeader
              title="حالة الأنظمة"
              subtitle="المراقبة الموحدة للخدمات"
            >
              <button
                className="mini-btn"
                onClick={() => loadDashboard()}
              >
                ↻ تحديث
              </button>
            </SectionHeader>

            <div className="service-list">
              {services.map((service) => (
                <div className="service-row" key={service.name}>
                  <div className="service-name">
                    <StatusDot status={statusClass(service.status)} />
                    <div>
                      <strong>{service.name}</strong>
                      <small>{service.detail}</small>
                    </div>
                  </div>

                  <span
                    className={`status-badge ${statusClass(
                      service.status
                    )}`}
                  >
                    {statusClass(service.status) === "success"
                      ? "سليم"
                      : statusClass(service.status) === "danger"
                      ? "خطأ"
                      : "فحص"}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel glass">
            <SectionHeader
              title="أوامر المالك السريعة"
              subtitle="اختصارات التشغيل والإدارة"
            />

            <div className="command-grid">
              <button
                onClick={() =>
                  executeOwnerCommand(
                    "RUN_AI",
                    "تشغيل الذكاء الاصطناعي"
                  )
                }
              >
                <b>✦</b>
                <span>تشغيل AI</span>
              </button>

              <button
                onClick={() =>
                  executeOwnerCommand(
                    "TEST_PLATFORM",
                    "اختبار المنصة"
                  )
                }
              >
                <b>✓</b>
                <span>اختبار شامل</span>
              </button>

              <button
                onClick={() =>
                  executeOwnerCommand(
                    "BUILD_GAMES",
                    "بناء الألعاب"
                  )
                }
              >
                <b>🎮</b>
                <span>بناء الألعاب</span>
              </button>

              <button
                onClick={() =>
                  executeOwnerCommand(
                    "DEPLOY_PRODUCTION",
                    "النشر للإنتاج"
                  )
                }
              >
                <b>▲</b>
                <span>النشر</span>
              </button>

              <button
                onClick={() =>
                  executeOwnerCommand(
                    "AUTO_REPAIR",
                    "الإصلاح التلقائي"
                  )
                }
              >
                <b>⚙</b>
                <span>إصلاح تلقائي</span>
              </button>

              <button
                onClick={() => setActivePage("monitor")}
              >
                <b>◉</b>
                <span>المراقبة</span>
              </button>
            </div>
          </section>
        </div>

        <section className="panel glass">
          <SectionHeader
            title="آخر الأحداث"
            subtitle="أحدث نشاط داخل مركز التحكم"
          >
            <button
              className="mini-btn"
              onClick={() => setActivePage("logs")}
            >
              عرض الكل
            </button>
          </SectionHeader>

          <LogList logs={logs.slice(0, 5)} />
        </section>
      </>
    );
  }

  function renderAI() {
    return (
      <>
        <SectionHeader
          title="مركز الذكاء الاصطناعي"
          subtitle="إدارة محرك مجد الآلي"
        >
          <button
            className="primary-btn compact"
            onClick={() =>
              executeOwnerCommand(
                "RUN_AUTONOMOUS_AI",
                "تشغيل الوضع المستقل"
              )
            }
          >
            ✦ تشغيل
          </button>
        </SectionHeader>

        <section className="stats-grid">
          <StatCard
            icon="✦"
            title="حالة AI"
            value={ai.status || "—"}
            subtitle={ai.mode || "Autonomous"}
            status={statusClass(ai.status)}
          />
          <StatCard
            icon="◌"
            title="قيد التنفيذ"
            value={ai.activeJobs}
            subtitle="مهام"
          />
          <StatCard
            icon="✓"
            title="مكتملة"
            value={ai.completedJobs}
            subtitle="مهام ناجحة"
          />
          <StatCard
            icon="!"
            title="فشل"
            value={ai.failedJobs}
            subtitle="مهام تحتاج مراجعة"
            status={ai.failedJobs > 0 ? "danger" : "success"}
          />
        </section>

        <section className="panel glass">
          <SectionHeader
            title="الأتمتة"
            subtitle="صلاحيات التنفيذ التلقائي"
          />

          <div className="settings-list">
            <SettingToggle
              title="البناء التلقائي"
              description="بناء المشاريع والألعاب تلقائياً."
              value={automation.autoBuild}
              onChange={(value) =>
                updateAutomation("autoBuild", value)
              }
            />

            <SettingToggle
              title="الاختبار التلقائي"
              description="تشغيل الاختبارات بعد البناء."
              value={automation.autoTest}
              onChange={(value) =>
                updateAutomation("autoTest", value)
              }
            />

            <SettingToggle
              title="الإصلاح الذاتي"
              description="محاولة إصلاح الأخطاء المكتشفة تلقائياً."
              value={automation.autoRepair}
              onChange={(value) =>
                updateAutomation("autoRepair", value)
              }
            />

            <SettingToggle
              title="النشر التلقائي"
              description="لا يتم تفعيله إلا عند ربط مسار الإنتاج الحقيقي."
              value={automation.autoDeploy}
              onChange={(value) =>
                updateAutomation("autoDeploy", value)
              }
            />
          </div>
        </section>
      </>
    );
  }

  function renderGames() {
    return (
      <>
        <SectionHeader
          title="إدارة الألعاب"
          subtitle="الألعاب والبناء وحالة النشر"
        >
          <button
            className="primary-btn compact"
            onClick={() =>
              executeOwnerCommand(
                "CREATE_GAME",
                "بدء إنشاء لعبة"
              )
            }
          >
            + إنشاء لعبة
          </button>
        </SectionHeader>

        <section className="panel glass table-panel">
          {games.length ? (
            <div className="responsive-table">
              <table>
                <thead>
                  <tr>
                    <th>اللعبة</th>
                    <th>الحالة</th>
                    <th>المنصة</th>
                    <th>اللاعبون</th>
                    <th>البناء</th>
                    <th>التحكم</th>
                  </tr>
                </thead>
                <tbody>
                  {games.map((game, index) => (
                    <tr key={game.id || index}>
                      <td>
                        <strong>{game.name || "بدون اسم"}</strong>
                      </td>
                      <td>
                        <span
                          className={`status-badge ${statusClass(
                            game.status
                          )}`}
                        >
                          {game.status || "—"}
                        </span>
                      </td>
                      <td>{game.platform || "—"}</td>
                      <td>{safeNumber(game.players)}</td>
                      <td>{game.build || "—"}</td>
                      <td>
                        <button
                          className="mini-btn"
                          onClick={() =>
                            executeOwnerCommand(
                              `TEST_GAME:${game.id}`,
                              `اختبار ${game.name}`
                            )
                          }
                        >
                          اختبار
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState text="لا توجد ألعاب مسجلة" />
          )}
        </section>
      </>
    );
  }

  function renderUsers() {
    return (
      <>
        <SectionHeader
          title="المستخدمون"
          subtitle="إدارة مجتمع منصة مجد"
        />

        <section className="stats-grid">
          <StatCard
            icon="♟"
            title="إجمالي المستخدمين"
            value={metrics.users.toLocaleString("ar-SA")}
            subtitle="حساب"
          />
          <StatCard
            icon="◉"
            title="متصلون الآن"
            value={metrics.onlineUsers.toLocaleString("ar-SA")}
            subtitle="مستخدم"
          />
          <StatCard
            icon="◆"
            title="التنبيهات"
            value={metrics.alerts}
            subtitle="تنبيهات"
            status={metrics.alerts ? "warning" : "success"}
          />
        </section>

        <section className="panel glass">
          <EmptyState text="سيظهر سجل المستخدمين هنا عند ربط مسار الإدارة." />
        </section>
      </>
    );
  }

  function renderWallets() {
    return (
      <>
        <SectionHeader
          title="المحافظ والمدفوعات"
          subtitle="مركز العمليات المالية لمنصة مجد"
        />

        <section className="stats-grid">
          <StatCard
            icon="◈"
            title="الإيرادات"
            value={`${metrics.revenue.toLocaleString("ar-SA")} ر.س`}
            subtitle="إجمالي مسجل"
          />
          <StatCard
            icon="↗"
            title="الإيداعات"
            value={`${metrics.deposits.toLocaleString("ar-SA")} ر.س`}
            subtitle="إجمالي الإيداعات"
          />
          <StatCard
            icon="≡"
            title="المعاملات"
            value={metrics.transactions.toLocaleString("ar-SA")}
            subtitle="عملية"
          />
        </section>

        <section className="panel glass">
          <SectionHeader
            title="بوابة الدفع"
            subtitle="حالة التكامل المالي"
          />
          <div className="finance-card">
            <div className="finance-logo">M</div>
            <div>
              <strong>Payment Gateway</strong>
              <p>
                البيانات الحية تظهر تلقائياً عند اتصال مسار
                /api/payment/status.
              </p>
            </div>
          </div>
        </section>
      </>
    );
  }

  function renderAds() {
    return (
      <>
        <SectionHeader
          title="الإعلانات"
          subtitle="إدارة نظام الإعلانات والمكافآت"
        />

        <section className="panel glass">
          <div className="feature-grid">
            <FeatureCard
              icon="▶"
              title="إعلانات المكافآت"
              text="إدارة مكافآت مشاهدة الإعلانات داخل الألعاب."
            />
            <FeatureCard
              icon="◎"
              title="الحملات"
              text="متابعة الحملات الإعلانية ومصادرها."
            />
            <FeatureCard
              icon="◈"
              title="العائد"
              text="عرض الإيرادات عند ربط مزود الإعلانات الحقيقي."
            />
          </div>
        </section>
      </>
    );
  }

  function renderDeploy() {
    return (
      <>
        <SectionHeader
          title="البناء والنشر"
          subtitle="إدارة دورة الإصدار والإنتاج"
        />

        <section className="panel glass">
          <div className="pipeline">
            {[
              ["01", "SOURCE", "الكود"],
              ["02", "TEST", "الاختبار"],
              ["03", "BUILD", "البناء"],
              ["04", "VERIFY", "التحقق"],
              ["05", "DEPLOY", "النشر"],
              ["06", "LIVE", "الإنتاج"],
            ].map(([number, name, arabic], index) => (
              <React.Fragment key={number}>
                <div className="pipeline-step">
                  <span>{number}</span>
                  <strong>{name}</strong>
                  <small>{arabic}</small>
                </div>
                {index < 5 ? (
                  <div className="pipeline-line">←</div>
                ) : null}
              </React.Fragment>
            ))}
          </div>

          <div className="deploy-actions">
            <button
              className="secondary-btn"
              onClick={() =>
                executeOwnerCommand(
                  "RUN_TESTS",
                  "تشغيل الاختبارات"
                )
              }
            >
              ✓ اختبار
            </button>

            <button
              className="secondary-btn"
              onClick={() =>
                executeOwnerCommand("BUILD", "بناء الإنتاج")
              }
            >
              ⚙ بناء
            </button>

            <button
              className="primary-btn"
              onClick={() =>
                executeOwnerCommand(
                  "DEPLOY_PRODUCTION",
                  "النشر للإنتاج"
                )
              }
            >
              ▲ نشر الإنتاج
            </button>
          </div>
        </section>
      </>
    );
  }

  function renderMonitor() {
    return (
      <>
        <SectionHeader
          title="المراقبة الحية"
          subtitle="حالة خدمات MAJD GAMES"
        >
          <button
            className="mini-btn"
            onClick={() => loadDashboard()}
          >
            ↻ تحديث الآن
          </button>
        </SectionHeader>

        <section className="monitor-grid">
          {services.map((service) => (
            <article className="monitor-card glass" key={service.name}>
              <div className="monitor-ring">
                <StatusDot status={statusClass(service.status)} />
              </div>
              <h3>{service.name}</h3>
              <strong
                className={`text-${statusClass(service.status)}`}
              >
                {statusClass(service.status) === "success"
                  ? "ONLINE"
                  : statusClass(service.status) === "danger"
                  ? "OFFLINE"
                  : "CHECK"}
              </strong>
              <small>{service.detail}</small>
            </article>
          ))}
        </section>
      </>
    );
  }

  function renderSecurity() {
    return (
      <>
        <SectionHeader
          title="الأمان"
          subtitle="مركز الحماية والصلاحيات"
        />

        <section className="panel glass">
          <div className="security-hero">
            <div className="security-shield">◆</div>
            <div>
              <h3>MAJD SECURITY</h3>
              <p>
                لوحة مراقبة أمنية موحدة. لا تعرض المفاتيح أو الأسرار
                الحساسة داخل الواجهة.
              </p>
            </div>
          </div>

          <div className="feature-grid">
            <FeatureCard
              icon="♛"
              title="صلاحيات المالك"
              text="التحكم الإداري الأعلى داخل لوحة مجد."
            />
            <FeatureCard
              icon="◆"
              title="الأسرار"
              text="تبقى في متغيرات البيئة على الخادم ولا تُضمّن في React."
            />
            <FeatureCard
              icon="◉"
              title="المراقبة"
              text="تسجيل الأحداث والتنبيهات التشغيلية."
            />
          </div>
        </section>
      </>
    );
  }

  function renderLogs() {
    return (
      <>
        <SectionHeader
          title="السجلات"
          subtitle="أحداث مركز التحكم"
        >
          <button
            className="mini-btn danger-outline"
            onClick={() => setLogs([])}
          >
            مسح العرض
          </button>
        </SectionHeader>

        <section className="panel glass">
          {logs.length ? (
            <LogList logs={logs} />
          ) : (
            <EmptyState text="لا توجد أحداث معروضة" />
          )}
        </section>
      </>
    );
  }

  function renderSettings() {
    return (
      <>
        <SectionHeader
          title="الإعدادات"
          subtitle="إعدادات مركز التحكم"
        />

        <section className="panel glass">
          <div className="settings-list">
            <SettingToggle
              title="وضع الصيانة"
              description="إعداد واجهة التحكم لوضع الصيانة."
              value={automation.maintenanceMode}
              onChange={(value) =>
                updateAutomation("maintenanceMode", value)
              }
            />

            <SettingToggle
              title="النشر التلقائي"
              description="تفعيل النشر الآلي بعد نجاح الاختبارات."
              value={automation.autoDeploy}
              onChange={(value) =>
                updateAutomation("autoDeploy", value)
              }
            />
          </div>

          <div className="system-info">
            <div>
              <span>النطاق</span>
              <strong>{platform.domain}</strong>
            </div>
            <div>
              <span>البيئة</span>
              <strong>{platform.environment}</strong>
            </div>
            <div>
              <span>الإصدار</span>
              <strong>{platform.version}</strong>
            </div>
            <div>
              <span>API</span>
              <strong>{API_BASE}</strong>
            </div>
          </div>
        </section>
      </>
    );
  }

  function renderPage() {
    switch (activePage) {
      case "ai":
        return renderAI();
      case "games":
        return renderGames();
      case "users":
        return renderUsers();
      case "wallets":
        return renderWallets();
      case "ads":
        return renderAds();
      case "deploy":
        return renderDeploy();
      case "monitor":
        return renderMonitor();
      case "security":
        return renderSecurity();
      case "logs":
        return renderLogs();
      case "settings":
        return renderSettings();
      default:
        return renderOverview();
    }
  }

  return (
    <div className="majd-control-panel" dir="rtl">
      <style>{`
        :root {
          --majd-bg: #050912;
          --majd-bg-2: #09111e;
          --majd-panel: rgba(11, 20, 34, 0.82);
          --majd-panel-strong: rgba(8, 15, 27, 0.96);
          --majd-gold: #e8b84c;
          --majd-gold-2: #ffd979;
          --majd-blue: #2f8cff;
          --majd-cyan: #5ccfff;
          --majd-green: #3bd88f;
          --majd-red: #ff5c70;
          --majd-orange: #ffb347;
          --majd-text: #f4f7fb;
          --majd-muted: #8e9aab;
          --majd-border: rgba(255, 255, 255, 0.08);
          --majd-gold-border: rgba(232, 184, 76, 0.24);
        }

        * {
          box-sizing: border-box;
        }

        html {
          background: var(--majd-bg);
        }

        body {
          margin: 0;
          background: var(--majd-bg);
        }

        button,
        input,
        select,
        textarea {
          font: inherit;
        }

        button {
          -webkit-tap-highlight-color: transparent;
        }

        .majd-control-panel {
          min-height: 100vh;
          background:
            radial-gradient(circle at 80% 0%, rgba(24, 76, 143, .18), transparent 28%),
            radial-gradient(circle at 20% 10%, rgba(232, 184, 76, .08), transparent 20%),
            linear-gradient(180deg, #050912 0%, #07101c 50%, #050912 100%);
          color: var(--majd-text);
          font-family:
            "Tajawal",
            "Noto Sans Arabic",
            "Segoe UI",
            Arial,
            sans-serif;
          overflow-x: hidden;
        }

        .glass {
          background: linear-gradient(
            145deg,
            rgba(13, 24, 41, .90),
            rgba(6, 12, 23, .88)
          );
          border: 1px solid var(--majd-border);
          box-shadow:
            0 18px 55px rgba(0, 0, 0, .22),
            inset 0 1px 0 rgba(255, 255, 255, .025);
          backdrop-filter: blur(18px);
        }

        .topbar {
          height: 74px;
          position: fixed;
          top: 0;
          right: 260px;
          left: 0;
          z-index: 40;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 28px;
          background: rgba(5, 9, 18, .84);
          border-bottom: 1px solid var(--majd-border);
          backdrop-filter: blur(20px);
        }

        .topbar-title {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .topbar-title h1 {
          font-size: 17px;
          margin: 0;
          font-weight: 800;
        }

        .topbar-title small {
          display: block;
          color: var(--majd-muted);
          margin-top: 3px;
        }

        .menu-button {
          display: none;
          border: 1px solid var(--majd-border);
          background: rgba(255,255,255,.04);
          color: white;
          width: 42px;
          height: 42px;
          border-radius: 12px;
          cursor: pointer;
        }

        .top-actions {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .owner-badge {
          display: flex;
          align-items: center;
          gap: 9px;
          padding: 7px 12px;
          border: 1px solid var(--majd-gold-border);
          border-radius: 14px;
          background: rgba(232,184,76,.07);
        }

        .owner-avatar {
          width: 34px;
          height: 34px;
          display: grid;
          place-items: center;
          border-radius: 10px;
          color: #111;
          background: linear-gradient(135deg, var(--majd-gold-2), #b77b18);
          font-size: 18px;
        }

        .owner-badge strong {
          font-size: 12px;
          display: block;
        }

        .owner-badge small {
          color: var(--majd-gold);
          font-size: 10px;
        }

        .sidebar {
          position: fixed;
          right: 0;
          top: 0;
          bottom: 0;
          width: 260px;
          z-index: 50;
          background:
            linear-gradient(180deg, rgba(7, 13, 24, .99), rgba(4, 8, 15, .99));
          border-left: 1px solid var(--majd-border);
          padding: 18px 14px;
          overflow-y: auto;
        }

        .majd-logo {
          height: 58px;
          display: flex;
          align-items: center;
          gap: 11px;
          padding: 0 9px 17px;
          border-bottom: 1px solid var(--majd-border);
          margin-bottom: 18px;
          direction: ltr;
        }

        .majd-logo .crown {
          width: 43px;
          height: 43px;
          border-radius: 12px;
          display: grid;
          place-items: center;
          font-size: 25px;
          color: #171006;
          background:
            linear-gradient(145deg, #fff0a6, #d79a2e 55%, #87500b);
          box-shadow: 0 0 24px rgba(232,184,76,.2);
        }

        .majd-logo strong {
          display: block;
          color: var(--majd-gold-2);
          font-size: 20px;
          letter-spacing: 3px;
          line-height: 1;
        }

        .majd-logo span {
          color: var(--majd-muted);
          font-size: 9px;
          letter-spacing: 6px;
        }

        .nav-title {
          color: #647184;
          font-size: 10px;
          font-weight: 800;
          padding: 0 13px 8px;
        }

        .nav {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .nav button {
          border: 1px solid transparent;
          background: transparent;
          color: #aeb7c4;
          min-height: 44px;
          border-radius: 11px;
          padding: 0 13px;
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          transition: .2s ease;
          text-align: right;
        }

        .nav button:hover {
          color: white;
          background: rgba(255,255,255,.035);
        }

        .nav button.active {
          color: var(--majd-gold-2);
          background:
            linear-gradient(
              90deg,
              rgba(232,184,76,.13),
              rgba(47,140,255,.04)
            );
          border-color: rgba(232,184,76,.14);
        }

        .nav-icon {
          width: 25px;
          text-align: center;
          font-size: 17px;
        }

        .sidebar-footer {
          margin-top: 25px;
          padding: 14px;
          border-radius: 13px;
          border: 1px solid rgba(59,216,143,.14);
          background: rgba(59,216,143,.035);
        }

        .sidebar-footer strong {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
        }

        .sidebar-footer small {
          color: var(--majd-muted);
          display: block;
          margin-top: 7px;
          line-height: 1.6;
        }

        .main {
          margin-right: 260px;
          padding: 100px 28px 40px;
          min-height: 100vh;
        }

        .hero {
          position: relative;
          min-height: 360px;
          border-radius: 24px;
          overflow: hidden;
          margin-bottom: 22px;
          border-color: rgba(232,184,76,.16);
          display: flex;
          align-items: center;
        }

        .hero-background {
          position: absolute;
          inset: -8%;
          background:
            radial-gradient(circle at 78% 35%, rgba(52,130,255,.24), transparent 22%),
            radial-gradient(circle at 20% 50%, rgba(232,184,76,.09), transparent 25%),
            linear-gradient(100deg, rgba(4,8,15,.98) 25%, rgba(6,17,34,.84) 65%, rgba(6,22,45,.72));
          animation: heroMove 16s ease-in-out infinite alternate;
        }

        @keyframes heroMove {
          from { transform: scale(1.03) translate3d(0,0,0); }
          to { transform: scale(1.09) translate3d(-1.2%,1%,0); }
        }

        .stars {
          position: absolute;
          inset: 0;
          opacity: .55;
          background-image:
            radial-gradient(circle at 10% 20%, #fff 0 1px, transparent 1.5px),
            radial-gradient(circle at 30% 70%, #5ccfff 0 1px, transparent 1.5px),
            radial-gradient(circle at 70% 18%, #fff 0 1px, transparent 1.5px),
            radial-gradient(circle at 88% 60%, #ffd979 0 1px, transparent 1.5px),
            radial-gradient(circle at 55% 80%, #fff 0 1px, transparent 1.5px);
          background-size: 180px 150px;
          animation: starsMove 22s linear infinite;
        }

        @keyframes starsMove {
          from { transform: translateY(0); }
          to { transform: translateY(40px); }
        }

        .hero-glow {
          position: absolute;
          width: 260px;
          height: 260px;
          border-radius: 50%;
          filter: blur(80px);
          opacity: .14;
          animation: glowFloat 7s ease-in-out infinite alternate;
        }

        .glow-one {
          background: #287cff;
          left: 38%;
          top: -100px;
        }

        .glow-two {
          background: #e8b84c;
          right: 20%;
          bottom: -170px;
          animation-delay: -3s;
        }

        @keyframes glowFloat {
          to { transform: translate(35px, 30px) scale(1.2); }
        }

        .hero-content {
          position: relative;
          z-index: 5;
          padding: 45px 48px;
          max-width: 650px;
        }

        .hero-kicker {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: var(--majd-gold);
          font-size: 11px;
          letter-spacing: 2px;
          margin-bottom: 15px;
        }

        .hero h1 {
          font-size: clamp(32px, 5vw, 58px);
          line-height: 1.05;
          margin: 0 0 17px;
          letter-spacing: -2px;
        }

        .hero h1 span {
          color: var(--majd-gold-2);
          text-shadow: 0 0 30px rgba(232,184,76,.16);
        }

        .hero p {
          color: #aeb9c9;
          max-width: 580px;
          line-height: 1.9;
          margin: 0 0 25px;
          font-size: 14px;
        }

        .hero-buttons,
        .deploy-actions {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }

        .primary-btn,
        .secondary-btn,
        .mini-btn {
          border-radius: 11px;
          cursor: pointer;
          transition: .2s ease;
        }

        .primary-btn {
          border: 1px solid rgba(255,217,121,.4);
          padding: 12px 18px;
          color: #120e05;
          font-weight: 900;
          background:
            linear-gradient(135deg, #ffe391, #d99b2d);
          box-shadow: 0 8px 25px rgba(232,184,76,.12);
        }

        .primary-btn:hover {
          transform: translateY(-1px);
          filter: brightness(1.07);
        }

        .primary-btn:disabled {
          opacity: .55;
          cursor: wait;
        }

        .primary-btn.compact {
          padding: 9px 15px;
        }

        .secondary-btn,
        .mini-btn {
          color: #dce4ee;
          background: rgba(255,255,255,.04);
          border: 1px solid var(--majd-border);
        }

        .secondary-btn {
          padding: 12px 18px;
        }

        .mini-btn {
          padding: 7px 11px;
          font-size: 11px;
        }

        .secondary-btn:hover,
        .mini-btn:hover {
          border-color: rgba(232,184,76,.25);
          color: var(--majd-gold-2);
        }

        .danger-outline {
          color: #ff8795;
          border-color: rgba(255,92,112,.2);
        }

        .royal-emblem {
          position: absolute;
          z-index: 4;
          left: 8%;
          top: 50%;
          transform: translateY(-50%);
          width: 230px;
          height: 250px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          filter: drop-shadow(0 20px 40px rgba(0,0,0,.5));
          animation: emblemFloat 6s ease-in-out infinite alternate;
        }

        @keyframes emblemFloat {
          from { transform: translateY(-51%); }
          to { transform: translateY(-47%); }
        }

        .emblem-crown {
          position: relative;
          z-index: 2;
          font-size: 72px;
          line-height: .8;
          color: var(--majd-gold-2);
          text-shadow:
            0 0 25px rgba(232,184,76,.25),
            0 5px 0 #80500e;
        }

        .emblem-shield {
          width: 145px;
          height: 155px;
          display: grid;
          place-items: center;
          clip-path: polygon(50% 0, 92% 18%, 85% 72%, 50% 100%, 15% 72%, 8% 18%);
          background:
            linear-gradient(145deg, #e9b846, #6e410b 18%, #111a29 20%, #050a12 76%, #d99c2f 78%);
          color: #e7b547;
          font-family: Georgia, serif;
          font-size: 90px;
          font-weight: 900;
          text-shadow: 0 4px 0 #6d420e;
        }

        .emblem-name {
          color: var(--majd-gold-2);
          font-family: Georgia, serif;
          font-weight: 900;
          font-size: 34px;
          letter-spacing: 8px;
          margin-top: -5px;
        }

        .emblem-sub {
          color: #b8c4d4;
          font-size: 10px;
          letter-spacing: 10px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(6, minmax(0, 1fr));
          gap: 13px;
          margin-bottom: 22px;
        }

        .stat-card {
          min-height: 112px;
          border-radius: 17px;
          padding: 17px;
          display: flex;
          align-items: center;
          gap: 13px;
        }

        .stat-icon {
          flex: 0 0 42px;
          height: 42px;
          display: grid;
          place-items: center;
          border-radius: 12px;
          background: rgba(59,216,143,.08);
          color: var(--majd-green);
          border: 1px solid rgba(59,216,143,.1);
        }

        .stat-icon.warning {
          color: var(--majd-orange);
          background: rgba(255,179,71,.08);
        }

        .stat-icon.danger {
          color: var(--majd-red);
          background: rgba(255,92,112,.08);
        }

        .stat-copy {
          min-width: 0;
        }

        .stat-copy span,
        .stat-copy small {
          color: var(--majd-muted);
          display: block;
        }

        .stat-copy span {
          font-size: 10px;
          margin-bottom: 5px;
        }

        .stat-copy strong {
          font-size: 18px;
          display: block;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .stat-copy small {
          font-size: 9px;
          margin-top: 4px;
        }

        .dashboard-columns {
          display: grid;
          grid-template-columns: 1.25fr .75fr;
          gap: 18px;
          margin-bottom: 18px;
        }

        .panel {
          border-radius: 18px;
          padding: 20px;
          margin-bottom: 18px;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
          margin-bottom: 18px;
        }

        .section-header h2 {
          font-size: 17px;
          margin: 0;
        }

        .section-header p {
          color: var(--majd-muted);
          margin: 5px 0 0;
          font-size: 11px;
        }

        .section-actions {
          display: flex;
          gap: 8px;
        }

        .service-list {
          display: flex;
          flex-direction: column;
        }

        .service-row {
          min-height: 58px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(255,255,255,.05);
          gap: 12px;
        }

        .service-row:last-child {
          border-bottom: 0;
        }

        .service-name {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .service-name strong {
          font-size: 12px;
          display: block;
        }

        .service-name small {
          color: var(--majd-muted);
          font-size: 9px;
          display: block;
          margin-top: 3px;
        }

        .status-dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--majd-orange);
          box-shadow: 0 0 12px rgba(255,179,71,.5);
        }

        .status-dot.success {
          background: var(--majd-green);
          box-shadow: 0 0 12px rgba(59,216,143,.55);
        }

        .status-dot.danger {
          background: var(--majd-red);
          box-shadow: 0 0 12px rgba(255,92,112,.55);
        }

        .status-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 52px;
          padding: 5px 8px;
          border-radius: 999px;
          font-size: 9px;
          border: 1px solid rgba(255,179,71,.16);
          color: var(--majd-orange);
          background: rgba(255,179,71,.06);
        }

        .status-badge.success {
          color: var(--majd-green);
          border-color: rgba(59,216,143,.16);
          background: rgba(59,216,143,.06);
        }

        .status-badge.danger {
          color: var(--majd-red);
          border-color: rgba(255,92,112,.16);
          background: rgba(255,92,112,.06);
        }

        .command-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 9px;
        }

        .command-grid button {
          min-height: 77px;
          border-radius: 13px;
          border: 1px solid var(--majd-border);
          color: #d8e0eb;
          background: rgba(255,255,255,.025);
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: .2s ease;
        }

        .command-grid button:hover {
          border-color: var(--majd-gold-border);
          background: rgba(232,184,76,.055);
          color: var(--majd-gold-2);
          transform: translateY(-1px);
        }

        .command-grid b {
          font-size: 19px;
          color: var(--majd-gold);
        }

        .command-grid span {
          font-size: 10px;
        }

        .log-list {
          display: flex;
          flex-direction: column;
        }

        .log-row {
          display: grid;
          grid-template-columns: 28px 120px 1fr auto;
          align-items: center;
          gap: 10px;
          min-height: 52px;
          border-bottom: 1px solid rgba(255,255,255,.045);
        }

        .log-row:last-child {
          border-bottom: 0;
        }

        .log-symbol {
          width: 25px;
          height: 25px;
          border-radius: 8px;
          display: grid;
          place-items: center;
          color: var(--majd-green);
          background: rgba(59,216,143,.06);
        }

        .log-symbol.warning {
          color: var(--majd-orange);
          background: rgba(255,179,71,.06);
        }

        .log-symbol.danger {
          color: var(--majd-red);
          background: rgba(255,92,112,.06);
        }

        .log-row strong {
          font-size: 10px;
        }

        .log-row p {
          margin: 0;
          color: #aab4c2;
          font-size: 10px;
        }

        .log-row time {
          color: #687587;
          font-size: 9px;
        }

        .responsive-table {
          width: 100%;
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
          min-width: 720px;
        }

        th {
          color: #77869a;
          font-size: 10px;
          text-align: right;
          padding: 12px;
          border-bottom: 1px solid var(--majd-border);
        }

        td {
          padding: 14px 12px;
          color: #c6cfdb;
          font-size: 11px;
          border-bottom: 1px solid rgba(255,255,255,.045);
        }

        td strong {
          color: white;
        }

        .settings-list {
          display: flex;
          flex-direction: column;
        }

        .setting-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          padding: 15px 0;
          border-bottom: 1px solid rgba(255,255,255,.05);
        }

        .setting-row:last-child {
          border-bottom: 0;
        }

        .setting-row strong {
          display: block;
          font-size: 12px;
        }

        .setting-row p {
          color: var(--majd-muted);
          font-size: 10px;
          margin: 5px 0 0;
        }

        .toggle {
          position: relative;
          width: 45px;
          height: 25px;
          flex: 0 0 45px;
          border: 1px solid rgba(255,255,255,.1);
          border-radius: 99px;
          background: #161f2c;
          cursor: pointer;
          padding: 0;
          transition: .2s ease;
        }

        .toggle span {
          position: absolute;
          width: 19px;
          height: 19px;
          top: 2px;
          right: 3px;
          border-radius: 50%;
          background: #718095;
          transition: .2s ease;
        }

        .toggle.on {
          background: rgba(59,216,143,.13);
          border-color: rgba(59,216,143,.28);
        }

        .toggle.on span {
          right: 21px;
          background: var(--majd-green);
          box-shadow: 0 0 12px rgba(59,216,143,.4);
        }

        .feature-grid,
        .monitor-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 13px;
        }

        .feature-card {
          min-height: 150px;
          border: 1px solid var(--majd-border);
          border-radius: 15px;
          padding: 20px;
          background: rgba(255,255,255,.018);
        }

        .feature-icon {
          width: 42px;
          height: 42px;
          display: grid;
          place-items: center;
          border-radius: 12px;
          color: var(--majd-gold);
          background: rgba(232,184,76,.07);
          margin-bottom: 14px;
        }

        .feature-card h3 {
          font-size: 13px;
          margin: 0 0 7px;
        }

        .feature-card p {
          color: var(--majd-muted);
          font-size: 10px;
          line-height: 1.8;
          margin: 0;
        }

        .finance-card,
        .security-hero {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 18px;
          border-radius: 14px;
          background: rgba(255,255,255,.02);
          border: 1px solid var(--majd-border);
        }

        .finance-logo,
        .security-shield {
          width: 58px;
          height: 58px;
          flex: 0 0 58px;
          display: grid;
          place-items: center;
          border-radius: 15px;
          background: linear-gradient(145deg, #ffe28a, #a96912);
          color: #171005;
          font-weight: 900;
          font-size: 25px;
        }

        .finance-card strong,
        .security-hero h3 {
          margin: 0;
          font-size: 13px;
        }

        .finance-card p,
        .security-hero p {
          margin: 6px 0 0;
          color: var(--majd-muted);
          font-size: 10px;
          line-height: 1.7;
        }

        .security-hero {
          margin-bottom: 15px;
        }

        .pipeline {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 30px 0;
          overflow-x: auto;
        }

        .pipeline-step {
          width: 100px;
          flex: 0 0 100px;
          min-height: 100px;
          border-radius: 15px;
          border: 1px solid var(--majd-gold-border);
          background: rgba(232,184,76,.035);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }

        .pipeline-step span {
          color: var(--majd-gold);
          font-size: 9px;
        }

        .pipeline-step strong {
          margin: 7px 0;
          font-size: 11px;
        }

        .pipeline-step small {
          color: var(--majd-muted);
          font-size: 9px;
        }

        .pipeline-line {
          color: #46556a;
          padding: 0 8px;
        }

        .deploy-actions {
          justify-content: center;
          margin-top: 15px;
        }

        .monitor-card {
          border-radius: 17px;
          min-height: 180px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
        }

        .monitor-ring {
          width: 58px;
          height: 58px;
          border-radius: 50%;
          display: grid;
          place-items: center;
          border: 1px solid rgba(47,140,255,.22);
          box-shadow: inset 0 0 25px rgba(47,140,255,.06);
        }

        .monitor-card h3 {
          margin: 13px 0 6px;
          font-size: 12px;
        }

        .monitor-card strong {
          font-size: 10px;
          letter-spacing: 1px;
        }

        .monitor-card small {
          color: var(--majd-muted);
          margin-top: 5px;
          font-size: 9px;
        }

        .text-success { color: var(--majd-green); }
        .text-warning { color: var(--majd-orange); }
        .text-danger { color: var(--majd-red); }

        .system-info {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
          margin-top: 20px;
        }

        .system-info > div {
          padding: 15px;
          border: 1px solid var(--majd-border);
          border-radius: 13px;
          background: rgba(255,255,255,.02);
        }

        .system-info span {
          display: block;
          color: var(--majd-muted);
          font-size: 9px;
          margin-bottom: 6px;
        }

        .system-info strong {
          font-size: 11px;
          word-break: break-word;
        }

        .empty-state {
          min-height: 220px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #69778a;
          text-align: center;
        }

        .empty-state div {
          font-size: 40px;
          color: rgba(232,184,76,.25);
          margin-bottom: 12px;
        }

        .empty-state strong {
          font-size: 12px;
        }

        .refresh-info {
          color: var(--majd-muted);
          font-size: 9px;
          white-space: nowrap;
        }

        .loading-line {
          position: fixed;
          top: 73px;
          right: 260px;
          left: 0;
          height: 2px;
          z-index: 60;
          overflow: hidden;
          pointer-events: none;
        }

        .loading-line.active::after {
          content: "";
          position: absolute;
          width: 35%;
          height: 100%;
          background: linear-gradient(
            90deg,
            transparent,
            var(--majd-gold),
            transparent
          );
          animation: loadingMove 1.1s linear infinite;
        }

        @keyframes loadingMove {
          from { right: -35%; }
          to { right: 100%; }
        }

        .notice {
          position: fixed;
          left: 22px;
          bottom: 22px;
          z-index: 100;
          max-width: min(390px, calc(100vw - 44px));
          padding: 13px 16px;
          border-radius: 12px;
          color: #dff9eb;
          background: rgba(12,34,25,.96);
          border: 1px solid rgba(59,216,143,.2);
          box-shadow: 0 20px 50px rgba(0,0,0,.4);
          font-size: 11px;
        }

        .notice.warning {
          color: #ffe4b5;
          background: rgba(38,27,10,.97);
          border-color: rgba(255,179,71,.2);
        }

        .sidebar-overlay {
          display: none;
        }

        @media (max-width: 1250px) {
          .stats-grid {
            grid-template-columns: repeat(3, 1fr);
          }

          .royal-emblem {
            opacity: .62;
            left: 3%;
          }
        }

        @media (max-width: 900px) {
          .sidebar {
            transform: translateX(105%);
            transition: transform .25s ease;
            box-shadow: -20px 0 60px rgba(0,0,0,.5);
          }

          .sidebar.open {
            transform: translateX(0);
          }

          .sidebar-overlay {
            display: block;
            position: fixed;
            inset: 0;
            z-index: 45;
            background: rgba(0,0,0,.55);
            backdrop-filter: blur(3px);
          }

          .topbar {
            right: 0;
            padding: 0 15px;
          }

          .loading-line {
            right: 0;
          }

          .menu-button {
            display: block;
          }

          .main {
            margin-right: 0;
            padding: 92px 15px 30px;
          }

          .dashboard-columns {
            grid-template-columns: 1fr;
          }

          .feature-grid,
          .monitor-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .system-info {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (max-width: 650px) {
          .owner-badge > div:last-child {
            display: none;
          }

          .refresh-info {
            display: none;
          }

          .hero {
            min-height: 420px;
            align-items: flex-end;
          }

          .hero-content {
            padding: 28px 22px;
            background:
              linear-gradient(
                180deg,
                transparent,
                rgba(4,8,15,.9) 35%,
                rgba(4,8,15,.98)
              );
            width: 100%;
          }

          .hero h1 {
            font-size: 38px;
          }

          .hero p {
            font-size: 12px;
          }

          .royal-emblem {
            width: 170px;
            height: 190px;
            top: 32%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: .85;
          }

          @keyframes emblemFloat {
            from { transform: translate(-50%, -52%); }
            to { transform: translate(-50%, -47%); }
          }

          .emblem-crown {
            font-size: 52px;
          }

          .emblem-shield {
            width: 105px;
            height: 112px;
            font-size: 62px;
          }

          .emblem-name {
            font-size: 23px;
          }

          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .stat-card {
            padding: 13px;
            min-height: 100px;
          }

          .stat-icon {
            flex-basis: 36px;
            height: 36px;
          }

          .stat-copy strong {
            font-size: 15px;
          }

          .feature-grid,
          .monitor-grid {
            grid-template-columns: 1fr;
          }

          .command-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .log-row {
            grid-template-columns: 28px 1fr auto;
          }

          .log-row > strong {
            display: none;
          }

          .pipeline {
            justify-content: flex-start;
          }

          .system-info {
            grid-template-columns: 1fr 1fr;
          }

          .section-header {
            align-items: flex-start;
          }

          .section-header h2 {
            font-size: 15px;
          }
        }

        @media (max-width: 390px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }

          .hero-buttons button,
          .deploy-actions button {
            width: 100%;
          }

          .system-info {
            grid-template-columns: 1fr;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
          }
        }
      `}</style>

      {sidebarOpen ? (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      ) : null}

      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <MajdLogo />

        <div className="nav-title">مركز القيادة</div>

        <nav className="nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={activePage === item.id ? "active" : ""}
              onClick={() => {
                setActivePage(item.id);
                setSidebarOpen(false);
              }}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <strong>
            <StatusDot
              status={statusClass(platform.status)}
            />
            MAJD PLATFORM
          </strong>
          <small>
            {platform.domain}
            <br />
            {platform.environment}
          </small>
        </div>
      </aside>

      <header className="topbar">
        <div className="topbar-title">
          <button
            className="menu-button"
            onClick={() => setSidebarOpen(true)}
            aria-label="فتح القائمة"
          >
            ☰
          </button>

          <div>
            <h1>{currentPage}</h1>
            <small>MAJD Advanced Control Panel</small>
          </div>
        </div>

        <div className="top-actions">
          <span className="refresh-info">
            آخر تحديث{" "}
            {lastRefresh.toLocaleTimeString("ar-SA", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>

          <div className="owner-badge">
            <div className="owner-avatar">♛</div>
            <div>
              <strong>OWNER</strong>
              <small>SUPREME CONTROL</small>
            </div>
          </div>
        </div>
      </header>

      <div className={`loading-line ${loading ? "active" : ""}`} />

      <main className="main">{renderPage()}</main>

      {notice ? (
        <div className={`notice ${notice.type || ""}`}>
          {notice.message}
        </div>
      ) : null}
    </div>
  );
}

function LogList({ logs }) {
  return (
    <div className="log-list">
      {logs.map((log) => (
        <div className="log-row" key={log.id}>
          <span className={`log-symbol ${log.type}`}>
            {log.type === "success"
              ? "✓"
              : log.type === "danger"
              ? "!"
              : "•"}
          </span>
          <strong>{log.title}</strong>
          <p>{log.message}</p>
          <time>{log.time}</time>
        </div>
      ))}
    </div>
  );
}

function SettingToggle({
  title,
  description,
  value,
  onChange,
}) {
  return (
    <div className="setting-row">
      <div>
        <strong>{title}</strong>
        <p>{description}</p>
      </div>

      <Toggle checked={value} onChange={onChange} />
    </div>
  );
}

function FeatureCard({ icon, title, text }) {
  return (
    <article className="feature-card">
      <div className="feature-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}
