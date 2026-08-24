// ============================================================
// MAJD GAME FACTORY
// 09-MAJD-REAL-COMMERCE-REWARDS-INTEGRATION.jsx
// ============================================================
//
// FINAL REAL INTEGRATION UI
//
// 01. Challenges
// 02. MAJD Coins / Wallet
// 03. Moyasar Payments
// 04. Rewarded Ads
// 05. Transaction Ledger
// 06. SUPREME OWNER Controls
// 07. Backend Health / Real Status
//
// IMPORTANT:
// - NO demo balances.
// - NO fake payment success.
// - NO browser-side coin grants.
// - NO client-authoritative rewards.
// - OWNER authority must ALSO be enforced by backend.
// ============================================================

import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  ChevronLeft,
  CircleDollarSign,
  Clock3,
  Coins,
  CreditCard,
  Crown,
  Database,
  Gift,
  History,
  Loader2,
  LockKeyhole,
  Play,
  RefreshCw,
  Server,
  ShieldCheck,
  Sparkles,
  Target,
  Trophy,
  Tv,
  Wallet,
  XCircle,
  Zap,
} from "lucide-react";

// ============================================================
// CONFIG
// ============================================================

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  ""
).replace(/\/$/, "");

const ENDPOINTS = {
  me: "/api/auth/me",

  health: "/api/health",

  wallet: "/api/wallet",
  transactions: "/api/wallet/transactions",

  challenges: "/api/challenges",
  claimChallenge: (id) => `/api/challenges/${id}/claim`,

  packages: "/api/coins/packages",

  checkout: "/api/checkout",
  verifyPayment: "/api/payment/verify",

  rewardedAdStatus: "/api/ads/rewarded/status",
  rewardedAdStart: "/api/ads/rewarded/start",
  rewardedAdComplete: "/api/ads/rewarded/complete",

  ownerOverview: "/api/owner/overview",
  ownerWalletAdjust: "/api/owner/wallet/adjust",
  ownerTransactions: "/api/owner/transactions",
  ownerChallenges: "/api/owner/challenges",
  ownerPackages: "/api/owner/coins/packages",
  ownerAds: "/api/owner/ads",
  ownerPayments: "/api/owner/payments",
};

// ============================================================
// CONSTANTS
// ============================================================

const OWNER_ROLES = new Set([
  "OWNER",
  "SUPREME_OWNER",
  "MAJD_SUPREME",
]);

const PAYMENT_METHODS = [
  {
    id: "mada",
    name: "مدى",
    label: "MADA",
  },
  {
    id: "applepay",
    name: "Apple Pay",
    label: " Pay",
  },
  {
    id: "card",
    name: "بطاقة بنكية",
    label: "VISA / MC",
  },
];

// ============================================================
// HELPERS
// ============================================================

function getAuthToken() {
  try {
    return (
      localStorage.getItem("majd_token") ||
      localStorage.getItem("token") ||
      sessionStorage.getItem("majd_token") ||
      sessionStorage.getItem("token") ||
      ""
    );
  } catch {
    return "";
  }
}

async function apiRequest(
  path,
  {
    method = "GET",
    body,
    headers = {},
    signal,
  } = {}
) {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    credentials: "include",
    signal,

    headers: {
      Accept: "application/json",

      ...(body !== undefined
        ? {
            "Content-Type": "application/json",
          }
        : {}),

      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),

      ...headers,
    },

    body:
      body !== undefined
        ? JSON.stringify(body)
        : undefined,
  });

  let payload = null;

  const contentType =
    response.headers.get("content-type") || "";

  try {
    if (contentType.includes("application/json")) {
      payload = await response.json();
    } else {
      const text = await response.text();

      payload = text
        ? {
            message: text,
          }
        : null;
    }
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const error = new Error(
      payload?.message ||
        payload?.error ||
        `HTTP ${response.status}`
    );

    error.status = response.status;
    error.payload = payload;

    throw error;
  }

  return payload;
}

function formatNumber(value = 0) {
  return new Intl.NumberFormat("ar-SA").format(
    Number(value || 0)
  );
}

function formatMoney(value = 0) {
  return new Intl.NumberFormat("ar-SA", {
    style: "currency",
    currency: "SAR",
  }).format(Number(value || 0));
}

function normalizeArray(payload, key) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.[key])) {
    return payload[key];
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
}

function isOwnerUser(user) {
  const role = String(
    user?.role ||
      user?.authority ||
      user?.accountRole ||
      ""
  ).toUpperCase();

  return OWNER_ROLES.has(role);
}

function cleanPaymentQuery() {
  const url = new URL(window.location.href);

  [
    "id",
    "payment_id",
    "status",
    "message",
  ].forEach((key) => {
    url.searchParams.delete(key);
  });

  window.history.replaceState(
    {},
    document.title,
    `${url.pathname}${url.search}${url.hash}`
  );
}

// ============================================================
// UI COMPONENTS
// ============================================================

