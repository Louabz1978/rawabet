import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { api, clearToken, setToken } from "./lib/api.js";
import "./styles.css";

const text = {
  en: {
    brand: "Rawabet",
    sub: "Professional Network",
    email: "Email",
    password: "Password",
    login: "Sign in",
    register: "Register",
    createAccount: "Create account",
    verifyEmail: "Verify email",
    verificationCode: "Verification code",
    haveAccount: "Already have an account?",
    needAccount: "Create a new account",
    checkEmail: "Check your email for the verification code.",
    logout: "Logout",
    demoAdmin: "Admin demo",
    demoUser: "User demo",
    home: "Home",
    profile: "Profile",
    jobs: "Jobs",
    admin: "Admin",
    search: "Search job, company, or job number",
    completeProfile: "Complete profile",
    editProfileAction: "Edit profile",
    workspace: "Workspace",
    profileViews: "Jobs applied",
    profileStrength: "Profile strength",
    strengthGreat: "All-Star profile. You look ready for recruiters.",
    strengthGood: "Strong profile. Add certificates for more credibility.",
    strengthNeedsWork: "Add your photo, resume, certificates, skills, and work history to strengthen your profile.",
    publicProfile: "Public profile",
    savedJobs: "Saved jobs",
    resumeUpload: "Resume upload",
    resumeUploadBody: "PDF, DOC, and portfolio files",
    verifiedCerts: "Certificates",
    verifiedCertsBody: "Show licenses, awards, and training",
    workTimeline: "Work history",
    workTimelineBody: "Structured career timeline",
    startPost: "Start a professional update",
    article: "Article",
    portfolio: "Portfolio",
    event: "Event",
    welcomeTitle: "Welcome to Rawabet",
    welcome: "Build your verified professional identity",
    welcomeBody: "Rawabet helps professionals create bilingual profiles, upload resumes and certificates, apply to jobs, and connect with opportunity.",
    editProfile: "Save profile",
    fullName: "Full name",
    phone: "Phone number",
    dob: "Date of birth",
    headline: "Headline",
    location: "Location",
    about: "About",
    skills: "Skills",
    resume: "Resume",
    certificate: "Certificate",
    upload: "Upload",
    profilePicture: "Profile picture",
    changePhoto: "Change photo",
    attachments: "Attachments",
    noAttachments: "No attachments yet",
    viewFile: "View file",
    removeAttachment: "Remove",
    maxCertificates: "Up to 5 certificates",
    profileBuilder: "Profile Builder",
    completeYourRawabet: "Complete your Rawabet profile",
    basicInfo: "Basic information",
    mediaFiles: "Photo, resume, certificates",
    careerHistory: "Career history",
    cancel: "Cancel",
    filesStayLocal: "Files are stored in Rawabet",
    filesStayLocalBody: "Uploads are sent to the Python backend and saved for this profile.",
    experience: "Experience",
    addExperience: "Add experience",
    title: "Title",
    company: "Company",
    type: "Type",
    activeJobs: "Active jobs",
    appliedJobs: "Applied jobs",
    whereIApplied: "Where I applied for",
    noAppliedJobs: "No applications yet",
    appliedOnly: "Applied jobs only",
    allJobs: "All jobs",
    companySearch: "Company search",
    allStatuses: "All statuses",
    more: "More",
    upcomingInterviews: "Upcoming interviews",
    clearChat: "Clear chat",
    adminPosts: "Recent Added Jobs",
    noAdminPosts: "No admin posts yet",
    apply: "Apply",
    adminDashboard: "Admin dashboard",
    totalUsers: "Total users",
    verifiedProfiles: "Verified profiles",
    applications: "Applications",
    agent: "Agent",
    agentWorkspace: "Agent workspace",
    sharedProfiles: "Shared profiles",
    shareWithAgent: "Share with agent",
    noSharedProfiles: "No shared profiles yet",
    sharedForJob: "Shared for job",
    applicationStatus: "Application status",
    applicant: "Applicant",
    job: "Job",
    jobId: "Job ID",
    jobDetails: "Job details",
    category: "Category",
    allCategories: "All categories",
    salaryRange: "Salary range",
    allSalaries: "All salaries",
    salary150to300: "$150 - $300",
    salary300to500: "$300 - $500",
    salary500to800: "$500 - $800",
    salary800to1200: "$800 - $1,200",
    salary1200Plus: "$1,200+",
    previous: "Previous",
    next: "Next",
    page: "Page",
    noJobsMatching: "No jobs match this filter",
    monthlyRevenue: "Monthly revenue",
    users: "Users",
    searchUsers: "Search users",
    searchJobs: "Search by job ID, title, or company",
    reports: "Reports",
    growthAnalytics: "Growth analytics",
    usersGrowth: "Users growth",
    jobsPosted: "Jobs posted",
    monthlyApplications: "Monthly applications",
    applicationOutcomes: "Applied vs rejected vs approved",
    jobCategories: "Jobs by category",
    profileHealth: "Profile health",
    suspendedUsers: "Suspended users",
    pendingInterviews: "Scheduled interviews",
    overview: "Overview",
    userManagement: "User management",
    jobManagement: "Job management",
    applicationManagement: "Applications",
    interviews: "Interviews",
    supportInbox: "Support inbox",
    unreadMessages: "Unread messages",
    openChat: "Open chat",
    latestMessage: "Latest message",
    riskQueue: "Risk queue",
    pendingDocs: "Pending document reviews",
    view: "View",
    chooseAction: "Choose action",
    backToUsers: "Back to users",
    profileDetails: "Profile details",
    suspend: "Suspend",
    restore: "Restore",
    status: "Status",
    role: "Role",
    plan: "Plan",
    lastActive: "Last active",
    actions: "Actions",
    save: "Save",
    support: "Support",
    supportMessage: "Write a support message",
    send: "Send",
    clearingChat: "Clearing...",
    speakLive: "Speak with live support",
    endConversation: "End conversation",
    liveAgentRequest: "I want to speak with live support.",
    clearFailed: "Could not clear the conversation.",
    editUser: "Edit user",
    delete: "Delete",
    verify: "Verify",
    activate: "Activate",
    deactivate: "Deactivate",
    addJob: "Add job",
    editJob: "Edit job",
    deleteJob: "Delete job",
    salary: "Salary",
    description: "Description",
    screeningQuestions: "Application questions",
    screeningQuestionsHelp: "One question per line",
    answerQuestions: "Answer application questions",
    answerRequired: "Please answer all questions before applying.",
    submittedAnswers: "Submitted answers",
    noQuestions: "No questions",
    scheduleInterview: "Schedule interview",
    interviewEmailSent: "Interview email sent to",
    interviewEmailFailed: "Interview was scheduled, but email failed",
    recipientEmail: "Recipient email",
    interviewTime: "Interview time",
    upcomingAdminInterviews: "Upcoming interviews",
    interviewOutcome: "Interview outcome",
    channel: "Channel",
    notes: "Notes",
    language: "ع"
  },
  ar: {
    brand: "روابط",
    sub: "شبكة مهنية",
    email: "البريد الإلكتروني",
    password: "كلمة المرور",
    login: "تسجيل الدخول",
    register: "تسجيل",
    createAccount: "إنشاء حساب",
    verifyEmail: "تأكيد البريد",
    verificationCode: "رمز التحقق",
    haveAccount: "لديك حساب؟",
    needAccount: "إنشاء حساب جديد",
    checkEmail: "تحقق من بريدك للحصول على رمز التحقق.",
    logout: "خروج",
    demoAdmin: "تجربة المدير",
    demoUser: "تجربة المستخدم",
    home: "الرئيسية",
    profile: "الملف",
    jobs: "الوظائف",
    admin: "الإدارة",
    search: "ابحث عن الوظيفة أو الشركة أو رقم الوظيفة",
    completeProfile: "أكمل الملف",
    editProfileAction: "تعديل الملف",
    workspace: "مساحة العمل",
    profileViews: "عدد الوظائف المقدمة",
    profileStrength: "قوة الملف",
    strengthGreat: "ملف ممتاز. أنت جاهز للظهور أمام مسؤولي التوظيف.",
    strengthGood: "ملف قوي. أضف الشهادات لزيادة الموثوقية.",
    strengthNeedsWork: "أضف الصورة والسيرة الذاتية والشهادات والمهارات وتاريخ العمل لتقوية ملفك.",
    publicProfile: "الملف العام",
    savedJobs: "الوظائف المحفوظة",
    resumeUpload: "رفع السيرة الذاتية",
    resumeUploadBody: "ملفات PDF و DOC وملفات الأعمال",
    verifiedCerts: "الشهادات",
    verifiedCertsBody: "اعرض الرخص والجوائز والتدريب",
    workTimeline: "تاريخ العمل",
    workTimelineBody: "مسار مهني منظم",
    startPost: "ابدأ تحديثا مهنيا",
    article: "مقال",
    portfolio: "أعمال",
    event: "فعالية",
    welcomeTitle: "مرحبا بك في روابط",
    welcome: "ابن هويتك المهنية الموثقة",
    welcomeBody: "روابط تساعد المهنيين على إنشاء ملفات ثنائية اللغة ورفع السير الذاتية والشهادات والتقديم للوظائف والتواصل مع الفرص.",
    editProfile: "حفظ الملف",
    fullName: "الاسم الكامل",
    phone: "رقم الهاتف",
    dob: "تاريخ الميلاد",
    headline: "العنوان المهني",
    location: "الموقع",
    about: "نبذة",
    skills: "المهارات",
    resume: "السيرة الذاتية",
    certificate: "الشهادة",
    upload: "رفع",
    profilePicture: "الصورة الشخصية",
    changePhoto: "تغيير الصورة",
    attachments: "المرفقات",
    noAttachments: "لا توجد مرفقات بعد",
    viewFile: "عرض الملف",
    removeAttachment: "حذف",
    maxCertificates: "حتى 5 شهادات",
    profileBuilder: "منشئ الملف",
    completeYourRawabet: "أكمل ملفك في روابط",
    basicInfo: "المعلومات الأساسية",
    mediaFiles: "الصورة والسيرة والشهادات",
    careerHistory: "التاريخ المهني",
    cancel: "إلغاء",
    filesStayLocal: "يتم حفظ الملفات في روابط",
    filesStayLocalBody: "يتم إرسال الملفات إلى باكند بايثون وحفظها لهذا الملف.",
    experience: "الخبرات",
    addExperience: "إضافة خبرة",
    title: "المسمى",
    company: "الشركة",
    type: "النوع",
    activeJobs: "الوظائف النشطة",
    appliedJobs: "الوظائف المقدمة",
    whereIApplied: "الوظائف التي تقدمت إليها",
    noAppliedJobs: "لا توجد طلبات بعد",
    appliedOnly: "الوظائف المقدمة فقط",
    allJobs: "كل الوظائف",
    companySearch: "البحث باسم الشركة",
    allStatuses: "كل الحالات",
    more: "المزيد",
    upcomingInterviews: "المقابلات القادمة",
    clearChat: "مسح المحادثة",
    adminPosts: "أحدث الوظائف المضافة",
    noAdminPosts: "لا توجد منشورات من الإدارة بعد",
    apply: "تقديم",
    adminDashboard: "لوحة تحكم الإدارة",
    totalUsers: "إجمالي المستخدمين",
    verifiedProfiles: "الملفات الموثقة",
    applications: "طلبات التقديم",
    agent: "وكيل",
    agentWorkspace: "مساحة الوكيل",
    sharedProfiles: "الملفات المشاركة",
    shareWithAgent: "مشاركة مع وكيل",
    noSharedProfiles: "لا توجد ملفات مشاركة بعد",
    sharedForJob: "مشارك لوظيفة",
    applicationStatus: "حالة الطلب",
    applicant: "المتقدم",
    job: "الوظيفة",
    jobId: "رقم الوظيفة",
    jobDetails: "تفاصيل الوظيفة",
    category: "الفئة",
    allCategories: "كل الفئات",
    salaryRange: "نطاق الراتب",
    allSalaries: "كل الرواتب",
    salary150to300: "$150 - $300",
    salary300to500: "$300 - $500",
    salary500to800: "$500 - $800",
    salary800to1200: "$800 - $1,200",
    salary1200Plus: "$1,200+",
    previous: "السابق",
    next: "التالي",
    page: "الصفحة",
    noJobsMatching: "لا توجد وظائف مطابقة لهذا الفلتر",
    monthlyRevenue: "الإيراد الشهري",
    users: "المستخدمون",
    searchUsers: "ابحث عن مستخدمين",
    searchJobs: "ابحث برقم الوظيفة أو المسمى أو الشركة",
    reports: "التقارير",
    growthAnalytics: "تحليلات النمو",
    usersGrowth: "نمو المستخدمين",
    jobsPosted: "الوظائف المنشورة",
    monthlyApplications: "التقديمات الشهرية",
    applicationOutcomes: "التقديمات مقابل المرفوض والمقبول",
    jobCategories: "الوظائف حسب الفئة",
    profileHealth: "جودة الملفات",
    suspendedUsers: "الحسابات الموقوفة",
    pendingInterviews: "المقابلات المجدولة",
    overview: "نظرة عامة",
    userManagement: "إدارة المستخدمين",
    jobManagement: "إدارة الوظائف",
    applicationManagement: "طلبات التقديم",
    interviews: "المقابلات",
    supportInbox: "صندوق الدعم",
    unreadMessages: "رسائل غير مقروءة",
    openChat: "فتح المحادثة",
    latestMessage: "آخر رسالة",
    riskQueue: "قائمة المخاطر",
    pendingDocs: "مراجعات مستندات معلقة",
    view: "عرض",
    chooseAction: "اختر إجراء",
    backToUsers: "العودة للمستخدمين",
    profileDetails: "تفاصيل الملف",
    suspend: "إيقاف",
    restore: "استعادة",
    status: "الحالة",
    role: "الدور",
    plan: "الخطة",
    lastActive: "آخر نشاط",
    actions: "الإجراءات",
    save: "حفظ",
    support: "الدعم",
    supportMessage: "اكتب رسالة للدعم",
    send: "إرسال",
    clearingChat: "جار المسح...",
    speakLive: "التحدث مع دعم مباشر",
    endConversation: "إنهاء المحادثة",
    liveAgentRequest: "أريد التحدث مع موظف دعم مباشر.",
    clearFailed: "تعذر مسح المحادثة.",
    editUser: "تعديل المستخدم",
    delete: "حذف",
    verify: "توثيق",
    activate: "تفعيل",
    deactivate: "إيقاف",
    addJob: "إضافة وظيفة",
    editJob: "تعديل الوظيفة",
    deleteJob: "حذف الوظيفة",
    salary: "الراتب",
    description: "الوصف",
    screeningQuestions: "أسئلة التقديم",
    screeningQuestionsHelp: "سؤال واحد في كل سطر",
    answerQuestions: "أجب عن أسئلة التقديم",
    answerRequired: "يرجى الإجابة عن جميع الأسئلة قبل التقديم.",
    submittedAnswers: "إجابات المتقدم",
    noQuestions: "لا توجد أسئلة",
    scheduleInterview: "جدولة مقابلة",
    interviewEmailSent: "تم إرسال بريد المقابلة إلى",
    interviewEmailFailed: "تمت جدولة المقابلة، لكن فشل إرسال البريد",
    recipientEmail: "بريد المستلم",
    interviewTime: "وقت المقابلة",
    upcomingAdminInterviews: "المقابلات القادمة",
    interviewOutcome: "نتيجة المقابلة",
    channel: "القناة",
    notes: "ملاحظات",
    language: "EN"
  }
};

