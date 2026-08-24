import React, { useMemo, useState } from "react";
import {
  Trophy,
  Coins,
  CreditCard,
  Gift,
  Wallet,
  CheckCircle2,
  Clock3,
  XCircle,
  ChevronLeft,
  Crown,
  Star,
  Zap,
  ShieldCheck,
  ArrowUpRight,
  ArrowDownRight,
  History,
  Gem,
  Target,
  Sparkles,
} from "lucide-react";

const challenges = [
  {
    id: 1,
    title: "أكمل 3 مباريات اليوم",
    description: "شارك في ثلاث مباريات مؤهلة خلال اليوم.",
    progress: 2,
    target: 3,
    reward: 250,
    xp: 120,
    status: "active",
  },
  {
    id: 2,
    title: "حقق 5 انتصارات",
    description: "اربح خمس مباريات في أي لعبة تنافسية.",
    progress: 5,
    target: 5,
    reward: 500,
    xp: 250,
    status: "completed",
  },
  {
    id: 3,
    title: "شاهد بثاً مباشراً",
    description: "تابع بثاً مباشراً مؤهلاً لمدة 10 دقائق.",
    progress: 4,
    target: 10,
    reward: 150,
    xp: 75,
    status: "active",
  },
  {
    id: 4,
    title: "تحدي المجتمع الأسبوعي",
    description: "اجمع نقاط نشاط من الألعاب والمحتوى والمجتمع.",
    progress: 820,
    target: 1000,
    reward: 1200,
    xp: 600,
    status: "active",
  },
];

const coinPackages = [
  {
    id: "starter",
    name: "حزمة البداية",
    coins: 1000,
    bonus: 0,
    price: 9,
    popular: false,
  },
  {
    id: "silver",
    name: "الحزمة الفضية",
    coins: 2500,
    bonus: 250,
    price: 19,
    popular: false,
  },
  {
    id: "gold",
    name: "الحزمة الذهبية",
    coins: 6000,
    bonus: 1000,
    price: 39,
    popular: true,
  },
  {
    id: "royal",
    name: "الحزمة الملكية",
    coins: 15000,
    bonus: 3500,
    price: 79,
    popular: false,
  },
];

const transactionsSeed = [
  {
    id: "TX-982101",
    type: "purchase",
    title: "شراء الحزمة الذهبية",
    amount: 39,
    currency: "SAR",
    coins: 7000,
    date: "اليوم 12:41",
    status: "success",
  },
  {
    id: "TX-982087",
    type: "reward",
    title: "مكافأة تحدي يومي",
    amount: 0,
    currency: "SAR",
    coins: 500,
    date: "اليوم 10:22",
    status: "success",
  },
  {
    id: "TX-981944",
    type: "spend",
    title: "شراء عنصر داخل اللعبة",
    amount: 0,
    currency: "SAR",
    coins: -850,
    date: "أمس 21:17",
    status: "success",
  },
  {
    id: "TX-981802",
    type: "purchase",
    title: "محاولة شحن رصيد",
    amount: 19,
    currency: "SAR",
    coins: 2750,
    date: "أمس 18:03",
    status: "failed",
  },
];

const paymentMethods = [
  { id: "mada", name: "مدى", label: "MADA" },
  { id: "applepay", name: "Apple Pay", label: " Pay" },
  { id: "card", name: "بطاقة بنكية", label: "VISA / MC" },
];

function formatNumber(value) {
  return new Intl.NumberFormat("ar-SA").format(value);
}