function StatusBadge({ status }) {
  const normalized = String(status || "").toLowerCase();

  const config = {
    success: {
      label: "مكتملة",
      icon: CheckCircle2,
      className:
        "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
    },

    paid: {
      label: "مدفوعة",
      icon: CheckCircle2,
      className:
        "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
    },

    completed: {
      label: "مكتملة",
      icon: CheckCircle2,
      className:
        "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
    },

    claimed: {
      label: "تم الاستلام",
      icon: CheckCircle2,
      className:
        "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
    },

    pending: {
      label: "قيد المعالجة",
      icon: Clock3,
      className:
        "border-amber-500/20 bg-amber-500/10 text-amber-300",
    },

    failed: {
      label: "فشلت",
      icon: XCircle,
      className:
        "border-red-500/20 bg-red-500/10 text-red-300",
    },
  };

  const item =
    config[normalized] || config.pending;

  const Icon = item.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${item.className}`}
    >
      <Icon size={13} />
      {item.label}
    </span>
  );
}

function StatCard({
  icon: Icon,
  title,
  value,
  subtitle,
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#09121d] p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold text-white">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {subtitle}
          </p>
        </div>

        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[#d8a43b]/20 bg-[#d8a43b]/10 text-[#f3bf54]">
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
}

function EmptyState({ children }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#09121d] p-8 text-center text-sm text-slate-500">
      {children}
    </div>
  );
}

// ============================================================
// MAIN
// ============================================================

export default function MajdRealCommerceRewardsIntegration() {
  const [activeTab, setActiveTab] =
    useState("challenges");

  const [user, setUser] = useState(null);

  const [wallet, setWallet] = useState({
    balance: 0,
    points: 0,
  });

  const [challenges, setChallenges] =
    useState([]);

  const [packages, setPackages] =
    useState([]);

  const [transactions, setTransactions] =
    useState([]);

  const [adsStatus, setAdsStatus] =
    useState({
      available: false,
      reward: 0,
    });

  const [health, setHealth] =
    useState(null);

  const [ownerOverview, setOwnerOverview] =
    useState(null);

  const [selectedPackage, setSelectedPackage] =
    useState(null);

  const [selectedPayment, setSelectedPayment] =
    useState("mada");

  const [ownerUserId, setOwnerUserId] =
    useState("");

  const [ownerCoinAmount, setOwnerCoinAmount] =
    useState("");

  const [ownerReason, setOwnerReason] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [actionLoading, setActionLoading] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  // ==========================================================
  // AUTHORITY
  // ==========================================================

  const isSupremeOwner = useMemo(
    () => isOwnerUser(user),
    [user]
  );

  const selectedPackageData = useMemo(
    () =>
      packages.find(
        (item) =>
          String(item.id) ===
          String(selectedPackage)
      ) || null,
    [packages, selectedPackage]
  );

  const completedChallenges = useMemo(
    () =>
      challenges.filter((challenge) =>
        ["completed", "claimed"].includes(
          String(challenge.status).toLowerCase()
        )
      ).length,
    [challenges]
  );

  // ==========================================================
  // DATA LOADERS
  // ==========================================================

  const loadMe = useCallback(async () => {
    const result = await apiRequest(ENDPOINTS.me);

    const account =
      result?.user ||
      result?.account ||
      result?.data ||
      result;

    setUser(account || null);

    return account;
  }, []);

  const loadHealth = useCallback(async () => {
    try {
      const result = await apiRequest(
        ENDPOINTS.health
      );

      setHealth(result);
    } catch {
      setHealth({
        status: "offline",
      });
    }
  }, []);

  const loadWallet = useCallback(async () => {
    const result = await apiRequest(
      ENDPOINTS.wallet
    );

    setWallet({
      balance: Number(
        result?.balance ??
          result?.wallet?.balance ??
          0
      ),

      points: Number(
        result?.points ??
          result?.xp ??
          result?.wallet?.points ??
          0
      ),
    });
  }, []);

  const loadChallenges = useCallback(async () => {
    const result = await apiRequest(
      ENDPOINTS.challenges
    );

    setChallenges(
      normalizeArray(result, "challenges")
    );
  }, []);

  const loadPackages = useCallback(async () => {
    const result = await apiRequest(
      ENDPOINTS.packages
    );

    const list = normalizeArray(
      result,
      "packages"
    );

    setPackages(list);

    setSelectedPackage((current) => {
      if (
        current &&
        list.some(
          (item) =>
            String(item.id) === String(current)
        )
      ) {
        return current;
      }

      return list[0]?.id ?? null;
    });
  }, []);

  const loadTransactions =
    useCallback(async () => {
      const result = await apiRequest(
        ENDPOINTS.transactions
      );

      setTransactions(
        normalizeArray(
          result,
          "transactions"
        )
      );
    }, []);

  const loadAdsStatus =
    useCallback(async () => {
      try {
        const result = await apiRequest(
          ENDPOINTS.rewardedAdStatus
        );

        setAdsStatus({
          available:
            result?.available === true,

          reward: Number(
            result?.reward || 0
          ),

          provider:
            result?.provider || null,

          remaining:
            result?.remaining ?? null,
        });
      } catch {
        setAdsStatus({
          available: false,
          reward: 0,
        });
      }
    }, []);

  const loadOwnerOverview =
    useCallback(async () => {
      try {
        const result = await apiRequest(
          ENDPOINTS.ownerOverview
        );

        setOwnerOverview(result);
      } catch (err) {
        if (err.status !== 403) {
          throw err;
        }

        setOwnerOverview(null);
      }
    }, []);

  // ==========================================================
  // REFRESH
  // ==========================================================

  const refreshAll = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const account = await loadMe();

      await Promise.all([
        loadHealth(),
        loadWallet(),
        loadChallenges(),
        loadPackages(),
        loadTransactions(),
        loadAdsStatus(),
      ]);

      if (isOwnerUser(account)) {
        await loadOwnerOverview();
      }
    } catch (err) {
      setError(
        err?.message ||
          "تعذر تحميل البيانات الحقيقية من منصة مجد."
      );
    } finally {
      setLoading(false);
    }
  }, [
    loadMe,
    loadHealth,
    loadWallet,
    loadChallenges,
    loadPackages,
    loadTransactions,
    loadAdsStatus,
    loadOwnerOverview,
  ]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // ==========================================================
  // PAYMENT CALLBACK
  // ==========================================================

  useEffect(() => {
    const params =
      new URLSearchParams(
        window.location.search
      );

    const paymentId =
      params.get("payment_id") ||
      params.get("id");

    if (!paymentId) {
      return;
    }

    let cancelled = false;

    async function verifyPayment() {
      setActionLoading(
        "verify-payment"
      );

      setError("");

      setMessage(
        "جارٍ التحقق الحقيقي من عملية الدفع..."
      );

      try {
        const result = await apiRequest(
          ENDPOINTS.verifyPayment,
          {
            method: "POST",

            body: {
              paymentId,
            },
          }
        );

        if (cancelled) {
          return;
        }

        const paid =
          result?.success === true ||
          String(
            result?.status || ""
          ).toLowerCase() === "paid";

        if (!paid) {
          throw new Error(
            result?.message ||
              "عملية الدفع لم يتم تأكيدها."
          );
        }

        await Promise.all([
          loadWallet(),
          loadTransactions(),
        ]);

        if (isSupremeOwner) {
          await loadOwnerOverview();
        }

        setMessage(
          result?.message ||
            "تم تأكيد الدفع وتحديث المحفظة من الخادم."
        );
      } catch (err) {
        if (!cancelled) {
          setMessage("");

          setError(
            err?.message ||
              "فشل التحقق من عملية الدفع."
          );
        }
      } finally {
        if (!cancelled) {
          setActionLoading("");

          cleanPaymentQuery();
        }
      }
    }

    verifyPayment();

    return () => {
      cancelled = true;
    };
  }, [
    loadWallet,
    loadTransactions,
    loadOwnerOverview,
    isSupremeOwner,
  ]);

  // ==========================================================
  // CHALLENGE CLAIM
  // ==========================================================

  async function handleClaimReward(challengeId) {
    if (actionLoading) {
      return;
    }

    setActionLoading(
      `challenge-${challengeId}`
    );

    setMessage("");
    setError("");

    try {
      const result = await apiRequest(
        ENDPOINTS.claimChallenge(
          challengeId
        ),
        {
          method: "POST",
        }
      );

      await Promise.all([
        loadChallenges(),
        loadWallet(),
        loadTransactions(),
      ]);

      setMessage(
        result?.message ||
          "تم اعتماد مكافأة التحدي من الخادم."
      );
    } catch (err) {
      setError(
        err?.message ||
          "تعذر استلام المكافأة."
      );
    } finally {
      setActionLoading("");
    }
  }

  // ==========================================================
  // MOYASAR CHECKOUT
  // ==========================================================

  async function handlePurchase() {
    if (
      !selectedPackageData ||
      actionLoading
    ) {
      return;
    }

    setActionLoading("checkout");
    setMessage("");
    setError("");

    try {
      const result = await apiRequest(
        ENDPOINTS.checkout,
        {
          method: "POST",

          body: {
            packageId:
              selectedPackageData.id,

            paymentMethod:
              selectedPayment,

            callbackUrl:
              `${window.location.origin}${window.location.pathname}`,
          },
        }
      );

      const paymentUrl =
        result?.checkoutUrl ||
        result?.paymentUrl ||
        result?.url;

      if (!paymentUrl) {
        throw new Error(
          "الخادم لم يرجع رابط الدفع الآمن."
        );
      }

      window.location.assign(paymentUrl);
    } catch (err) {
      setError(
        err?.message ||
          "تعذر بدء عملية Moyasar."
      );

      setActionLoading("");
    }
  }

  // ==========================================================
  // REWARDED ADS
  // ==========================================================

  async function handleRewardedAd() {
    if (
      actionLoading ||
      !adsStatus.available
    ) {
      return;
    }

    setActionLoading("rewarded-ad");
    setMessage("");
    setError("");

    try {
      const session = await apiRequest(
        ENDPOINTS.rewardedAdStart,
        {
          method: "POST",
        }
      );

      if (!session?.sessionId) {
        throw new Error(
          "لم يتم إنشاء جلسة إعلان صالحة."
        );
      }

      /*
       * الشبكة الفعلية يجب أن تنفذ هنا من خلال SDK
       * الخاص بمزود الإعلانات المختار.
       *
       * لا نمنح أي Coins هنا.
       *
       * إذا أعاد الخادم URL حقيقيًا لمزود الإعلان
       * يمكن فتحه، لكن اكتمال الإعلان لا يعتمد
       * على مجرد فتح النافذة.
       */

      if (session?.adUrl) {
        const popup = window.open(
          session.adUrl,
          "_blank",
          "noopener,noreferrer"
        );

        if (!popup) {
          throw new Error(
            "تعذر فتح مزود الإعلان."
          );
        }
      }

      /*
       * complete endpoint MUST verify the provider
       * proof/session server-side.
       */

      const completed = await apiRequest(
        ENDPOINTS.rewardedAdComplete,
        {
          method: "POST",

          body: {
            sessionId: session.sessionId,
          },
        }
      );

      if (completed?.success !== true) {
        throw new Error(
          completed?.message ||
            "مزود الإعلان لم يؤكد الاستحقاق."
        );
      }

      await Promise.all([
        loadWallet(),
        loadTransactions(),
        loadAdsStatus(),
      ]);

      if (isSupremeOwner) {
        await loadOwnerOverview();
      }

      setMessage(
        completed?.message ||
          "تم اعتماد مكافأة الإعلان من الخادم."
      );
    } catch (err) {
      setError(
        err?.message ||
          "تعذر إكمال الإعلان المكافئ."
      );
    } finally {
      setActionLoading("");
    }
  }

  // ==========================================================
  // SUPREME OWNER WALLET ADJUSTMENT
  // ==========================================================

  async function handleOwnerWalletAdjustment(
    direction
  ) {
    if (!isSupremeOwner) {
      setError(
        "هذه العملية مخصصة للمالك الأعلى."
      );

      return;
    }

    const amount = Math.abs(
      Number(ownerCoinAmount)
    );

    if (
      !ownerUserId.trim() ||
      !Number.isFinite(amount) ||
      amount <= 0 ||
      !ownerReason.trim()
    ) {
      setError(
        "أدخل معرف المستخدم والمبلغ والسبب الإداري."
      );

      return;
    }

    setActionLoading(
      "owner-wallet-adjust"
    );

    setMessage("");
    setError("");

    try {
      const result = await apiRequest(
        ENDPOINTS.ownerWalletAdjust,
        {
          method: "POST",

          body: {
            userId:
              ownerUserId.trim(),

            amount:
              direction === "deduct"
                ? -amount
                : amount,

            reason:
              ownerReason.trim(),

            source:
              "SUPREME_OWNER_PANEL",
          },
        }
      );

      setOwnerCoinAmount("");
      setOwnerReason("");

      await Promise.all([
        loadOwnerOverview(),
        loadTransactions(),
      ]);

      setMessage(
        result?.message ||
          "تم تنفيذ أمر المالك وتسجيله في السجل."
      );
    } catch (err) {
      setError(
        err?.message ||
          "تعذر تنفيذ أمر المالك."
      );
    } finally {
      setActionLoading("");
    }
  }

  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <section
        dir="rtl"
        className="flex min-h-screen items-center justify-center bg-[#050b12] text-white"
      >
        <div className="text-center">
          <Loader2
            size={44}
            className="mx-auto animate-spin text-[#f3bf54]"
          />

          <p className="mt-4 text-sm text-slate-400">
            جارٍ الاتصال بأنظمة مجد الحقيقية...
          </p>
        </div>
      </section>
    );
  }

  // ==========================================================
  // TABS
  // ==========================================================

  const tabs = [
    {
      id: "challenges",
      label: "التحديات",
      icon: Target,
    },
    {
      id: "coins",
      label: "العملات والباقات",
      icon: Coins,
    },
    {
      id: "payments",
      label: "الدفع",
      icon: CreditCard,
    },
    {
      id: "ads",
      label: "الإعلانات",
      icon: Tv,
    },
    {
      id: "history",
      label: "سجل العمليات",
      icon: History,
    },

    ...(isSupremeOwner
      ? [
          {
            id: "owner",
            label: "المالك الأعلى",
            icon: Crown,
          },
        ]
      : []),
  ];

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <section
      dir="rtl"
      className="min-h-screen bg-[#050b12] px-4 py-5 text-slate-100 md:px-6 lg:px-8"
    >
      <div className="mx-auto max-w-[1600px]">

        {/* HEADER */}

        <div className="mb-6 overflow-hidden rounded-3xl border border-[#d8a43b]/25 bg-[radial-gradient(circle_at_top_right,rgba(216,164,59,.18),transparent_32%),linear-gradient(135deg,#0a1521,#07101a)] p-6 md:p-8">

          <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">

            <div>
              <div className="mb-3 flex items-center gap-2 text-[#f3bf54]">
                <Crown size={22} />

                <span className="text-sm font-semibold tracking-wide">
                  MAJD REAL SYSTEM
                </span>
              </div>

              <h1 className="text-2xl font-bold md:text-3xl">
                التحديات والعملات والمدفوعات والإعلانات
              </h1>

              <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-400">
                الربط الحقيقي لمنظومة المكافآت والمحفظة
                والمدفوعات والإعلانات في منصة مجد.
              </p>

              {isSupremeOwner && (
                <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-[#d8a43b]/30 bg-[#d8a43b]/10 px-3 py-1.5 text-xs font-bold text-[#f3bf54]">
                  <Crown size={14} />
                  SUPREME OWNER — المالك الأعلى
                </div>
              )}
            </div>

            <div className="grid min-w-[300px] grid-cols-2 gap-3">

              <div className="rounded-2xl border border-[#d8a43b]/20 bg-black/20 p-4">
                <p className="text-xs text-slate-400">
                  رصيد عملات مجد
                </p>

                <p className="mt-2 text-2xl font-bold text-[#f3bf54]">
                  {formatNumber(wallet.balance)}
                </p>
              </div>

              <div className="rounded-2xl border border-violet-500/20 bg-black/20 p-4">
                <p className="text-xs text-slate-400">
                  نقاط المستوى
                </p>

                <p className="mt-2 text-2xl font-bold text-violet-300">
                  {formatNumber(wallet.points)}
                </p>
              </div>

            </div>
          </div>
        </div>

        {/* REAL SYSTEM STATUS */}

        <div className="mb-5 flex flex-wrap gap-3">

          <div
            className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs ${
              ["ok", "healthy", "online"].includes(
                String(
                  health?.status || ""
                ).toLowerCase()
              )
                ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-300"
                : "border-red-500/20 bg-red-500/10 text-red-300"
            }`}
          >
            <Server size={15} />
            Backend:
            {" "}
            {health?.status || "غير متصل"}
          </div>

          <div className="inline-flex items-center gap-2 rounded-xl border border-blue-500/20 bg-blue-500/10 px-3 py-2 text-xs text-blue-300">
            <Database size={15} />
            بيانات من الخادم
          </div>

          <div className="inline-flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-300">
            <LockKeyhole size={15} />
            Server Authoritative
          </div>

          <button
            type="button"
            onClick={refreshAll}
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 hover:bg-white/10"
          >
            <RefreshCw size={14} />
            تحديث حقيقي
          </button>

        </div>

        {/* MESSAGES */}

        {message && (
          <div className="mb-5 flex items-center justify-between rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
            <span className="flex items-center gap-2">
              <CheckCircle2 size={18} />
              {message}
            </span>

            <button
              type="button"
              onClick={() => setMessage("")}
            >
              إغلاق
            </button>
          </div>
        )}

        {error && (
          <div className="mb-5 flex items-center justify-between rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            <span className="flex items-center gap-2">
              <AlertTriangle size={18} />
              {error}
            </span>

            <button
              type="button"
              onClick={() => setError("")}
            >
              إغلاق
            </button>
          </div>
        )}

        {/* STATS */}

        <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

          <StatCard
            icon={Wallet}
            title="الرصيد الحقيقي"
            value={formatNumber(wallet.balance)}
            subtitle="من Backend مجد"
          />

          <StatCard
            icon={Trophy}
            title="التحديات المكتملة"
            value={`${completedChallenges}/${challenges.length}`}
            subtitle="تقدم حقيقي"
          />

          <StatCard
            icon={Tv}
            title="Rewarded Ads"
            value={
              adsStatus.available
                ? "متاحة"
                : "غير متاحة"
            }
            subtitle={
              adsStatus.provider ||
              "مزود الإعلانات"
            }
          />

          <StatCard
            icon={ShieldCheck}
            title="المدفوعات"
            value="Moyasar"
            subtitle="تحقق من الخادم"
          />

        </div>

        {/* TABS */}

        <div className="mb-6 flex overflow-x-auto rounded-2xl border border-white/10 bg-[#09121d] p-1.5">

          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active =
              activeTab === tab.id;

            return (
              <button
                key={tab.id}
                type="button"
                onClick={() =>
                  setActiveTab(tab.id)
                }
                className={`flex min-w-max flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition ${
                  active
                    ? "bg-[#d8a43b] text-black"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon size={17} />
                {tab.label}
              </button>
            );
          })}

        </div>

        {/* ====================================================
            CHALLENGES
        ==================================================== */}

        {activeTab === "challenges" && (
          <div className="grid gap-4 md:grid-cols-2">

            {challenges.length === 0 && (
              <div className="md:col-span-2">
                <EmptyState>
                  لا توجد تحديات حقيقية متاحة حالياً.
                </EmptyState>
              </div>
            )}

            {challenges.map((challenge) => {
              const progress = Number(
                challenge.progress || 0
              );

              const target = Math.max(
                1,
                Number(challenge.target || 1)
              );

              const percent = Math.min(
                100,
                Math.round(
                  (progress / target) * 100
                )
              );

              const claimed =
                String(
                  challenge.status
                ).toLowerCase() === "claimed";

              const claimable =
                progress >= target &&
                !claimed;

              const claiming =
                actionLoading ===
                `challenge-${challenge.id}`;

              return (
                <article
                  key={challenge.id}
                  className="rounded-2xl border border-white/10 bg-[#09121d] p-5"
                >

                  <div className="flex items-start justify-between gap-3">

                    <div>
                      <h3 className="font-bold text-white">
                        {challenge.title}
                      </h3>

                      <p className="mt-1 text-xs leading-6 text-slate-500">
                        {challenge.description}
                      </p>
                    </div>

                    {claimed && (
                      <StatusBadge status="claimed" />
                    )}
                  </div>

                  <div className="mt-5">

                    <div className="mb-2 flex justify-between text-xs">
                      <span className="text-slate-400">
                        التقدم
                      </span>

                      <span>
                        {formatNumber(progress)}
                        {" / "}
                        {formatNumber(target)}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-white/5">
                      <div
                        className="h-full rounded-full bg-gradient-to-l from-[#d8a43b] to-[#ffde82]"
                        style={{
                          width: `${percent}%`,
                        }}
                      />
                    </div>

                  </div>

                  <div className="mt-5 flex items-center justify-between gap-3">

                    <div className="flex flex-wrap gap-2">

                      <span className="inline-flex items-center gap-1 rounded-lg bg-[#d8a43b]/10 px-2.5 py-1.5 text-xs text-[#f3bf54]">
                        <Coins size={14} />
                        {formatNumber(
                          challenge.reward
                        )}
                      </span>

                      <span className="inline-flex items-center gap-1 rounded-lg bg-violet-500/10 px-2.5 py-1.5 text-xs text-violet-300">
                        <Zap size={14} />
                        {formatNumber(
                          challenge.xp
                        )} XP
                      </span>

                    </div>

                    <button
                      type="button"
                      disabled={
                        !claimable ||
                        claiming
                      }
                      onClick={() =>
                        handleClaimReward(
                          challenge.id
                        )
                      }
                      className="rounded-xl bg-[#d8a43b] px-4 py-2 text-xs font-bold text-black disabled:cursor-not-allowed disabled:bg-white/5 disabled:text-slate-600"
                    >
                      {claiming
                        ? "جارٍ التحقق..."
                        : claimed
                        ? "تم الاستلام"
                        : claimable
                        ? "استلام المكافأة"
                        : "قيد التقدم"}
                    </button>

                  </div>
                </article>
              );
            })}

          </div>
        )}

        {/* ====================================================
            COINS
        ==================================================== */}

        {activeTab === "coins" && (
          <div>

            <h2 className="mb-5 text-lg font-bold">
              باقات عملات مجد
            </h2>

            {packages.length === 0 ? (
              <EmptyState>
                لا توجد باقات مفعلة من الخادم.
              </EmptyState>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

                {packages.map((item) => {
                  const selected =
                    String(selectedPackage) ===
                    String(item.id);

                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() =>
                        setSelectedPackage(
                          item.id
                        )
                      }
                      className={`rounded-2xl border p-5 text-right ${
                        selected
                          ? "border-[#d8a43b] bg-[#d8a43b]/10"
                          : "border-white/10 bg-[#09121d]"
                      }`}
                    >

                      <Coins
                        size={28}
                        className="text-[#f3bf54]"
                      />

                      <h3 className="mt-4 font-bold">
                        {item.name}
                      </h3>

                      <p className="mt-3 text-2xl font-bold text-[#f3bf54]">
                        {formatNumber(item.coins)}
                      </p>

                      {Number(item.bonus || 0) > 0 && (
                        <p className="mt-2 text-xs text-emerald-300">
                          + {formatNumber(item.bonus)} هدية
                        </p>
                      )}

                      <p className="mt-5 border-t border-white/5 pt-4 text-lg font-bold">
                        {formatMoney(item.price)}
                      </p>

                    </button>
                  );
                })}

              </div>
            )}

          </div>
        )}

        {/* ====================================================
            PAYMENT
        ==================================================== */}

        {activeTab === "payments" && (
          <div className="grid gap-5 lg:grid-cols-[1fr_380px]">

            <div className="rounded-2xl border border-white/10 bg-[#09121d] p-5">

              <h2 className="text-lg font-bold">
                الدفع الحقيقي
              </h2>

              <div className="mt-5 space-y-3">

                {PAYMENT_METHODS.map(
                  (method) => (
                    <button
                      key={method.id}
                      type="button"
                      onClick={() =>
                        setSelectedPayment(
                          method.id
                        )
                      }
                      className={`flex w-full items-center justify-between rounded-xl border p-4 ${
                        selectedPayment ===
                        method.id
                          ? "border-[#d8a43b] bg-[#d8a43b]/10"
                          : "border-white/10"
                      }`}
                    >
                      <span>
                        {method.name}
                      </span>

                      <span className="text-sm text-slate-400">
                        {method.label}
                      </span>
                    </button>
                  )
                )}

              </div>

              <div className="mt-5 rounded-xl border border-blue-500/10 bg-blue-500/5 p-4 text-xs leading-6 text-slate-400">
                بيانات البطاقة لا تمنح الرصيد من
                React. نجاح العملية يعتمد على
                تحقق Moyasar والخادم.
              </div>

            </div>

            <aside className="rounded-2xl border border-[#d8a43b]/20 bg-[#09121d] p-5">

              <h3 className="font-bold">
                ملخص الطلب
              </h3>

              {selectedPackageData ? (
                <>
                  <div className="mt-5 space-y-3 text-sm">

                    <div className="flex justify-between">
                      <span className="text-slate-400">
                        الباقة
                      </span>

                      <span>
                        {selectedPackageData.name}
                      </span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-slate-400">
                        العملات
                      </span>

                      <span>
                        {formatNumber(
                          selectedPackageData.coins
                        )}
                      </span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-slate-400">
                        المكافأة
                      </span>

                      <span className="text-emerald-300">
                        +{" "}
                        {formatNumber(
                          selectedPackageData.bonus ||
                            0
                        )}
                      </span>
                    </div>

                    <div className="flex justify-between border-t border-white/10 pt-4">
                      <span>
                        الإجمالي
                      </span>

                      <strong className="text-xl text-[#f3bf54]">
                        {formatMoney(
                          selectedPackageData.price
                        )}
                      </strong>
                    </div>

                  </div>

                  <button
                    type="button"
                    onClick={handlePurchase}
                    disabled={
                      actionLoading ===
                      "checkout"
                    }
                    className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-[#d8a43b] px-4 py-3 font-bold text-black disabled:opacity-50"
                  >
                    {actionLoading ===
                    "checkout" ? (
                      <>
                        <Loader2
                          size={17}
                          className="animate-spin"
                        />
                        جارٍ فتح Moyasar
                      </>
                    ) : (
                      <>
                        إتمام الدفع
                        <ChevronLeft size={18} />
                      </>
                    )}
                  </button>
                </>
              ) : (
                <p className="mt-5 text-sm text-slate-500">
                  اختر باقة أولاً.
                </p>
              )}

            </aside>
          </div>
        )}

        {/* ====================================================
            ADS
        ==================================================== */}

        {activeTab === "ads" && (
          <div className="rounded-2xl border border-white/10 bg-[#09121d] p-6">

            <Tv
              size={32}
              className="text-violet-300"
            />

            <h2 className="mt-4 text-xl font-bold">
              الإعلانات المكافئة
            </h2>

            <p className="mt-2 text-sm leading-7 text-slate-500">
              المكافأة لا تعتمد على الضغط.
              يجب أن يؤكد مزود الإعلان والخادم
              اكتمال الجلسة قبل إضافة العملات.
            </p>

            <div className="mt-5 rounded-xl border border-white/10 bg-black/20 p-4">

              <p className="text-xs text-slate-500">
                المكافأة
              </p>

              <p className="mt-1 text-xl font-bold text-[#f3bf54]">
                {formatNumber(
                  adsStatus.reward
                )}{" "}
                عملة
              </p>

            </div>

            <button
              type="button"
              disabled={
                !adsStatus.available ||
                actionLoading ===
                  "rewarded-ad"
              }
              onClick={handleRewardedAd}
              className="mt-5 flex items-center gap-2 rounded-xl bg-violet-500 px-5 py-3 font-bold text-white disabled:opacity-40"
            >
              <Play size={18} />

              {actionLoading ===
              "rewarded-ad"
                ? "جارٍ التحقق..."
                : "مشاهدة إعلان"}
            </button>

          </div>
        )}

        {/* ====================================================
            HISTORY
        ==================================================== */}

        {activeTab === "history" && (
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#09121d]">

            <div className="border-b border-white/10 p-5">
              <h2 className="font-bold">
                سجل العمليات الحقيقي
              </h2>
            </div>

            {transactions.length === 0 ? (
              <div className="p-5">
                <EmptyState>
                  لا توجد عمليات مسجلة.
                </EmptyState>
              </div>
            ) : (
              <div className="divide-y divide-white/5">

                {transactions.map(
                  (transaction) => {
                    const coins = Number(
                      transaction.coins || 0
                    );

                    return (
                      <div
                        key={transaction.id}
                        className="flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between"
                      >

                        <div className="flex items-center gap-3">

                          {coins >= 0 ? (
                            <ArrowUpRight
                              className="text-emerald-300"
                            />
                          ) : (
                            <ArrowDownRight
                              className="text-red-300"
                            />
                          )}

                          <div>
                            <p className="font-medium">
                              {transaction.title}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {transaction.id}
                              {" · "}
                              {transaction.date ||
                                transaction.createdAt}
                            </p>
                          </div>

                        </div>

                        <div className="flex items-center gap-4">

                          <div className="text-left">
                            <p
                              className={
                                coins >= 0
                                  ? "font-bold text-emerald-300"
                                  : "font-bold text-red-300"
                              }
                            >
                              {coins > 0 ? "+" : ""}
                              {formatNumber(coins)}
                              {" "}
                              عملة
                            </p>

                            {Number(
                              transaction.amount || 0
                            ) > 0 && (
                              <p className="text-xs text-slate-500">
                                {formatMoney(
                                  transaction.amount
                                )}
                              </p>
                            )}
                          </div>

                          <StatusBadge
                            status={
                              transaction.status
                            }
                          />

                        </div>
                      </div>
                    );
                  }
                )}

              </div>
            )}

          </div>
        )}

        {/* ====================================================
            SUPREME OWNER
        ==================================================== */}

        {activeTab === "owner" &&
          isSupremeOwner && (
            <div className="space-y-5">

              <div className="rounded-3xl border border-[#d8a43b]/30 bg-[linear-gradient(135deg,rgba(216,164,59,.15),rgba(9,18,29,.95))] p-6">

                <div className="flex items-center gap-3">
                  <Crown
                    size={30}
                    className="text-[#f3bf54]"
                  />

                  <div>
                    <p className="text-xs text-[#f3bf54]">
                      MAJD
                    </p>

                    <h2 className="text-xl font-bold">
                      SUPREME OWNER
                    </h2>

                    <p className="text-xs text-slate-500">
                      المالك الأعلى
                    </p>
                  </div>
                </div>

                <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">

                  <StatCard
                    icon={CircleDollarSign}
                    title="إجمالي الإيرادات"
                    value={formatMoney(
                      ownerOverview?.revenue ||
                        0
                    )}
                    subtitle="من الخادم"
                  />

                  <StatCard
                    icon={CreditCard}
                    title="المدفوعات"
                    value={formatNumber(
                      ownerOverview?.payments ||
                        0
                    )}
                    subtitle="عمليات مسجلة"
                  />

                  <StatCard
                    icon={Coins}
                    title="العملات المتداولة"
                    value={formatNumber(
                      ownerOverview?.coinsInCirculation ||
                        0
                    )}
                    subtitle="MAJD Coins"
                  />

                  <StatCard
                    icon={Activity}
                    title="الإعلانات المكافئة"
                    value={formatNumber(
                      ownerOverview?.rewardedAds ||
                        0
                    )}
                    subtitle="جلسات مؤكدة"
                  />

                </div>
              </div>

              {/* OWNER WALLET CONTROL */}

              <div className="rounded-2xl border border-[#d8a43b]/20 bg-[#09121d] p-5">

                <div className="flex items-center gap-2">
                  <ShieldCheck
                    className="text-[#f3bf54]"
                  />

                  <h3 className="font-bold">
                    أمر المالك — إدارة الرصيد
                  </h3>
                </div>

                <p className="mt-2 text-xs leading-6 text-slate-500">
                  أي إضافة أو خصم يجب أن يتحقق
                  منه Backend كصلاحية مالك أعلى
                  ويسجل في سجل التدقيق.
                </p>

                <div className="mt-5 grid gap-3 lg:grid-cols-3">

                  <input
                    value={ownerUserId}
                    onChange={(event) =>
                      setOwnerUserId(
                        event.target.value
                      )
                    }
                    placeholder="معرف المستخدم"
                    className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none focus:border-[#d8a43b]/50"
                  />

                  <input
                    type="number"
                    min="1"
                    value={ownerCoinAmount}
                    onChange={(event) =>
                      setOwnerCoinAmount(
                        event.target.value
                      )
                    }
                    placeholder="عدد العملات"
                    className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none focus:border-[#d8a43b]/50"
                  />

                  <input
                    value={ownerReason}
                    onChange={(event) =>
                      setOwnerReason(
                        event.target.value
                      )
                    }
                    placeholder="سبب العملية"
                    className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none focus:border-[#d8a43b]/50"
                  />

                </div>

                <div className="mt-4 flex flex-wrap gap-3">

                  <button
                    type="button"
                    disabled={
                      actionLoading ===
                      "owner-wallet-adjust"
                    }
                    onClick={() =>
                      handleOwnerWalletAdjustment(
                        "add"
                      )
                    }
                    className="rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50"
                  >
                    إضافة رصيد
                  </button>

                  <button
                    type="button"
                    disabled={
                      actionLoading ===
                      "owner-wallet-adjust"
                    }
                    onClick={() =>
                      handleOwnerWalletAdjustment(
                        "deduct"
                      )
                    }
                    className="rounded-xl bg-red-500 px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50"
                  >
                    خصم رصيد
                  </button>

                </div>

              </div>

              {/* OWNER REAL INTEGRATIONS */}

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

                {[
                  {
                    icon: CreditCard,
                    title: "Moyasar",
                    value:
                      ownerOverview?.moyasarStatus ||
                      "متصل بالخادم",
                  },
                  {
                    icon: Tv,
                    title: "الإعلانات",
                    value:
                      ownerOverview?.adsStatus ||
                      adsStatus.provider ||
                      "بانتظار المزود",
                  },
                  {
                    icon: Target,
                    title: "التحديات",
                    value: `${challenges.length} تحدي`,
                  },
                  {
                    icon: Database,
                    title: "السجل المالي",
                    value: `${transactions.length} عملية`,
                  },
                ].map((item) => {
                  const Icon = item.icon;

                  return (
                    <div
                      key={item.title}
                      className="rounded-2xl border border-white/10 bg-[#09121d] p-5"
                    >
                      <Icon
                        size={22}
                        className="text-[#f3bf54]"
                      />

                      <p className="mt-4 text-sm text-slate-400">
                        {item.title}
                      </p>

                      <p className="mt-1 font-bold">
                        {item.value}
                      </p>
                    </div>
                  );
                })}

              </div>

            </div>
          )}

      </div>
    </section>
  );
}