const JOB_CATEGORIES = [
  { value: "General", en: "General", ar: "عام" },
  { value: "Technology", en: "Technology", ar: "التقنية" },
  { value: "Engineering", en: "Engineering", ar: "الهندسة" },
  { value: "Data", en: "Data", ar: "البيانات" },
  { value: "Design", en: "Design", ar: "التصميم" },
  { value: "Product", en: "Product", ar: "المنتج" },
  { value: "Sales", en: "Sales", ar: "المبيعات" },
  { value: "Marketing", en: "Marketing", ar: "التسويق" },
  { value: "HR", en: "HR", ar: "الموارد البشرية" },
  { value: "Finance", en: "Finance", ar: "المالية" },
  { value: "Operations", en: "Operations", ar: "العمليات" },
  { value: "Healthcare", en: "Healthcare", ar: "الرعاية الصحية" },
  { value: "Education", en: "Education", ar: "التعليم" }
];

function jobCategoryLabel(value, lang) {
  const match = JOB_CATEGORIES.find((category) => category.value === value);
  return match ? match[lang] : value || JOB_CATEGORIES[0][lang];
}

const STATUS_LABELS = {
  submitted: { en: "Submitted", ar: "تم التقديم" },
  review: { en: "In review", ar: "قيد المراجعة" },
  interview: { en: "Interview", ar: "مقابلة" },
  accepted: { en: "Accepted", ar: "مقبول" },
  rejected: { en: "Rejected", ar: "مرفوض" },
  active: { en: "Active", ar: "نشط" },
  verified: { en: "Verified", ar: "موثق" },
  suspended: { en: "Suspended", ar: "موقوف" },
  paused: { en: "Paused", ar: "متوقف" },
  closed: { en: "Closed", ar: "مغلق" }
};

const APPLICATION_STATUSES = ["submitted", "review", "interview", "accepted", "rejected"];
const INTERVIEW_OUTCOME_STATUSES = ["accepted", "rejected"];
const USER_STATUSES = ["active", "verified", "review", "suspended"];
const JOB_STATUSES = ["active", "paused", "closed"];
const PLAN_OPTIONS = ["free", "premium"];
const USER_ROLES = ["member", "recruiter", "company", "agent", "admin"];

function statusLabel(value, lang) {
  return STATUS_LABELS[value]?.[lang] || value || "-";
}

function normalizeStatusValue(value) {
  if (!value) return "";
  const normalized = String(value).trim().toLowerCase();
  const match = Object.entries(STATUS_LABELS).find(([key, labels]) => {
    return normalized === key || normalized === labels.en.toLowerCase() || normalized === labels.ar;
  });
  return match ? match[0] : normalized;
}

function planLabel(value, lang) {
  const labels = {
    free: { en: "Free", ar: "مجاني" },
    premium: { en: "Premium", ar: "مميز" }
  };
  return labels[value]?.[lang] || value || "-";
}

function questionsFromText(value = "") {
  return String(value).split("\n").map((item) => item.trim()).filter(Boolean);
}

function questionsToText(value = []) {
  return Array.isArray(value) ? value.join("\n") : "";
}

function salaryBounds(salary = "") {
  const values = String(salary).match(/\$?\s*[\d,]+/g)?.map((item) => Number(item.replace(/[^\d]/g, ""))).filter(Boolean) || [];
  if (!values.length) return { min: 0, max: 0 };
  return { min: Math.min(...values), max: Math.max(...values) };
}

function matchesSalaryRange(job, range) {
  if (!range) return true;
  const { min, max } = salaryBounds(job.salary_range);
  if (!max) return false;
  if (range === "150-300") return max >= 150 && min <= 300;
  if (range === "300-500") return max >= 300 && min <= 500;
  if (range === "500-800") return max >= 500 && min <= 800;
  if (range === "800-1200") return max >= 800 && min <= 1200;
  if (range === "1200-plus") return max >= 1200;
  return true;
}