function StatusBadge({ status }) {
  const config = {
    success: {
      label: "مكتملة",
      className:
        "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
      icon: CheckCircle2,
    },
    pending: {
      label: "قيد المعالجة",
      className: "border-amber-500/20 bg-amber-500/10 text-amber-300",
      icon: Clock3,
    },
    failed: {
      label: "فشلت",
      className: "border-red-500/20 bg-red-500/10 text-red-300",
      icon: XCircle,
    },
  };

  const item = config[status] || config.pending;
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

function StatCard({ icon: Icon, title, value, subtitle }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#09121d] p-5 shadow-[0_20px_50px_rgba(0,0,0,.25)]">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{title}</p>
          <p className="mt-2 text-2xl font-bold text-white">{value}</p>
          <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
        </div>

        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[#d8a43b]/20 bg-[#d8a43b]/10 text-[#f3bf54]">
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
}

export default function MajdChallengesCoinsPayments() {
  const [activeTab, setActiveTab] = useState("challenges");
  const [balance, setBalance] = useState(78450);
  const [points, setPoints] = useState(12480);
  const [selectedPackage, setSelectedPackage] = useState("gold");
  const [selectedPayment, setSelectedPayment] = useState("mada");
  const [transactions, setTransactions] = useState(transactionsSeed);
  const [challengeState, setChallengeState] = useState(challenges);
  const [message, setMessage] = useState("");

  const completedChallenges = useMemo(
    () => challengeState.filter((item) => item.status === "completed").length,
    [challengeState]
  );

  const selectedPackageData = useMemo(
    () => coinPackages.find((item) => item.id === selectedPackage),
    [selectedPackage]
  );

  const handleClaimReward = (challengeId) => {
    setChallengeState((current) =>
      current.map((challenge) => {
        if (
          challenge.id === challengeId &&
          challenge.progress >= challenge.target
        ) {
          setBalance((value) => value + challenge.reward);
          setPoints((value) => value + challenge.xp);

          setTransactions((items) => [
            {
              id: `TX-${Date.now()}`,
              type: "reward",
              title: `مكافأة: ${challenge.title}`,
              amount: 0,
              currency: "SAR",
              coins: challenge.reward,
              date: "الآن",
              status: "success",
            },
            ...items,
          ]);

          setMessage(
            `تمت إضافة ${formatNumber(challenge.reward)} عملة إلى رصيدك.`
          );

          return {
            ...challenge,
            status: "claimed",
          };
        }

        return challenge;
      })
    );
  };

  const handlePurchase = () => {
    if (!selectedPackageData) return;

    const totalCoins =
      selectedPackageData.coins + selectedPackageData.bonus;

    setTransactions((items) => [
      {
        id: `TX-${Date.now()}`,
        type: "purchase",
        title: `شراء ${selectedPackageData.name}`,
        amount: selectedPackageData.price,
        currency: "SAR",
        coins: totalCoins,
        date: "الآن",
        status: "success",
      },
      ...items,
    ]);

    setBalance((value) => value + totalCoins);

    setMessage(
      `تمت العملية بنجاح وإضافة ${formatNumber(
        totalCoins
      )} عملة مجد إلى محفظتك.`
    );
  };

  return (
    <section
      dir="rtl"
      className="min-h-screen bg-[#050b12] px-4 py-5 text-slate-100 md:px-6 lg:px-8"
    >
      <div className="mx-auto max-w-[1600px]">
        <div className="mb-6 overflow-hidden rounded-3xl border border-[#d8a43b]/25 bg-[radial-gradient(circle_at_top_right,rgba(216,164,59,.18),transparent_32%),linear-gradient(135deg,#0a1521,#07101a)] p-6 md:p-8">
          <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
            <div>
              <div className="mb-3 flex items-center gap-2 text-[#f3bf54]">
                <Crown size={22} />
                <span className="text-sm font-semibold tracking-wide">
                  MAJD REWARDS & PAYMENTS
                </span>
              </div>

              <h1 className="text-2xl font-bold md:text-3xl">
                التحديات والعملات والمدفوعات
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-400">
                مركز موحد لإدارة تحديات مجد، المكافآت، رصيد العملات، الباقات
                وعمليات الدفع وسجل المعاملات.
              </p>
            </div>

            <div className="grid min-w-[300px] grid-cols-2 gap-3">
              <div className="rounded-2xl border border-[#d8a43b]/20 bg-black/20 p-4">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Coins size={15} className="text-[#f3bf54]" />
                  رصيد عملات مجد
                </div>
                <div className="mt-2 text-2xl font-bold text-[#f3bf54]">
                  {formatNumber(balance)}
                </div>
              </div>

              <div className="rounded-2xl border border-violet-500/20 bg-black/20 p-4">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Sparkles size={15} className="text-violet-400" />
                  نقاط المستوى
                </div>
                <div className="mt-2 text-2xl font-bold text-violet-300">
                  {formatNumber(points)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {message && (
          <div className="mb-5 flex items-center justify-between gap-4 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={18} />
              {message}
            </div>

            <button
              type="button"
              onClick={() => setMessage("")}
              className="text-emerald-200/70 transition hover:text-white"
            >
              إغلاق
            </button>
          </div>
        )}

        <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            icon={Coins}
            title="الرصيد الحالي"
            value={formatNumber(balance)}
            subtitle="عملة مجد"
          />

          <StatCard
            icon={Trophy}
            title="التحديات المكتملة"
            value={`${completedChallenges}/${challengeState.length}`}
            subtitle="تحديات المرحلة الحالية"
          />

          <StatCard
            icon={Gift}
            title="مكافآت الشهر"
            value="8,650"
            subtitle="عملة تم الحصول عليها"
          />

          <StatCard
            icon={ShieldCheck}
            title="حالة المدفوعات"
            value="محمية"
            subtitle="عمليات آمنة ومشفرة"
          />
        </div>

        <div className="mb-6 flex overflow-x-auto rounded-2xl border border-white/10 bg-[#09121d] p-1.5">
          {[
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
              id: "history",
              label: "سجل العمليات",
              icon: History,
            },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex min-w-max flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition ${
                  active
                    ? "bg-[#d8a43b] text-[#111]"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon size={17} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {activeTab === "challenges" && (
          <div className="grid gap-5 xl:grid-cols-[1fr_340px]">
            <div className="grid gap-4 md:grid-cols-2">
              {challengeState.map((challenge) => {
                const percent = Math.min(
                  100,
                  Math.round((challenge.progress / challenge.target) * 100)
                );

                const claimable =
                  challenge.progress >= challenge.target &&
                  challenge.status !== "claimed";

                return (
                  <article
                    key={challenge.id}
                    className="rounded-2xl border border-white/10 bg-[#09121d] p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex gap-3">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-[#d8a43b]/20 bg-[#d8a43b]/10 text-[#f3bf54]">
                          <Trophy size={21} />
                        </div>

                        <div>
                          <h3 className="font-bold text-white">
                            {challenge.title}
                          </h3>
                          <p className="mt-1 text-xs leading-6 text-slate-500">
                            {challenge.description}
                          </p>
                        </div>
                      </div>

                      {challenge.status === "claimed" && (
                        <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-1 text-[11px] text-emerald-300">
                          تم الاستلام
                        </span>
                      )}
                    </div>

                    <div className="mt-5">
                      <div className="mb-2 flex items-center justify-between text-xs">
                        <span className="text-slate-400">التقدم</span>
                        <span className="text-white">
                          {formatNumber(challenge.progress)} /{" "}
                          {formatNumber(challenge.target)}
                        </span>
                      </div>

                      <div className="h-2 overflow-hidden rounded-full bg-white/5">
                        <div
                          className="h-full rounded-full bg-gradient-to-l from-[#d8a43b] to-[#ffde82]"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>

                    <div className="mt-5 flex items-center justify-between gap-3">
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-lg bg-[#d8a43b]/10 px-2.5 py-1.5 text-xs text-[#f3bf54]">
                          <Coins size={14} />
                          {formatNumber(challenge.reward)}
                        </span>

                        <span className="inline-flex items-center gap-1 rounded-lg bg-violet-500/10 px-2.5 py-1.5 text-xs text-violet-300">
                          <Zap size={14} />
                          {formatNumber(challenge.xp)} XP
                        </span>
                      </div>

                      <button
                        type="button"
                        disabled={!claimable}
                        onClick={() => handleClaimReward(challenge.id)}
                        className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
                          claimable
                            ? "bg-[#d8a43b] text-black hover:bg-[#efc05b]"
                            : "cursor-not-allowed bg-white/5 text-slate-600"
                        }`}
                      >
                        {challenge.status === "claimed"
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

            <aside className="rounded-2xl border border-[#d8a43b]/20 bg-[linear-gradient(180deg,rgba(216,164,59,.12),rgba(9,18,29,.9))] p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#d8a43b]/15 text-[#f3bf54]">
                  <Crown size={25} />
                </div>

                <div>
                  <p className="text-xs text-slate-400">المستوى الحالي</p>
                  <h3 className="font-bold text-white">المستوى الملكي 99</h3>
                </div>
              </div>

              <div className="mt-6 rounded-xl border border-white/10 bg-black/20 p-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">تقدم المستوى</span>
                  <span className="text-[#f3bf54]">78,540 / 100,000 XP</span>
                </div>

                <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/5">
                  <div className="h-full w-[78%] rounded-full bg-[#d8a43b]" />
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {[
                  ["مكافأة الدخول اليومي", "150 عملة"],
                  ["سلسلة النشاط", "7 أيام"],
                  ["مضاعف XP", "x1.5"],
                  ["ترتيب التحديات", "#18"],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.02] px-3 py-3"
                  >
                    <span className="text-sm text-slate-400">{label}</span>
                    <span className="text-sm font-bold text-white">{value}</span>
                  </div>
                ))}
              </div>
            </aside>
          </div>
        )}

        {activeTab === "coins" && (
          <div>
            <div className="mb-5">
              <h2 className="text-lg font-bold text-white">باقات عملات مجد</h2>
              <p className="mt-1 text-sm text-slate-500">
                اختر الباقة المناسبة وسيتم إضافتها مباشرة إلى محفظتك بعد نجاح
                الدفع.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {coinPackages.map((item) => {
                const selected = selectedPackage === item.id;

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedPackage(item.id)}
                    className={`relative rounded-2xl border p-5 text-right transition ${
                      selected
                        ? "border-[#d8a43b] bg-[#d8a43b]/10"
                        : "border-white/10 bg-[#09121d] hover:border-white/20"
                    }`}
                  >
                    {item.popular && (
                      <span className="absolute left-4 top-4 rounded-full bg-[#d8a43b] px-2 py-1 text-[10px] font-bold text-black">
                        الأكثر اختياراً
                      </span>
                    )}

                    <Gem className="mb-5 text-[#f3bf54]" size={28} />

                    <h3 className="font-bold text-white">{item.name}</h3>

                    <p className="mt-3 text-2xl font-bold text-[#f3bf54]">
                      {formatNumber(item.coins)}
                    </p>

                    <p className="text-xs text-slate-500">عملة مجد</p>

                    {item.bonus > 0 && (
                      <div className="mt-3 inline-flex items-center gap-1 rounded-lg bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300">
                        <Gift size={13} />
                        + {formatNumber(item.bonus)} هدية
                      </div>
                    )}

                    <div className="mt-5 border-t border-white/5 pt-4">
                      <span className="text-lg font-bold text-white">
                        {item.price} SAR
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === "payments" && selectedPackageData && (
          <div className="grid gap-5 lg:grid-cols-[1fr_380px]">
            <div className="rounded-2xl border border-white/10 bg-[#09121d] p-5">
              <h2 className="text-lg font-bold text-white">طريقة الدفع</h2>

              <div className="mt-5 grid gap-3">
                {paymentMethods.map((method) => {
                  const selected = selectedPayment === method.id;

                  return (
                    <button
                      key={method.id}
                      type="button"
                      onClick={() => setSelectedPayment(method.id)}
                      className={`flex items-center justify-between rounded-xl border px-4 py-4 transition ${
                        selected
                          ? "border-[#d8a43b] bg-[#d8a43b]/10"
                          : "border-white/10 bg-black/10 hover:bg-white/[0.03]"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5">
                          <CreditCard size={20} />
                        </div>

                        <span className="font-medium text-white">
                          {method.name}
                        </span>
                      </div>

                      <span className="text-sm font-bold text-slate-400">
                        {method.label}
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="mt-6 flex items-start gap-3 rounded-xl border border-blue-500/10 bg-blue-500/5 p-4 text-xs leading-6 text-slate-400">
                <ShieldCheck
                  size={18}
                  className="mt-0.5 shrink-0 text-blue-300"
                />
                يتم تنفيذ الدفع من خلال بوابة دفع آمنة. لا يتم تخزين بيانات
                البطاقة الحساسة داخل واجهة مجد.
              </div>
            </div>

            <aside className="rounded-2xl border border-[#d8a43b]/20 bg-[#09121d] p-5">
              <h3 className="font-bold text-white">ملخص الطلب</h3>

              <div className="mt-5 space-y-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">الباقة</span>
                  <span className="text-white">
                    {selectedPackageData.name}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-slate-400">العملات</span>
                  <span className="text-white">
                    {formatNumber(selectedPackageData.coins)}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-slate-400">الهدية</span>
                  <span className="text-emerald-300">
                    + {formatNumber(selectedPackageData.bonus)}
                  </span>
                </div>

                <div className="border-t border-white/10 pt-4">
                  <div className="flex items-end justify-between">
                    <span className="text-slate-400">الإجمالي</span>
                    <span className="text-2xl font-bold text-[#f3bf54]">
                      {selectedPackageData.price} SAR
                    </span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={handlePurchase}
                className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-[#d8a43b] px-4 py-3.5 font-bold text-black transition hover:bg-[#efc05b]"
              >
                إتمام الدفع
                <ChevronLeft size={18} />
              </button>
            </aside>
          </div>
        )}

        {activeTab === "history" && (
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#09121d]">
            <div className="border-b border-white/10 px-5 py-4">
              <h2 className="font-bold text-white">سجل المعاملات</h2>
            </div>

            <div className="divide-y divide-white/5">
              {transactions.map((transaction) => {
                const positive = transaction.coins > 0;

                return (
                  <div
                    key={transaction.id}
                    className="flex flex-col gap-4 px-5 py-4 transition hover:bg-white/[0.02] md:flex-row md:items-center md:justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-11 w-11 items-center justify-center rounded-xl ${
                          transaction.type === "reward"
                            ? "bg-violet-500/10 text-violet-300"
                            : transaction.type === "spend"
                            ? "bg-red-500/10 text-red-300"
                            : "bg-[#d8a43b]/10 text-[#f3bf54]"
                        }`}
                      >
                        {transaction.type === "reward" ? (
                          <Gift size={20} />
                        ) : transaction.type === "spend" ? (
                          <ArrowDownRight size={20} />
                        ) : (
                          <ArrowUpRight size={20} />
                        )}
                      </div>

                      <div>
                        <h3 className="text-sm font-medium text-white">
                          {transaction.title}
                        </h3>
                        <p className="mt-1 text-xs text-slate-500">
                          {transaction.id} · {transaction.date}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 md:justify-end">
                      <div className="text-left">
                        <div
                          className={`text-sm font-bold ${
                            positive ? "text-emerald-300" : "text-red-300"
                          }`}
                        >
                          {transaction.coins > 0 ? "+" : ""}
                          {formatNumber(transaction.coins)} عملة
                        </div>

                        {transaction.amount > 0 && (
                          <div className="mt-1 text-xs text-slate-500">
                            {transaction.amount} {transaction.currency}
                          </div>
                        )}
                      </div>

                      <StatusBadge status={transaction.status} />
                    </div>
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