function App() {
  const [lang, setLang] = useState(localStorage.getItem("rawabet_lang") || "en");
  const [view, setView] = useState("home");
  const [session, setSession] = useState(null);
  const [me, setMe] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [admin, setAdmin] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminApplications, setAdminApplications] = useState([]);
  const [adminInterviews, setAdminInterviews] = useState([]);
  const [agentShares, setAgentShares] = useState([]);
  const [supportThreads, setSupportThreads] = useState([]);
  const [supportTarget, setSupportTarget] = useState("");
  const [adminStartTab, setAdminStartTab] = useState("");
  const [jobSearch, setJobSearch] = useState("");
  const [selectedJobId, setSelectedJobId] = useState("");
  const [jobMode, setJobMode] = useState("all");
  const [error, setError] = useState("");
  const [builderOpen, setBuilderOpen] = useState(false);
  const [supportOpen, setSupportOpen] = useState(false);
  const t = (key) => text[lang][key] || key;

  useEffect(() => {
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = lang;
    localStorage.setItem("rawabet_lang", lang);
  }, [lang]);

  async function loadApp() {
    const data = await api("/account");
    setMe(data);
    setSession(data.user);
    if (data.user.role === "admin") {
      try {
        setJobs(await api("/admin/jobs"));
      } catch {
        setJobs(await api("/jobs"));
      }
    } else {
      setJobs(await api("/jobs"));
    }
    if (data.user.role === "admin") {
      setAdmin(await api("/admin/overview"));
      setAdminUsers(await api("/admin/users"));
      setAdminApplications(await api("/admin/applications"));
      setAdminInterviews(await api("/admin/interviews"));
      setSupportThreads(await api("/admin/support/threads"));
    }
    if (data.user.role === "agent") {
      setAgentShares(await api("/agent/shares"));
    }
  }

  async function loadSupportThreads() {
    if (session?.role === "admin") {
      setSupportThreads(await api("/admin/support/threads"));
    }
  }

  useEffect(() => {
    if (localStorage.getItem("rawabet_token")) {
      loadApp().catch(() => clearToken());
    }
  }, []);

  useEffect(() => {
    if (session?.role !== "admin") return undefined;
    const timer = setInterval(() => loadSupportThreads().catch(() => {}), 12000);
    return () => clearInterval(timer);
  }, [session?.role]);

  async function login(email, password) {
    setError("");
    try {
      const data = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      setToken(data.token);
      try {
        await loadApp();
        setView("home");
      } catch (loadError) {
        clearToken();
        setSession(null);
        setMe(null);
        throw loadError;
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function verifyAndLoad(token) {
    setToken(token);
    try {
      await loadApp();
      setView("home");
    } catch (err) {
      clearToken();
      setSession(null);
      setMe(null);
      throw err;
    }
  }

  function logout() {
    clearToken();
    setSession(null);
    setMe(null);
    setAdmin(null);
    setAdminApplications([]);
    setSupportThreads([]);
  }

  const supportUnread = supportThreads.filter((thread) => Number(thread.unread_count || 0) > 0).length;

  function openJob(jobId) {
    setJobMode("all");
    setSelectedJobId(jobId);
    setJobSearch("");
    setView("jobs");
  }

  function openAppliedJobs() {
    setJobMode("applied");
    setSelectedJobId("");
    setJobSearch("");
    setView("jobs");
  }

  if (!session || !me) return <Login lang={lang} setLang={setLang} t={t} login={login} verifyAndLoad={verifyAndLoad} error={error} setError={setError} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => setView("home")}>
          <img className="brand-mark" src="/brand/rawabet-mark.png" alt="" />
          <img className="brand-wordmark" src="/brand/rawabet-wordmark.png" alt="Rawabet - روابط تجمعنا" />
        </button>
        <label className="search">
          <span>⌕</span>
          <input placeholder={t("search")} value={jobSearch} onChange={(event) => { setJobMode("all"); setJobSearch(event.target.value); setView("jobs"); }} />
        </label>
        <nav className="desktop-nav">
          {[
            ["home", "⌂"],
            ["profile", "◉"],
            ["jobs", "▣"]
          ].map(([item, icon]) => <button className={`nav-link ${view === item ? "active" : ""}`} onClick={() => setView(item)} key={item}><span>{icon}</span><b>{t(item)}</b></button>)}
          {session.role === "admin" && <button className={`nav-link ${view === "admin" ? "active" : ""}`} onClick={() => setView("admin")}><span>▥</span><b>{t("admin")}</b></button>}
          {session.role === "agent" && <button className={`nav-link ${view === "agent" ? "active" : ""}`} onClick={() => setView("agent")}><span>◈</span><b>{t("agent")}</b></button>}
        </nav>
        <div className="top-actions">
          <button className="icon-button" onClick={() => setLang(lang === "en" ? "ar" : "en")}>{t("language")}</button>
          <button className="secondary-button compact notify-button" onClick={() => session.role === "admin" ? (setAdminStartTab("support"), setView("admin")) : setSupportOpen(true)}>{t("support")}{supportUnread > 0 && <span>{supportUnread}</span>}</button>
          <button className="primary-button compact" onClick={() => setBuilderOpen(true)}>{t("completeProfile")}</button>
          <button className="secondary-button compact" onClick={logout}>{t("logout")}</button>
        </div>
      </header>

      <main className={view === "admin" ? "admin-main" : ""}>
        {view === "home" && <Home t={t} lang={lang} me={me} jobs={jobs} setView={setView} openJob={openJob} openAppliedJobs={openAppliedJobs} openBuilder={() => setBuilderOpen(true)} />}
        {view === "profile" && <Profile t={t} me={me} reload={loadApp} />}
        {view === "jobs" && <Jobs t={t} lang={lang} jobs={jobs} applications={me.applications || []} interviews={me.interviews || []} search={jobSearch} mode={jobMode} setMode={setJobMode} selectedJobId={selectedJobId} clearSelectedJob={() => setSelectedJobId("")} reload={loadApp} />}
        {view === "admin" && session.role === "admin" && <Admin t={t} lang={lang} admin={admin} users={adminUsers} setUsers={setAdminUsers} jobs={jobs} applications={adminApplications} setApplications={setAdminApplications} interviews={adminInterviews} supportThreads={supportThreads} initialTab={adminStartTab} clearInitialTab={() => setAdminStartTab("")} reload={loadApp} openSupport={(userId) => { setSupportTarget(userId || ""); setSupportOpen(true); }} />}
        {view === "agent" && session.role === "agent" && <AgentWorkspace t={t} lang={lang} shares={agentShares} />}
      </main>
      {builderOpen && <ProfileBuilder t={t} me={me} reload={loadApp} close={() => setBuilderOpen(false)} />}
      {supportOpen && <SupportWindow t={t} me={me} users={adminUsers} initialUserId={supportTarget} onUpdate={loadSupportThreads} close={() => { setSupportOpen(false); setSupportTarget(""); }} />}
    </div>
  );
}

function Login({ lang, setLang, t, login, verifyAndLoad, error, setError }) {
  const [mode, setMode] = useState("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [dob, setDob] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [notice, setNotice] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setEmail("");
      setPassword("");
    }, 120);
    return () => clearTimeout(timer);
  }, []);

  async function submitLogin(event) {
    event.preventDefault();
    setError("");
    setLoggingIn(true);
    try {
      await login(email, password);
    } finally {
      setLoggingIn(false);
    }
  }

  async function register(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setRegistering(true);
    try {
      const data = await api("/auth/register", { method: "POST", body: JSON.stringify({ fullName, email, phone, dob, password }) });
      setNotice(data.devOtp ? `${data.message} OTP: ${data.devOtp}` : data.message || t("checkEmail"));
      setMode("verify");
    } catch (err) {
      setError(err.message);
    } finally {
      setRegistering(false);
    }
  }

  async function verify(event) {
    event.preventDefault();
    setError("");
    setVerifying(true);
    try {
      const data = await api("/auth/verify-registration", { method: "POST", body: JSON.stringify({ email, otp }) });
      await verifyAndLoad(data.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setVerifying(false);
    }
  }

  return (
    <main className={`login-page ${lang === "ar" ? "login-page-rtl" : ""}`}>
      <header className="login-top">
        <img className="login-top-logo" src="/brand/rawabet-wordmark.png" alt="Rawabet - روابط تجمعنا" />
        <button type="button" className="icon-button" onClick={() => setLang(lang === "en" ? "ar" : "en")}>{t("language")}</button>
      </header>
      <section className="login-stage">
        <div className="login-copy">
          <h1>{t("welcome")}</h1>
          {mode === "login" && <form className="login-card" onSubmit={submitLogin} autoComplete="off">
            <label>{t("email")}<input name="rawabet-login-email" autoComplete="new-password" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>{t("password")}<input name="rawabet-login-password" autoComplete="new-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={loggingIn}>{loggingIn && <span className="spinner" aria-hidden="true"></span>}{t("login")}</button>
            <button className="auth-switch" type="button" onClick={() => { setMode("register"); setError(""); }}>{t("needAccount")}</button>
          </form>}

          {mode === "register" && <form className="login-card" onSubmit={register}>
            <label>{t("fullName")}<input value={fullName} onChange={(event) => setFullName(event.target.value)} required /></label>
            <label>{t("email")}<input value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>{t("phone")}<input value={phone} onChange={(event) => setPhone(event.target.value)} required /></label>
            <label>{t("dob")}<input type="date" value={dob} onChange={(event) => setDob(event.target.value)} required /></label>
            <label>{t("password")}<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={registering}>{registering && <span className="spinner" aria-hidden="true"></span>}{t("createAccount")}</button>
            <button className="auth-switch" type="button" disabled={registering} onClick={() => { setMode("login"); setError(""); }}>{t("haveAccount")} {t("login")}</button>
          </form>}

          {mode === "verify" && <form className="login-card" onSubmit={verify}>
            <label>{t("email")}<input value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>{t("verificationCode")}<input value={otp} onChange={(event) => setOtp(event.target.value)} required /></label>
            {notice && <p className="notice">{notice}</p>}
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={verifying}>{verifying && <span className="spinner" aria-hidden="true"></span>}{t("verifyEmail")}</button>
            <button className="auth-switch" type="button" disabled={verifying} onClick={() => { setMode("login"); setError(""); }}>{t("haveAccount")} {t("login")}</button>
          </form>}
        </div>
        <div className="login-visual">
          <img src="/brand/login-hero.svg" alt="" />
        </div>
      </section>
    </main>
  );
}

function Home({ t, lang, me, jobs, setView, openJob, openAppliedJobs, openBuilder }) {
  const strength = Number(me.profile?.profile_strength ?? 0);
  const applications = me.applications || [];
  const priorityApplications = applications.filter((item) => ["interview", "review"].includes(normalizeStatusValue(item.status)));
  const skills = Array.isArray(me.profile?.skills) ? me.profile.skills.filter(Boolean) : [];
  const experiences = me.experiences || [];
  const interviews = me.interviews || [];
  const scheduledJobIds = new Set(interviews.map((item) => item.job_id).filter(Boolean));
  const orderedJobs = [...jobs].sort((a, b) => Number(scheduledJobIds.has(b.id)) - Number(scheduledJobIds.has(a.id))).slice(0, 20);
  return (
    <div className="layout-grid">
      <aside className="profile-rail">
        <section className="profile-card">
          <div className="cover-strip" />
          <div className="avatar-wrap"><Avatar user={me.user} /><span className="online-dot" /></div>
          <h2>{me.user.fullName}</h2>
          <p>{me.user.headline}</p>
          <button className="secondary-button" onClick={openBuilder}>{t("editProfileAction")}</button>
        </section>
        {!!interviews.length && <section className="panel side-panel interview-panel">
          <h2>{t("upcomingInterviews")}</h2>
          {interviews.slice(0, 3).map((interview) => <button className="panel-link interview-link" type="button" onClick={() => setView("jobs")} key={interview.id}><span>◌</span><div><strong>{interview.job_title || t("job")}</strong><small>{new Date(interview.scheduled_at).toLocaleString()}</small></div></button>)}
        </section>}
        <section className="panel side-panel workspace-panel">
          <h2>{t("workspace")}</h2>
          <button className="panel-link" onClick={() => setView("profile")}><span>↗</span>{t("publicProfile")}</button>
          <button className="panel-link" onClick={() => setView("jobs")}><span>▦</span>{t("savedJobs")}</button>
          {me.user.role === "admin" && <button className="panel-link" onClick={() => setView("admin")}><span>▥</span>{t("adminDashboard")}</button>}
        </section>
      </aside>
      <section className="feed">
        <article className="panel post-card">
          <div className="post-head"><div className="company-logo">R</div><div><h2>{t("adminPosts")}</h2><p>{t("jobs")}</p></div></div>
          <div className="admin-post-list">
            {orderedJobs.length ? orderedJobs.map((job) => (
              <article className={scheduledJobIds.has(job.id) ? "admin-post highlighted-job" : "admin-post"} key={job.id}>
                <strong>{job.title}</strong>
                <span>{job.salary_range || "-"} · {job.company_name}</span>
                <button className="secondary-button compact" type="button" onClick={() => openJob(job.id)}>{t("more")}</button>
              </article>
            )) : <p>{t("noAdminPosts")}</p>}
          </div>
        </article>
      </section>
      <aside className="insight-rail">
        <section className="panel side-panel strength-panel">
          <h2>{t("profileStrength")}</h2>
          <div className="meter"><span style={{ width: `${strength}%` }} /></div>
          <p>{strength >= 85 ? t("strengthGreat") : strength >= 55 ? t("strengthGood") : t("strengthNeedsWork")}</p>
        </section>
        <section className="panel side-panel">
          <h2>{t("profileViews")}</h2>
          <strong className="side-stat">{formatNumber(applications.length)}</strong>
          <div className="job-strip side-job-strip">{priorityApplications.length ? priorityApplications.map((item) => <span className="application-chip" key={item.id}>{item.title}<b className={`status ${normalizeStatusValue(item.status)}`}>{statusLabel(normalizeStatusValue(item.status), lang)}</b></span>) : <span>{t("noAppliedJobs")}</span>}</div>
          {!!applications.length && <button className="panel-link more-link" type="button" onClick={openAppliedJobs}><span>↗</span>{t("more")}</button>}
        </section>
        <section className="panel side-panel">
          <h2>{t("skills")}</h2>
          <div className="profile-summary-list skill-summary">
            {skills.length ? skills.map((skill) => <span key={skill}>{skill}</span>) : <button className="panel-link" type="button" onClick={openBuilder}>{t("completeProfile")}</button>}
          </div>
          <div className="summary-divider" />
          <h2>{t("workTimeline")}</h2>
          <div className="profile-summary-list experience-summary">
            {experiences.length ? experiences.map((item) => <article key={item.id}><strong>{item.title}</strong><span>{item.company}</span></article>) : <button className="panel-link" type="button" onClick={openBuilder}>{t("addExperience")}</button>}
          </div>
        </section>
      </aside>
    </div>
  );
}

function ProfileBuilder({ t, me, reload, close }) {
  const [form, setForm] = useState({
    fullName: me.user.fullName || "",
    phone: me.user.phone || "",
    dob: me.user.dob || "",
    headline: me.user.headline || "",
    location: me.user.location || "",
    about: me.profile?.about || "",
    skills: (me.profile?.skills || []).join(", ")
  });
  const [experience, setExperience] = useState({ title: "", company: "" });
  const [saving, setSaving] = useState(false);

  async function saveProfile(event) {
    event.preventDefault();
    setSaving(true);
    await api("/account/profile", {
      method: "PUT",
      body: JSON.stringify({
        ...form,
        skills: form.skills.split(",").map((item) => item.trim()).filter(Boolean)
      })
    });
    await reload();
    setSaving(false);
    close();
  }

  async function upload(kind, file) {
    if (!file) return;
    const body = new FormData();
    body.append("kind", kind);
    body.append("file", file);
    try {
      await api("/account/documents", { method: "POST", body });
      await reload();
    } catch (err) {
      alert(err.message);
    }
  }

  async function uploadAvatar(file) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    await api("/account/avatar", { method: "POST", body });
    await reload();
  }

  async function addExperience() {
    if (!experience.title || !experience.company) return;
    await api("/account/experience", { method: "POST", body: JSON.stringify(experience) });
    setExperience({ title: "", company: "" });
    await reload();
  }

  return (
    <div className="builder-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && close()}>
      <section className="builder-modal" role="dialog" aria-modal="true" aria-labelledby="profileBuilderTitle">
        <header className="builder-head">
          <div>
            <p>{t("profileBuilder")}</p>
            <h2 id="profileBuilderTitle">{t("completeYourRawabet")}</h2>
          </div>
          <button className="icon-button" type="button" onClick={close} aria-label="Close">×</button>
        </header>

        <div className="builder-grid">
          <form className="builder-panel" onSubmit={saveProfile}>
            <h3>{t("basicInfo")}</h3>
            <label>{t("fullName")}<input value={form.fullName} onChange={(e) => setForm({ ...form, fullName: e.target.value })} /></label>
            <label>{t("phone")}<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <label>{t("dob")}<input type="date" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} /></label>
            <label>{t("headline")}<input value={form.headline} onChange={(e) => setForm({ ...form, headline: e.target.value })} /></label>
            <label>{t("location")}<input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></label>
            <label>{t("about")}<textarea value={form.about} onChange={(e) => setForm({ ...form, about: e.target.value })} /></label>
            <label>{t("skills")}<input value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} /></label>
            <button className="primary-button" disabled={saving}>{saving ? t("save") : t("editProfile")}</button>
          </form>

          <section className="builder-panel">
            <h3>{t("mediaFiles")}</h3>
            <label>{t("profilePicture")}<input type="file" accept="image/*" onChange={(e) => uploadAvatar(e.target.files[0])} /></label>
            <label>{t("resume")}<input type="file" accept=".pdf,.doc,.docx" onChange={(e) => upload("resume", e.target.files[0])} /></label>
            <label>{t("certificate")}<input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e) => upload("certificate", e.target.files[0])} /><span>{t("maxCertificates")}</span></label>
            <div className="upload-preview">
              <Avatar user={me.user} size="large" />
              <div><strong>{t("filesStayLocal")}</strong><p>{t("filesStayLocalBody")}</p></div>
            </div>
            <DocumentLinks t={t} documents={me.documents} avatarUrl={me.user.avatarUrl} />
          </section>

          <section className="builder-panel span">
            <h3>{t("careerHistory")}</h3>
            <div className="row-fields">
              <input placeholder={t("title")} value={experience.title} onChange={(e) => setExperience({ ...experience, title: e.target.value })} />
              <input placeholder={t("company")} value={experience.company} onChange={(e) => setExperience({ ...experience, company: e.target.value })} />
              <button className="secondary-button" type="button" onClick={addExperience}>{t("addExperience")}</button>
            </div>
            <div className="timeline-list">
              {me.experiences.map((item) => <div className="timeline-item" key={item.id}><strong>{item.title}</strong><span>{item.company}</span></div>)}
            </div>
          </section>
        </div>

        <footer className="builder-actions">
          <button className="secondary-button" type="button" onClick={close}>{t("cancel")}</button>
          <button className="primary-button" type="button" onClick={saveProfile}>{t("editProfile")}</button>
        </footer>
      </section>
    </div>
  );
}

function Profile({ t, me, reload }) {
  const [form, setForm] = useState({
    fullName: me.user.fullName || "",
    phone: me.user.phone || "",
    dob: me.user.dob || "",
    headline: me.user.headline || "",
    location: me.user.location || "",
    about: me.profile?.about || "",
    skills: (me.profile?.skills || []).join(", ")
  });
  const [experience, setExperience] = useState({ title: "", company: "" });

  async function saveProfile(event) {
    event.preventDefault();
    await api("/account/profile", {
      method: "PUT",
      body: JSON.stringify({ ...form, skills: form.skills.split(",").map((item) => item.trim()).filter(Boolean) })
    });
    await reload();
  }

  async function upload(kind, file) {
    if (!file) return;
    const body = new FormData();
    body.append("kind", kind);
    body.append("file", file);
    try {
      await api("/account/documents", { method: "POST", body });
      await reload();
    } catch (err) {
      alert(err.message);
    }
  }

  async function uploadAvatar(file) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    await api("/account/avatar", { method: "POST", body });
    await reload();
  }

  async function addExperience(event) {
    event.preventDefault();
    await api("/account/experience", { method: "POST", body: JSON.stringify(experience) });
    setExperience({ title: "", company: "" });
    await reload();
  }

  return (
    <div className="profile-page">
      <section className="profile-hero panel">
        <Avatar user={me.user} size="large" />
        <div><h1>{me.user.fullName}</h1><p>{me.user.headline}</p><span>{me.user.location}</span><span>{t("dob")}: {me.user.dob || "-"}</span></div>
      </section>
      <form className="panel form-grid" onSubmit={saveProfile}>
        {["fullName", "phone", "headline", "location"].map((key) => <label key={key}>{t(key)}<input value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></label>)}
        <label>{t("dob")}<input type="date" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} /></label>
        <label className="span">{t("about")}<textarea value={form.about} onChange={(e) => setForm({ ...form, about: e.target.value })} /></label>
        <label className="span">{t("skills")}<input value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} /></label>
        <button className="primary-button">{t("editProfile")}</button>
      </form>
      <section className="panel upload-grid">
        <label>{t("profilePicture")}<input type="file" accept="image/*" onChange={(e) => uploadAvatar(e.target.files[0])} /></label>
        <label>{t("resume")}<input type="file" accept=".pdf,.doc,.docx" onChange={(e) => upload("resume", e.target.files[0])} /></label>
        <label>{t("certificate")}<input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e) => upload("certificate", e.target.files[0])} /><span>{t("maxCertificates")}</span></label>
        <div className="span"><DocumentLinks t={t} documents={me.documents} avatarUrl={me.user.avatarUrl} /></div>
      </section>
      <section className="panel">
        <h2>{t("experience")}</h2>
        <form className="row-fields" onSubmit={addExperience}>
          <input placeholder={t("title")} value={experience.title} onChange={(e) => setExperience({ ...experience, title: e.target.value })} />
          <input placeholder={t("company")} value={experience.company} onChange={(e) => setExperience({ ...experience, company: e.target.value })} />
          <button className="secondary-button">{t("addExperience")}</button>
        </form>
        {me.experiences.map((item) => <div className="timeline-item" key={item.id}><strong>{item.title}</strong><span>{item.company}</span></div>)}
      </section>
    </div>
  );
}

function Jobs({ t, lang, jobs, applications, interviews = [], search = "", mode = "all", setMode, selectedJobId = "", clearSelectedJob, reload }) {
  const [openJobId, setOpenJobId] = useState("");
  const [questionJobId, setQuestionJobId] = useState("");
  const [answerDrafts, setAnswerDrafts] = useState({});
  const [applyError, setApplyError] = useState("");
  const [category, setCategory] = useState("");
  const [salaryRange, setSalaryRange] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [companySearch, setCompanySearch] = useState("");
  const [page, setPage] = useState(1);
  const appliedByJob = new Map(applications.map((item) => [item.job_id, item]));
  const scheduledJobIds = new Set(interviews.map((item) => item.job_id).filter(Boolean));
  const normalizedSearch = search.trim().toLowerCase();
  const appliedJobs = applications.map((application) => ({
    id: application.job_id,
    title: application.title,
    company_name: application.company_name,
    category: application.category,
    location: application.location,
    type: application.type,
    salary_range: application.salary_range,
    description: application.description,
    status: application.job_status,
    job_number: application.job_number,
    screening_questions: application.screening_questions || [],
    applicationStatus: application.status,
    applicationCreatedAt: application.created_at
  }));
  const sourceJobs = mode === "applied" ? appliedJobs : jobs;
  const visibleJobs = sourceJobs.filter((job) => {
    const matchesSearch = mode === "applied"
      ? (!companySearch.trim() || `${job.company_name || ""}`.toLowerCase().includes(companySearch.trim().toLowerCase()))
      : (!normalizedSearch || `${job.job_number || ""} #${job.job_number || ""} ${job.title || ""} ${job.company_name || ""}`.toLowerCase().includes(normalizedSearch));
    const matchesCategory = !category || (job.category || "General") === category;
    const matchesSalary = matchesSalaryRange(job, salaryRange);
    const matchesStatus = mode !== "applied" || !statusFilter || job.applicationStatus === statusFilter;
    return matchesSearch && matchesCategory && matchesSalary && matchesStatus;
  }).sort((a, b) => Number(scheduledJobIds.has(b.id)) - Number(scheduledJobIds.has(a.id)));
  useEffect(() => {
    if (!selectedJobId) return;
    const index = visibleJobs.findIndex((job) => job.id === selectedJobId);
    if (index >= 0) {
      setPage(Math.max(1, Math.ceil((index + 1) / 20)));
      setOpenJobId(selectedJobId);
      setTimeout(() => document.getElementById(`job-${selectedJobId}`)?.scrollIntoView({ behavior: "smooth", block: "center" }), 80);
    }
    clearSelectedJob?.();
  }, [selectedJobId]);
  const pageSize = 20;
  const totalPages = Math.max(1, Math.ceil(visibleJobs.length / pageSize));
  const pagedJobs = visibleJobs.slice((page - 1) * pageSize, page * pageSize);
  async function apply(job) {
    const questions = job.screening_questions || [];
    const answers = questions.map((question) => ({ question, answer: (answerDrafts[job.id]?.[question] || "").trim() }));
    if (questions.length && answers.some((item) => !item.answer)) {
      setQuestionJobId(job.id);
      setOpenJobId(job.id);
      setApplyError(t("answerRequired"));
      return;
    }
    await api(`/jobs/${job.id}/apply`, { method: "POST", body: JSON.stringify({ answers }) });
    setQuestionJobId("");
    setApplyError("");
    await reload();
  }
  return <section className="job-list">
    <div className="panel job-filter-bar">
      <div className="segmented-control">
        <button type="button" className={mode === "all" ? "active" : ""} onClick={() => { setMode?.("all"); setPage(1); }}>{t("allJobs")}</button>
        <button type="button" className={mode === "applied" ? "active" : ""} onClick={() => { setMode?.("applied"); setPage(1); }}>{t("appliedOnly")}</button>
      </div>
      {mode === "applied" && <label>{t("companySearch")}
        <input value={companySearch} onChange={(event) => { setCompanySearch(event.target.value); setPage(1); }} />
      </label>}
      <label>{t("category")}
        <select value={category} onChange={(event) => { setCategory(event.target.value); setPage(1); }}>
          <option value="">{t("allCategories")}</option>
          {JOB_CATEGORIES.map((item) => <option value={item.value} key={item.value}>{item[lang]}</option>)}
        </select>
      </label>
      {mode === "applied" && <label>{t("applicationStatus")}
        <select value={statusFilter} onChange={(event) => { setStatusFilter(event.target.value); setPage(1); }}>
          <option value="">{t("allStatuses")}</option>
          {APPLICATION_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}
        </select>
      </label>}
      <label>{t("salaryRange")}
        <select value={salaryRange} onChange={(event) => { setSalaryRange(event.target.value); setPage(1); }}>
          <option value="">{t("allSalaries")}</option>
          <option value="150-300">{t("salary150to300")}</option>
          <option value="300-500">{t("salary300to500")}</option>
          <option value="500-800">{t("salary500to800")}</option>
          <option value="800-1200">{t("salary800to1200")}</option>
          <option value="1200-plus">{t("salary1200Plus")}</option>
        </select>
      </label>
    </div>
    {visibleJobs.length ? pagedJobs.map((job) => {
    const application = appliedByJob.get(job.id);
    const applicationStatus = job.applicationStatus || application?.status;
    const isOpen = openJobId === job.id;
    const isScheduled = scheduledJobIds.has(job.id);
    const questions = job.screening_questions || [];
    const showQuestions = questionJobId === job.id && questions.length > 0 && !applicationStatus;
    return <article id={`job-${job.id}`} className={isScheduled || openJobId === job.id ? "job-card panel highlighted-job" : "job-card panel"} key={job.id}>
      <div>
        <h2>{job.title}</h2>
        <small className="job-public-id">{t("jobId")}: #{job.job_number || "-"}</small>
        <p>{job.company_name} · {jobCategoryLabel(job.category, lang)} · {job.location}</p>
        <span>{job.salary_range}</span>
        {isScheduled && <small className="application-status status interview">{t("upcomingInterviews")}</small>}
        {applicationStatus && <small className={`application-status status ${applicationStatus}`}>{t("applicationStatus")}: {statusLabel(applicationStatus, lang)}</small>}
      </div>
      <div className="job-actions">
        <button className="secondary-button" onClick={() => setOpenJobId(isOpen ? "" : job.id)}>{t("jobDetails")}</button>
        <button className="primary-button" disabled={!!applicationStatus} onClick={() => questions.length && questionJobId !== job.id ? (setQuestionJobId(job.id), setOpenJobId(job.id), setApplyError("")) : apply(job)}>{applicationStatus ? statusLabel(applicationStatus, lang) : t("apply")}</button>
      </div>
      {isOpen && <section className="job-details">
        <dl>
          <div><dt>{t("jobId")}</dt><dd>#{job.job_number || "-"}</dd></div>
          <div><dt>{t("company")}</dt><dd>{job.company_name}</dd></div>
          <div><dt>{t("category")}</dt><dd>{jobCategoryLabel(job.category, lang)}</dd></div>
          <div><dt>{t("location")}</dt><dd>{job.location}</dd></div>
          <div><dt>{t("status")}</dt><dd>{statusLabel(job.status, lang)}</dd></div>
          <div><dt>{t("salary")}</dt><dd>{job.salary_range || "-"}</dd></div>
          <div><dt>{t("type")}</dt><dd>{job.type}</dd></div>
        </dl>
        <h3>{t("description")}</h3>
        <p>{job.description || "-"}</p>
        {questions.length > 0 && <div className="job-question-preview"><h3>{t("screeningQuestions")}</h3>{questions.map((question) => <span key={question}>{question}</span>)}</div>}
      </section>}
      {showQuestions && <section className="job-apply-questions">
        <h3>{t("answerQuestions")}</h3>
        {questions.map((question) => <label key={question}>{question}<textarea value={answerDrafts[job.id]?.[question] || ""} onChange={(event) => setAnswerDrafts({ ...answerDrafts, [job.id]: { ...(answerDrafts[job.id] || {}), [question]: event.target.value } })} /></label>)}
        {applyError && <p className="error">{applyError}</p>}
        <button className="primary-button compact" type="button" onClick={() => apply(job)}>{t("apply")}</button>
      </section>}
    </article>;
  }) : <article className="panel"><p>{t("noJobsMatching")}</p></article>}
    {visibleJobs.length > pageSize && <div className="pagination panel">
      <button className="secondary-button compact" type="button" disabled={page <= 1} onClick={() => setPage(page - 1)}>{t("previous")}</button>
      <span>{t("page")} {page} / {totalPages}</span>
      <button className="secondary-button compact" type="button" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>{t("next")}</button>
    </div>}
  </section>;
}

function Admin({ t, lang, admin, users, setUsers, jobs, applications, setApplications, interviews = [], supportThreads, initialTab, clearInitialTab, reload, openSupport }) {
  const [tab, setTab] = useState("overview");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState(null);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [jobAdminSearch, setJobAdminSearch] = useState("");
  const emptyJobForm = { companyName: "مختبرات روابط", title: "", category: "General", location: "عن بعد", type: "دوام كامل", salaryRange: "", description: "", questionsText: "" };
  const [jobForm, setJobForm] = useState(emptyJobForm);
  const [editingJob, setEditingJob] = useState(null);
  const [interview, setInterview] = useState({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
  const [schedulingInterview, setSchedulingInterview] = useState(false);
  const unreadTotal = supportThreads.filter((thread) => Number(thread.unread_count || 0) > 0).length;
  const adminTabs = [
    ["overview", t("overview"), "▦"],
    ["users", t("userManagement"), "◎"],
    ["jobs", t("jobManagement"), "▣"],
    ["applications", t("applicationManagement"), "◈"],
    ["interviews", t("interviews"), "◌"],
    ["support", t("supportInbox"), "✉"]
  ];
  const normalizedJobAdminSearch = jobAdminSearch.trim().toLowerCase();
  const adminVisibleJobs = jobs.filter((job) => {
    if (!normalizedJobAdminSearch) return true;
    return `${job.job_number || ""} ${job.title || ""} ${job.company_name || ""}`.toLowerCase().includes(normalizedJobAdminSearch);
  });
  const agents = users.filter((user) => user.role === "agent");
  useEffect(() => {
    if (initialTab) {
      setTab(initialTab);
      clearInitialTab?.();
    }
  }, [initialTab]);
  async function searchUsers(value) {
    setSearch(value);
    setUsers(await api(`/admin/users?search=${encodeURIComponent(value)}`));
  }
  async function patchUser(user, patch) {
    await api(`/admin/users/${user.id}`, { method: "PATCH", body: JSON.stringify(patch) });
    searchUsers(search);
  }
  async function deleteUser(user) {
    if (!confirm(`Delete ${user.full_name}?`)) return;
    await api(`/admin/users/${user.id}`, { method: "DELETE" });
    searchUsers(search);
  }
  async function openUserProfile(user) {
    setSelectedProfile(await api(`/admin/users/${user.id}/profile`));
    setEditing(null);
    setTab("userProfile");
  }
  async function refreshSelectedProfile(userId = selectedProfile?.user?.id) {
    if (!userId) return;
    setSelectedProfile(await api(`/admin/users/${userId}/profile`));
    await searchUsers(search);
  }
  async function runUserAction(user, action) {
    if (!action) return;
    if (action === "edit") await openUserProfile(user);
    if (action === "verify") await patchUser(user, { status: "verified" });
    if (action === "activate") await patchUser(user, { status: "active" });
    if (action === "deactivate") await patchUser(user, { status: "suspended" });
    if (action === "delete") await deleteUser(user);
  }
  async function saveSelectedProfile(event) {
    event.preventDefault();
    await api(`/admin/users/${selectedProfile.user.id}/profile`, {
      method: "PATCH",
      body: JSON.stringify({
        fullName: selectedProfile.user.full_name,
        email: selectedProfile.user.email,
        newPassword: selectedProfile.user.newPassword || undefined,
        phone: selectedProfile.user.phone,
        dob: selectedProfile.user.dob,
        headline: selectedProfile.user.headline,
        location: selectedProfile.user.location,
        role: selectedProfile.user.role,
        plan: selectedProfile.user.plan,
        status: selectedProfile.user.status,
        about: selectedProfile.profile?.about || "",
        skills: typeof selectedProfile.profile?.skills === "string" ? selectedProfile.profile.skills.split(",").map((item) => item.trim()).filter(Boolean) : selectedProfile.profile?.skills || []
      })
    });
    setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, newPassword: "" } });
    await refreshSelectedProfile();
  }
  async function uploadSelectedAttachment(kind, file) {
    if (!file || !selectedProfile) return;
    const body = new FormData();
    body.append("kind", kind);
    body.append("file", file);
    try {
      await api(`/admin/users/${selectedProfile.user.id}/documents`, { method: "POST", body });
      await refreshSelectedProfile();
    } catch (err) {
      alert(err.message);
    }
  }
  async function uploadSelectedAvatar(file) {
    if (!file || !selectedProfile) return;
    const body = new FormData();
    body.append("file", file);
    await api(`/admin/users/${selectedProfile.user.id}/avatar`, { method: "POST", body });
    await refreshSelectedProfile();
  }
  async function deleteSelectedAttachment(documentId) {
    await api(`/admin/documents/${documentId}`, { method: "DELETE" });
    await refreshSelectedProfile();
  }
  async function saveUser(event) {
    event.preventDefault();
    await api(`/admin/users/${editing.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        fullName: editing.full_name,
        email: editing.email,
        newPassword: editing.newPassword || undefined,
        phone: editing.phone,
        dob: editing.dob,
        headline: editing.headline,
        location: editing.location,
        role: editing.role,
        plan: editing.plan,
        status: editing.status
      })
    });
    setEditing(null);
    searchUsers(search);
  }
  async function addJob(event) {
    event.preventDefault();
    await api("/admin/jobs", { method: "POST", body: JSON.stringify({ ...jobForm, screeningQuestions: questionsFromText(jobForm.questionsText) }) });
    setJobForm(emptyJobForm);
    await reload();
  }
  function startEditJob(job) {
    setEditingJob({
      id: job.id,
      companyName: job.company_name || "",
      title: job.title || "",
      category: job.category || "General",
      location: job.location || "",
      type: job.type || "دوام كامل",
      salaryRange: job.salary_range || "",
      description: job.description || "",
      status: job.status || "active",
      questionsText: questionsToText(job.screening_questions)
    });
    setTimeout(() => document.getElementById("edit-job-form")?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
  }
  async function runJobAction(job, action) {
    if (!action) return;
    if (action === "edit") startEditJob(job);
    if (action === "delete") await deleteJob(job);
  }
  async function saveJob(event) {
    event.preventDefault();
    await api(`/admin/jobs/${editingJob.id}`, { method: "PATCH", body: JSON.stringify({ ...editingJob, screeningQuestions: questionsFromText(editingJob.questionsText) }) });
    setEditingJob(null);
    await reload();
  }
  async function deleteJob(job) {
    if (!confirm(`${t("deleteJob")}: ${job.title}?`)) return;
    await api(`/admin/jobs/${job.id}`, { method: "DELETE" });
    if (editingJob?.id === job.id) setEditingJob(null);
    await reload();
  }
  async function updateApplicationStatus(application, status) {
    const nextStatus = normalizeStatusValue(status);
    if (!nextStatus) return;
    if (nextStatus === "interview") {
      setInterview({
        userId: application.user_id,
        jobId: application.job_id,
        scheduledAt: "",
        channel: interview.channel || "Video call",
        notes: `${application.full_name} - ${application.job_title}`
      });
      setTab("interviews");
      setTimeout(() => document.getElementById("schedule-interview-form")?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
      return;
    }
    await api(`/admin/applications/${application.id}`, { method: "PATCH", body: JSON.stringify({ status: nextStatus }) });
    setApplications(await api("/admin/applications"));
    await reload();
  }
  async function shareApplication(application, agentId) {
    if (!agentId) return;
    await api("/admin/application-shares", {
      method: "POST",
      body: JSON.stringify({ applicationId: application.id, agentId })
    });
  }
  async function shareUser(targetUser, agentId) {
    if (!agentId) return;
    await api("/admin/user-shares", {
      method: "POST",
      body: JSON.stringify({ userId: targetUser.id, agentId })
    });
  }
  async function scheduleInterview(event) {
    event.preventDefault();
    if (!interview.userId || !interview.scheduledAt) return;
    setSchedulingInterview(true);
    try {
      const result = await api("/admin/interviews", {
        method: "POST",
        body: JSON.stringify({ ...interview, jobId: interview.jobId || null })
      });
      if (result.emailSent) {
        alert(`${t("interviewEmailSent")} ${result.recipientEmail}`);
      } else {
        alert(`${t("interviewEmailFailed")}: ${result.emailError || "-"}`);
      }
      setInterview({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
      await reload();
    } finally {
      setSchedulingInterview(false);
    }
  }
  async function updateInterviewStatus(item, status) {
    const nextStatus = normalizeStatusValue(status);
    if (!nextStatus) return;
    await api(`/admin/interviews/${item.id}`, { method: "PATCH", body: JSON.stringify({ status: nextStatus }) });
    await reload();
  }
  if (!admin) return null;
  return (
    <div className="admin-page">
      <section className="admin-heading"><div><p>{t("admin")}</p><h1>{t("adminDashboard")}</h1></div><button className="primary-button">{t("reports")}</button></section>
      <section className="admin-console">
        <aside className="admin-menu panel">
          {adminTabs.map(([id, label, icon]) => <button className={tab === id ? "active" : ""} type="button" onClick={() => setTab(id)} key={id}><span>{icon}</span>{label}{id === "support" && unreadTotal > 0 && <b>{unreadTotal}</b>}</button>)}
        </aside>

        <div className="admin-content">
          {tab === "overview" && <>
            <section className="metric-grid">
              <Metric label={t("totalUsers")} value={admin.metrics.users} />
              <Metric label={t("verifiedProfiles")} value={admin.metrics.verifiedProfiles} />
              <Metric label={t("applications")} value={admin.metrics.applications} />
              <Metric label={t("activeJobs")} value={admin.metrics.activeJobs} />
              <Metric label={t("suspendedUsers")} value={admin.metrics.suspendedUsers} />
              <Metric label={t("pendingInterviews")} value={admin.metrics.pendingInterviews} />
            </section>
            <section className="analytics-grid">
              <AnalyticsBars title={t("usersGrowth")} data={admin.analytics?.usersGrowth || []} />
              <AnalyticsBars title={t("jobsPosted")} data={admin.analytics?.jobsPosted || []} />
              <AnalyticsBars title={t("monthlyApplications")} data={admin.analytics?.monthlyApplications || []} />
              <AnalyticsList title={t("applicationOutcomes")} data={admin.analytics?.applicationOutcomes || []} />
              <AnalyticsList title={t("jobCategories")} data={admin.analytics?.jobCategories || []} />
              <article className="panel">
                <h2>{t("riskQueue")}</h2>
                <div className="risk-list"><strong>{admin.metrics.pendingDocuments}</strong><span>{t("pendingDocs")}</span></div>
              </article>
              <AnalyticsList title={t("profileHealth")} data={admin.analytics?.profileHealth || []} />
            </section>
          </>}

          {tab === "users" && <>
            <section className="panel">
              <div className="section-head"><h2>{t("users")}</h2><input placeholder={t("searchUsers")} value={search} onChange={(e) => searchUsers(e.target.value)} /></div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>{t("users")}</th><th>{t("role")}</th><th>{t("plan")}</th><th>{t("status")}</th><th>{t("attachments")}</th><th>{t("lastActive")}</th><th>{t("shareWithAgent")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>{users.map((user) => <tr key={user.id}><td><div className="table-user"><Avatar user={user} size="small" /><div><strong>{user.full_name}</strong><span>{user.email}</span></div></div></td><td>{user.role}</td><td><select className="plan-select" value={user.plan || "free"} onChange={(e) => patchUser(user, { plan: e.target.value })}>{PLAN_OPTIONS.map((plan) => <option value={plan} key={plan}>{planLabel(plan, lang)}</option>)}</select></td><td><span className={`status ${user.status}`}>{statusLabel(user.status, lang)}</span></td><td><DocumentLinks t={t} documents={user.documents} avatarUrl={user.avatar_url} compact /></td><td>{new Date(user.last_active_at).toLocaleDateString()}</td><td><select className="action-select" defaultValue="" disabled={!agents.length} onChange={async (e) => { await shareUser(user, e.target.value); e.target.value = ""; }}><option value="">{agents.length ? t("shareWithAgent") : t("agent")}</option>{agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}</select></td><td><select className="action-select" defaultValue="" onChange={(e) => { runUserAction(user, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option><option value="edit">{t("editUser")}</option><option value="verify">{t("verify")}</option><option value="activate">{t("activate")}</option><option value="deactivate">{t("deactivate")}</option><option value="delete">{t("delete")}</option></select></td></tr>)}</tbody>
                </table>
              </div>
            </section>
            {editing && <form className="panel admin-form" onSubmit={saveUser}>
              <h2>{t("editUser")}</h2>
              <input value={editing.full_name || ""} onChange={(e) => setEditing({ ...editing, full_name: e.target.value })} />
              <input value={editing.email || ""} onChange={(e) => setEditing({ ...editing, email: e.target.value })} />
              <input type="password" value={editing.newPassword || ""} onChange={(e) => setEditing({ ...editing, newPassword: e.target.value })} placeholder={t("password")} autoComplete="new-password" />
              <input value={editing.phone || ""} onChange={(e) => setEditing({ ...editing, phone: e.target.value })} placeholder={t("phone")} />
              <input type="date" value={editing.dob || ""} onChange={(e) => setEditing({ ...editing, dob: e.target.value })} />
              <input value={editing.headline || ""} onChange={(e) => setEditing({ ...editing, headline: e.target.value })} placeholder={t("headline")} />
              <input value={editing.location || ""} onChange={(e) => setEditing({ ...editing, location: e.target.value })} placeholder={t("location")} />
              <div className="row-fields">
                <select value={editing.role} onChange={(e) => setEditing({ ...editing, role: e.target.value })}>{USER_ROLES.map((role) => <option value={role} key={role}>{role}</option>)}</select>
                <select value={editing.plan || "free"} onChange={(e) => setEditing({ ...editing, plan: e.target.value })}>{PLAN_OPTIONS.map((plan) => <option value={plan} key={plan}>{planLabel(plan, lang)}</option>)}</select>
                <select value={editing.status} onChange={(e) => setEditing({ ...editing, status: e.target.value })}>{USER_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select>
                <button className="primary-button">{t("save")}</button>
              </div>
            </form>}
          </>}

          {tab === "userProfile" && selectedProfile && <section className="admin-profile-view">
            <div className="section-head">
              <h2>{t("profileDetails")}</h2>
              <button className="secondary-button compact" onClick={() => setTab("users")}>{t("backToUsers")}</button>
            </div>
            <section className="profile-hero panel">
              <Avatar user={selectedProfile.user} size="large" />
              <div><h1>{selectedProfile.user.full_name}</h1><p>{selectedProfile.user.headline}</p><span>{selectedProfile.user.location}</span></div>
            </section>
            <section className="admin-profile-grid">
              <form className="panel admin-form" onSubmit={saveSelectedProfile}>
                <h2>{t("editUser")}</h2>
                <input value={selectedProfile.user.full_name || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, full_name: e.target.value } })} />
                <input value={selectedProfile.user.email || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, email: e.target.value } })} />
                <input type="password" value={selectedProfile.user.newPassword || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, newPassword: e.target.value } })} placeholder={t("password")} autoComplete="new-password" />
                <input value={selectedProfile.user.phone || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, phone: e.target.value } })} placeholder={t("phone")} />
                <input type="date" value={selectedProfile.user.dob || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, dob: e.target.value } })} />
                <input value={selectedProfile.user.headline || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, headline: e.target.value } })} placeholder={t("headline")} />
                <input value={selectedProfile.user.location || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, location: e.target.value } })} placeholder={t("location")} />
                <select value={selectedProfile.user.plan || "free"} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, plan: e.target.value } })}>{PLAN_OPTIONS.map((plan) => <option value={plan} key={plan}>{planLabel(plan, lang)}</option>)}</select>
                <textarea value={selectedProfile.profile?.about || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, profile: { ...(selectedProfile.profile || {}), about: e.target.value } })} placeholder={t("about")} />
                <input value={Array.isArray(selectedProfile.profile?.skills) ? selectedProfile.profile.skills.join(", ") : selectedProfile.profile?.skills || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, profile: { ...(selectedProfile.profile || {}), skills: e.target.value } })} placeholder={t("skills")} />
                <div className="row-fields">
                  <select value={selectedProfile.user.role} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, role: e.target.value } })}>{USER_ROLES.map((role) => <option value={role} key={role}>{role}</option>)}</select>
                  <select value={selectedProfile.user.status} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, status: e.target.value } })}>{USER_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select>
                  <button className="primary-button">{t("save")}</button>
                </div>
              </form>
              <section className="panel admin-form">
                <h2>{t("attachments")}</h2>
                <label>{t("profilePicture")}<input type="file" accept="image/*" onChange={(e) => uploadSelectedAvatar(e.target.files[0])} /></label>
                <label>{t("resume")}<input type="file" accept=".pdf,.doc,.docx" onChange={(e) => uploadSelectedAttachment("resume", e.target.files[0])} /></label>
                <label>{t("certificate")}<input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e) => uploadSelectedAttachment("certificate", e.target.files[0])} /><span>{t("maxCertificates")}</span></label>
                <DocumentLinks t={t} documents={selectedProfile.documents} avatarUrl={selectedProfile.user.avatar_url} onDelete={deleteSelectedAttachment} />
              </section>
            </section>
            <section className="panel">
              <h2>{t("about")}</h2>
              <p>{selectedProfile.profile?.about || "-"}</p>
              <div className="chips">{(selectedProfile.profile?.skills || []).map((skill) => <span key={skill}>{skill}</span>)}</div>
            </section>
            <section className="panel">
              <h2>{t("experience")}</h2>
              {(selectedProfile.experiences || []).map((item) => <div className="timeline-item" key={item.id}><strong>{item.title}</strong><span>{item.company}</span></div>)}
            </section>
          </section>}

          {tab === "jobs" && <section className="job-admin-grid">
            <form className="panel admin-form job-editor-form" onSubmit={addJob}>
              <h2>{t("addJob")}</h2>
              <input placeholder={t("company")} value={jobForm.companyName} onChange={(e) => setJobForm({ ...jobForm, companyName: e.target.value })} />
              <input placeholder={t("title")} value={jobForm.title} onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })} />
              <select value={jobForm.category} onChange={(e) => setJobForm({ ...jobForm, category: e.target.value })}>
                {JOB_CATEGORIES.map((item) => <option value={item.value} key={item.value}>{item[lang]}</option>)}
              </select>
              <input placeholder={t("location")} value={jobForm.location} onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })} />
              <input placeholder={t("salary")} value={jobForm.salaryRange} onChange={(e) => setJobForm({ ...jobForm, salaryRange: e.target.value })} />
              <textarea placeholder={t("description")} value={jobForm.description} onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })} />
              <textarea placeholder={`${t("screeningQuestions")} - ${t("screeningQuestionsHelp")}`} value={jobForm.questionsText} onChange={(e) => setJobForm({ ...jobForm, questionsText: e.target.value })} />
              <button className="primary-button">{t("addJob")}</button>
            </form>

            {editingJob && <form id="edit-job-form" className="panel admin-form job-editor-form" onSubmit={saveJob}>
              <h2>{t("editJob")}</h2>
              <input placeholder={t("company")} value={editingJob.companyName} onChange={(e) => setEditingJob({ ...editingJob, companyName: e.target.value })} />
              <input placeholder={t("title")} value={editingJob.title} onChange={(e) => setEditingJob({ ...editingJob, title: e.target.value })} />
              <select value={editingJob.category} onChange={(e) => setEditingJob({ ...editingJob, category: e.target.value })}>
                {JOB_CATEGORIES.map((item) => <option value={item.value} key={item.value}>{item[lang]}</option>)}
              </select>
              <input placeholder={t("location")} value={editingJob.location} onChange={(e) => setEditingJob({ ...editingJob, location: e.target.value })} />
              <input placeholder={t("type")} value={editingJob.type} onChange={(e) => setEditingJob({ ...editingJob, type: e.target.value })} />
              <input placeholder={t("salary")} value={editingJob.salaryRange} onChange={(e) => setEditingJob({ ...editingJob, salaryRange: e.target.value })} />
              <select value={editingJob.status} onChange={(e) => setEditingJob({ ...editingJob, status: e.target.value })}>{JOB_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select>
              <textarea placeholder={t("description")} value={editingJob.description} onChange={(e) => setEditingJob({ ...editingJob, description: e.target.value })} />
              <textarea placeholder={`${t("screeningQuestions")} - ${t("screeningQuestionsHelp")}`} value={editingJob.questionsText || ""} onChange={(e) => setEditingJob({ ...editingJob, questionsText: e.target.value })} />
              <div className="row-fields">
                <button className="primary-button">{t("save")}</button>
                <button className="secondary-button" type="button" onClick={() => setEditingJob(null)}>{t("cancel")}</button>
              </div>
            </form>}

            <section className="panel span-two job-management-card">
              <div className="section-head"><h2>{t("jobManagement")}</h2><input placeholder={t("searchJobs")} value={jobAdminSearch} onChange={(e) => setJobAdminSearch(e.target.value)} /><span className="status">{adminVisibleJobs.length}</span></div>
              <div className="table-wrap job-table-wrap">
                <table>
                  <thead><tr><th>{t("jobId")}</th><th>{t("job")}</th><th>{t("category")}</th><th>{t("location")}</th><th>{t("status")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>{adminVisibleJobs.map((job) => <tr key={job.id}><td><strong className="job-number">#{job.job_number || "-"}</strong></td><td><strong>{job.title}</strong><span>{job.company_name}</span></td><td>{jobCategoryLabel(job.category, lang)}</td><td>{job.location}</td><td><span className={`status ${job.status}`}>{statusLabel(job.status, lang)}</span></td><td><select className="action-select" defaultValue="" onChange={(e) => { runJobAction(job, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option><option value="edit">{t("editJob")}</option><option value="delete">{t("deleteJob")}</option></select></td></tr>)}</tbody>
                </table>
              </div>
            </section>
          </section>}

          {tab === "applications" && <section className="panel">
            <div className="section-head"><h2>{t("applications")}</h2><span className="status">{applications.length}</span></div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>{t("applicant")}</th><th>{t("job")}</th><th>{t("location")}</th><th>{t("submittedAnswers")}</th><th>{t("applicationStatus")}</th><th>{t("shareWithAgent")}</th><th>{t("actions")}</th></tr></thead>
                <tbody>{applications.map((application) => <tr key={application.id}><td><div className="table-user"><Avatar user={{ full_name: application.full_name, avatar_url: application.avatar_url }} size="small" /><div><strong>{application.full_name}</strong><span>{application.email}</span></div></div></td><td><strong>{application.job_title}</strong><span>{application.company_name}</span></td><td>{application.location}</td><td><ApplicationAnswers t={t} answers={application.screening_answers} /></td><td><span className={`status ${application.status}`}>{statusLabel(application.status, lang)}</span></td><td><select className="action-select" defaultValue="" disabled={!agents.length} onChange={async (e) => { await shareApplication(application, e.target.value); e.target.value = ""; }}><option value="">{agents.length ? t("shareWithAgent") : t("agent")}</option>{agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}</select></td><td><select className="action-select" defaultValue="" onChange={(e) => { updateApplicationStatus(application, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option>{APPLICATION_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select></td></tr>)}</tbody>
              </table>
            </div>
          </section>}

          {tab === "interviews" && <>
            <form id="schedule-interview-form" className="panel admin-form" onSubmit={scheduleInterview}>
              <h2>{t("scheduleInterview")}</h2>
              <select value={interview.userId} onChange={(e) => setInterview({ ...interview, userId: e.target.value })}><option value="">{t("users")}</option>{users.map((user) => <option key={user.id} value={user.id}>{user.full_name} - {user.email}</option>)}</select>
              <select value={interview.jobId} onChange={(e) => setInterview({ ...interview, jobId: e.target.value })}><option value="">{t("jobs")}</option>{jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}</select>
              <input type="datetime-local" value={interview.scheduledAt} onChange={(e) => setInterview({ ...interview, scheduledAt: e.target.value })} />
              <input placeholder={t("channel")} value={interview.channel} onChange={(e) => setInterview({ ...interview, channel: e.target.value })} />
              <textarea placeholder={t("notes")} value={interview.notes} onChange={(e) => setInterview({ ...interview, notes: e.target.value })} />
              <button className="primary-button loading-button" disabled={schedulingInterview}>{schedulingInterview && <span className="spinner" aria-hidden="true"></span>}{t("scheduleInterview")}</button>
            </form>
            <section className="panel">
              <div className="section-head"><h2>{t("upcomingAdminInterviews")}</h2><span className="status">{interviews.length}</span></div>
              <div className="interview-admin-list">
                {interviews.length ? interviews.map((item) => <article className="interview-admin-item" key={item.id}>
                  <div><strong>{item.full_name}</strong><span>{item.email}</span></div>
                  <div><strong>{item.job_title || t("job")}</strong><span>{item.company_name || "-"}</span></div>
                  <div><strong>{new Date(item.scheduled_at).toLocaleString()}</strong><span>{item.channel}</span></div>
                  <select className="action-select" defaultValue="" onChange={(e) => { updateInterviewStatus(item, e.target.value); e.target.value = ""; }}>
                    <option value="">{t("interviewOutcome")}</option>
                    {INTERVIEW_OUTCOME_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}
                  </select>
                </article>) : <p>{t("noAppliedJobs")}</p>}
              </div>
            </section>
          </>}

          {tab === "support" && <section className="panel">
            <div className="section-head"><h2>{t("supportInbox")}</h2><span className="status">{unreadTotal} {t("unreadMessages")}</span></div>
            <div className="support-thread-list">
              {supportThreads.map((thread) => <article className={Number(thread.unread_count) > 0 ? "support-thread unread" : "support-thread"} key={thread.user_id}>
                <Avatar user={{ fullName: thread.full_name }} size="small" />
                <div><strong>{thread.full_name}</strong><span>{thread.email}</span><p>{thread.last_message}</p></div>
                <div className="support-thread-actions">{Number(thread.unread_count) > 0 && <b>{thread.unread_count}</b>}<button className="secondary-button compact" onClick={() => openSupport(thread.user_id)}>{t("openChat")}</button></div>
              </article>)}
            </div>
          </section>}
        </div>
      </section>
    </div>
  );
}

function AgentWorkspace({ t, lang, shares = [] }) {
  return (
    <section className="agent-page">
      <div className="section-head">
        <div>
          <h2>{t("agentWorkspace")}</h2>
          <p>{t("sharedProfiles")}</p>
        </div>
        <span className="status">{shares.length}</span>
      </div>
      {shares.length ? shares.map((share) => {
        const skills = Array.isArray(share.skills) ? share.skills : [];
        const experiences = Array.isArray(share.experiences) ? share.experiences : [];
        const isApplicationShare = share.share_type === "application";
        return (
          <article className="panel agent-share-card" key={share.share_id}>
            <header className="agent-profile-head">
              <Avatar user={{ full_name: share.full_name, avatar_url: share.avatar_url }} size="large" />
              <div>
                <h2>{share.full_name}</h2>
                <p>{share.headline || "-"}</p>
                <span>{share.email}</span>
              </div>
              <div className="agent-job-summary">
                {isApplicationShare ? <>
                  <strong>{share.job_title}</strong>
                  <span>{t("jobId")}: #{share.job_number || "-"}</span>
                  <span>{share.company_name} · {share.salary_range || "-"}</span>
                  <b className={`status ${share.application_status}`}>{statusLabel(share.application_status, lang)}</b>
                </> : <>
                  <strong>{t("profileDetails")}</strong>
                  <span>{t("sharedProfiles")}</span>
                </>}
              </div>
            </header>

            <div className="agent-share-grid">
              <section>
                <h3>{t("profileDetails")}</h3>
                <dl className="profile-facts">
                  <div><dt>{t("phone")}</dt><dd>{share.phone || "-"}</dd></div>
                  <div><dt>{t("dob")}</dt><dd>{share.dob || "-"}</dd></div>
                  <div><dt>{t("location")}</dt><dd>{share.user_location || "-"}</dd></div>
                  <div><dt>{t("about")}</dt><dd>{share.about || "-"}</dd></div>
                </dl>
                <div className="chips">{skills.length ? skills.map((skill) => <span key={skill}>{skill}</span>) : <span>{t("skills")}</span>}</div>
              </section>
              <section>
                <h3>{t("attachments")}</h3>
                <DocumentLinks t={t} documents={share.documents} avatarUrl={share.avatar_url} />
              </section>
              <section>
                <h3>{t("experience")}</h3>
                {experiences.length ? experiences.map((item) => (
                  <div className="timeline-item" key={item.id}>
                    <strong>{item.title}</strong>
                    <span>{item.company}{item.location ? ` · ${item.location}` : ""}</span>
                    {item.description && <p>{item.description}</p>}
                  </div>
                )) : <p className="muted-text">{t("workTimeline")}</p>}
              </section>
              {isApplicationShare && <section>
                <h3>{t("submittedAnswers")}</h3>
                <ApplicationAnswers t={t} answers={share.screening_answers} />
              </section>}
            </div>
          </article>
        );
      }) : <article className="panel"><p>{t("noSharedProfiles")}</p></article>}
    </section>
  );
}

function SupportWindow({ t, me, users, initialUserId = "", onUpdate, close }) {
  const [targetUserId, setTargetUserId] = useState(me.user.role === "admin" ? initialUserId || users[0]?.id || "" : me.user.id);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [chatError, setChatError] = useState("");
  async function loadMessages(userId = targetUserId) {
    const query = me.user.role === "admin" && userId ? `?user_id=${userId}` : "";
    setMessages(await api(`/support/messages${query}`));
    await onUpdate?.();
  }
  useEffect(() => {
    if (me.user.role === "admin" && !targetUserId && users[0]?.id) setTargetUserId(users[0].id);
  }, [users.length, targetUserId, me.user.role]);
  useEffect(() => {
    if (me.user.role === "admin" && initialUserId && initialUserId !== targetUserId) setTargetUserId(initialUserId);
  }, [initialUserId, me.user.role, targetUserId]);
  useEffect(() => { loadMessages(); }, [targetUserId]);
  async function sendMessage(event) {
    event.preventDefault();
    if (!message.trim()) return;
    setSending(true);
    try {
      await api("/support/messages", { method: "POST", body: JSON.stringify({ message, userId: me.user.role === "admin" ? targetUserId : undefined }) });
      setMessage("");
      await loadMessages();
    } finally {
      setSending(false);
    }
  }
  async function clearChat() {
    setClearing(true);
    setChatError("");
    try {
      await api("/support/messages/clear", {
        method: "POST",
        body: JSON.stringify({ userId: me.user.role === "admin" ? targetUserId : undefined })
      });
      setMessages([]);
      await onUpdate?.();
    } catch (err) {
      setChatError(err.message || t("clearFailed"));
    } finally {
      setClearing(false);
    }
  }
  async function requestLiveSupport() {
    setSending(true);
    try {
      await api("/support/messages", { method: "POST", body: JSON.stringify({ message: t("liveAgentRequest"), userId: me.user.role === "admin" ? targetUserId : undefined }) });
      await loadMessages();
    } finally {
      setSending(false);
    }
  }
  async function endConversation() {
    await clearChat();
    close();
  }
  const lastMessage = messages[messages.length - 1];
  const showBotOptions = lastMessage?.sender_role === "bot" && /دعم مباشر|live support|end the conversation|إنهاء المحادثة/.test(lastMessage.message || "");
  return (
    <div className="support-window">
      <header><strong>{t("support")}</strong><div><button type="button" onClick={clearChat} disabled={clearing}>{clearing ? t("clearingChat") : t("clearChat")}</button><button onClick={close}>×</button></div></header>
      {me.user.role === "admin" && <select value={targetUserId} onChange={(e) => setTargetUserId(e.target.value)}>{users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}</select>}
      <div className="support-messages">
        {messages.map((item) => <p className={`support-bubble ${item.sender_role}`} key={item.id}><strong>{item.sender_role}</strong>{item.message}</p>)}
      </div>
      {showBotOptions && <div className="support-options">
        <button className="secondary-button compact" type="button" onClick={requestLiveSupport} disabled={sending}>{t("speakLive")}</button>
        <button className="secondary-button compact" type="button" onClick={endConversation} disabled={clearing}>{t("endConversation")}</button>
      </div>}
      {chatError && <p className="error support-error">{chatError}</p>}
      <form onSubmit={sendMessage}>
        <input placeholder={t("supportMessage")} value={message} onChange={(e) => setMessage(e.target.value)} />
        <button className="primary-button" disabled={sending}>{t("send")}</button>
      </form>
    </div>
  );
}

function ApplicationAnswers({ t, answers = [] }) {
  const safeAnswers = Array.isArray(answers) ? answers : [];
  if (!safeAnswers.length) return <span className="muted-text">{t("noQuestions")}</span>;
  return <details className="answer-details">
    <summary>{t("view")}</summary>
    <div>
      {safeAnswers.map((item, index) => <article key={`${item.question}-${index}`}>
        <strong>{item.question}</strong>
        <span>{item.answer || "-"}</span>
      </article>)}
    </div>
  </details>;
}

function DocumentLinks({ t, documents = [], avatarUrl = "", compact = false, onDelete }) {
  const files = [
    ...(avatarUrl ? [{ id: "avatar", kind: "avatar", file_name: t("profilePicture"), file_url: avatarUrl }] : []),
    ...(Array.isArray(documents) ? documents : [])
  ];
  if (!files.length) return <p className="attachment-empty">{t("noAttachments")}</p>;
  if (compact) {
    return (
      <select className="attachment-select" defaultValue="" onChange={(event) => { if (event.target.value) window.open(event.target.value, "_blank", "noopener,noreferrer"); event.target.value = ""; }}>
        <option value="">{t("attachments")}</option>
        {files.map((item) => <option value={assetUrl(item.file_url || item.fileUrl)} key={item.id}>
          {item.kind === "resume" ? t("resume") : item.kind === "avatar" ? t("profilePicture") : t("certificate")} - {item.file_name || item.fileName || t("viewFile")}
        </option>)}
      </select>
    );
  }
  return (
    <div className="attachment-list">
      <strong>{t("attachments")}</strong>
      {files.map((item) => <div className="attachment-row" key={item.id}>
        <a href={assetUrl(item.file_url || item.fileUrl)} target="_blank" rel="noreferrer">
          <span>{item.kind === "resume" ? t("resume") : item.kind === "avatar" ? t("profilePicture") : t("certificate")}</span>
          {item.file_name || item.fileName || t("viewFile")}
        </a>
        {onDelete && item.kind !== "avatar" && <button type="button" onClick={() => onDelete(item.id)}>{t("removeAttachment")}</button>}
      </div>)}
    </div>
  );
}

function Metric({ label, value }) {
  return <article className="metric-card"><span>{label}</span><strong>{formatNumber(value)}</strong></article>;
}

function AnalyticsBars({ title, data = [] }) {
  const max = Math.max(1, ...data.map((item) => Number(item.value || 0)));
  return (
    <article className="panel analytics-card">
      <h2>{title}</h2>
      <div className="bar-chart compact-chart">
        {data.map((item) => {
          const value = Number(item.value || 0);
          return <div className="bar-group" key={item.label}><span title={`${item.label}: ${value}`} style={{ height: `${Math.max(8, (value / max) * 100)}%` }} /><small>{item.label}</small><b>{value}</b></div>;
        })}
      </div>
    </article>
  );
}

function AnalyticsList({ title, data = [] }) {
  const total = data.reduce((sum, item) => sum + Number(item.value || 0), 0);
  return (
    <article className="panel analytics-card">
      <h2>{title}</h2>
      <div className="analytics-list">
        {data.length ? data.map((item) => {
          const value = Number(item.value || 0);
          const percent = total ? Math.round((value / total) * 100) : 0;
          return <div className="analytics-row" key={item.label}><span>{item.label}</span><strong>{value}</strong><div><i style={{ width: `${percent}%` }} /></div></div>;
        }) : <p>0</p>}
      </div>
    </article>
  );
}

function Avatar({ user, size = "" }) {
  const [failed, setFailed] = useState(false);
  const className = `avatar ${size}`.trim();
  const avatarUrl = user.avatarUrl || user.avatar_url;
  const src = avatarUrl ? assetUrl(avatarUrl) : "";
  const name = user.fullName || user.full_name || "";
  useEffect(() => setFailed(false), [src]);
  if (src && !failed) return <img className={className} src={src} alt={name || "Profile"} onError={() => setFailed(true)} />;
  return <div className={className}>{initials(name)}</div>;
}

function initials(name = "") {
  return name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

function formatNumber(value = 0) {
  return Number(value || 0).toLocaleString();
}

function assetUrl(path = "") {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const apiBase = (import.meta.env.VITE_API_URL || "/api").replace(/\/api$/, "");
  return `${apiBase}${path}`;
}

createRoot(document.getElementById("root")).render(<App />);
