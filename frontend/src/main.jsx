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
    logout: "Logout",
    demoAdmin: "Admin demo",
    demoUser: "User demo",
    home: "Home",
    profile: "Profile",
    jobs: "Jobs",
    admin: "Admin",
    network: "Network",
    search: "Search people, jobs, companies",
    completeProfile: "Complete profile",
    workspace: "Workspace",
    profileViews: "Profile views",
    connections: "Connections",
    profileStrength: "Profile strength",
    strengthGreat: "All-Star profile. You look ready for recruiters.",
    strengthGood: "Strong profile. Add certificates for more credibility.",
    publicProfile: "Public profile",
    savedJobs: "Saved jobs",
    myNetwork: "My network",
    peopleYouMayKnow: "People you may know",
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
    activeJobs: "Active jobs",
    appliedJobs: "Applied jobs",
    whereIApplied: "Where I applied for",
    noAppliedJobs: "No applications yet",
    apply: "Apply",
    adminDashboard: "Admin dashboard",
    totalUsers: "Total users",
    verifiedProfiles: "Verified profiles",
    applications: "Applications",
    monthlyRevenue: "Monthly revenue",
    users: "Users",
    searchUsers: "Search users",
    reports: "Reports",
    overview: "Overview",
    userManagement: "User management",
    jobManagement: "Job management",
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
    editUser: "Edit user",
    delete: "Delete",
    verify: "Verify",
    activate: "Activate",
    deactivate: "Deactivate",
    addJob: "Add job",
    salary: "Salary",
    description: "Description",
    scheduleInterview: "Schedule interview",
    interviewTime: "Interview time",
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
    logout: "خروج",
    demoAdmin: "تجربة المدير",
    demoUser: "تجربة المستخدم",
    home: "الرئيسية",
    profile: "الملف",
    jobs: "الوظائف",
    admin: "الإدارة",
    network: "الشبكة",
    search: "ابحث عن أشخاص أو وظائف أو شركات",
    completeProfile: "أكمل الملف",
    workspace: "مساحة العمل",
    profileViews: "مشاهدات الملف",
    connections: "العلاقات",
    profileStrength: "قوة الملف",
    strengthGreat: "ملف ممتاز. أنت جاهز للظهور أمام مسؤولي التوظيف.",
    strengthGood: "ملف قوي. أضف الشهادات لزيادة الموثوقية.",
    publicProfile: "الملف العام",
    savedJobs: "الوظائف المحفوظة",
    myNetwork: "شبكتي",
    peopleYouMayKnow: "أشخاص قد تعرفهم",
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
    activeJobs: "الوظائف النشطة",
    appliedJobs: "الوظائف المقدمة",
    whereIApplied: "الوظائف التي تقدمت إليها",
    noAppliedJobs: "لا توجد طلبات بعد",
    apply: "تقديم",
    adminDashboard: "لوحة تحكم الإدارة",
    totalUsers: "إجمالي المستخدمين",
    verifiedProfiles: "الملفات الموثقة",
    applications: "طلبات التقديم",
    monthlyRevenue: "الإيراد الشهري",
    users: "المستخدمون",
    searchUsers: "ابحث عن مستخدمين",
    reports: "التقارير",
    overview: "نظرة عامة",
    userManagement: "إدارة المستخدمين",
    jobManagement: "إدارة الوظائف",
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
    editUser: "تعديل المستخدم",
    delete: "حذف",
    verify: "توثيق",
    activate: "تفعيل",
    deactivate: "إيقاف",
    addJob: "إضافة وظيفة",
    salary: "الراتب",
    description: "الوصف",
    scheduleInterview: "جدولة مقابلة",
    interviewTime: "وقت المقابلة",
    channel: "القناة",
    notes: "ملاحظات",
    language: "EN"
  }
};

function App() {
  const [lang, setLang] = useState(localStorage.getItem("rawabet_lang") || "en");
  const [view, setView] = useState("home");
  const [session, setSession] = useState(null);
  const [me, setMe] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [admin, setAdmin] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [supportThreads, setSupportThreads] = useState([]);
  const [supportTarget, setSupportTarget] = useState("");
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
    const data = await api("/me");
    setSession(data.user);
    setMe(data);
    setJobs(await api("/jobs"));
    if (data.user.role === "admin") {
      setAdmin(await api("/admin/overview"));
      setAdminUsers(await api("/admin/users"));
      setSupportThreads(await api("/admin/support/threads"));
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
      await loadApp();
    } catch (err) {
      setError(err.message);
    }
  }

  function logout() {
    clearToken();
    setSession(null);
    setMe(null);
    setAdmin(null);
    setSupportThreads([]);
  }

  const supportUnread = supportThreads.reduce((sum, thread) => sum + Number(thread.unread_count || 0), 0);

  if (!session) return <Login lang={lang} setLang={setLang} t={t} login={login} error={error} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => setView("home")}>
          <img className="brand-mark" src="/brand/rawabet-mark.png" alt="" />
          <img className="brand-wordmark" src="/brand/rawabet-wordmark.png" alt="Rawabet - روابط تجمعنا" />
        </button>
        <label className="search">
          <span>⌕</span>
          <input placeholder={t("search")} />
        </label>
        <nav className="desktop-nav">
          {[
            ["home", "⌂"],
            ["profile", "◉"],
            ["network", "◎"],
            ["jobs", "▣"]
          ].map(([item, icon]) => <button className={`nav-link ${view === item ? "active" : ""}`} onClick={() => setView(item)} key={item}><span>{icon}</span><b>{t(item)}</b></button>)}
          {session.role === "admin" && <button className={`nav-link ${view === "admin" ? "active" : ""}`} onClick={() => setView("admin")}><span>▥</span><b>{t("admin")}</b></button>}
        </nav>
        <div className="top-actions">
          <button className="icon-button" onClick={() => setLang(lang === "en" ? "ar" : "en")}>{t("language")}</button>
          <button className="secondary-button compact notify-button" onClick={() => setSupportOpen(true)}>{t("support")}{supportUnread > 0 && <span>{supportUnread}</span>}</button>
          <button className="primary-button compact" onClick={() => setBuilderOpen(true)}>{t("completeProfile")}</button>
          <button className="secondary-button compact" onClick={logout}>{t("logout")}</button>
        </div>
      </header>

      <main className={view === "admin" ? "admin-main" : ""}>
        {view === "home" && <Home t={t} me={me} jobs={jobs} setView={setView} openBuilder={() => setBuilderOpen(true)} />}
        {view === "profile" && <Profile t={t} me={me} reload={loadApp} />}
        {view === "network" && <Network t={t} />}
        {view === "jobs" && <Jobs t={t} jobs={jobs} reload={loadApp} />}
        {view === "admin" && session.role === "admin" && <Admin t={t} admin={admin} users={adminUsers} setUsers={setAdminUsers} jobs={jobs} supportThreads={supportThreads} reload={loadApp} openSupport={(userId) => { setSupportTarget(userId || ""); setSupportOpen(true); }} />}
      </main>
      {builderOpen && <ProfileBuilder t={t} me={me} reload={loadApp} close={() => setBuilderOpen(false)} />}
      {supportOpen && <SupportWindow t={t} me={me} users={adminUsers} initialUserId={supportTarget} onUpdate={loadSupportThreads} close={() => { setSupportOpen(false); setSupportTarget(""); }} />}
    </div>
  );
}

function Login({ lang, setLang, t, login, error }) {
  const [email, setEmail] = useState("admin@rawabet.app");
  const [password, setPassword] = useState("admin123");
  return (
    <main className="login-page">
      <section className="login-hero">
        <div className="brand large"><img className="brand-mark" src="/brand/rawabet-mark.png" alt="" /><img className="brand-wordmark" src="/brand/rawabet-wordmark.png" alt="Rawabet - روابط تجمعنا" /></div>
        <h1>{t("welcome")}</h1>
        <p>{t("welcomeBody")}</p>
      </section>
      <form className="login-card" onSubmit={(event) => { event.preventDefault(); login(email, password); }}>
        <button type="button" className="icon-button" onClick={() => setLang(lang === "en" ? "ar" : "en")}>{t("language")}</button>
        <label>{t("email")}<input value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        <label>{t("password")}<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
        {error && <p className="error">{error}</p>}
        <button className="primary-button">{t("login")}</button>
        <div className="demo-actions">
          <button type="button" onClick={() => { setEmail("admin@rawabet.app"); setPassword("admin123"); }}>{t("demoAdmin")}</button>
          <button type="button" onClick={() => { setEmail("loui@rawabet.app"); setPassword("user123"); }}>{t("demoUser")}</button>
        </div>
      </form>
    </main>
  );
}

function Home({ t, me, jobs, setView, openBuilder }) {
  const strength = me.profile?.profile_strength || 64;
  const stats = me.stats || {};
  const applications = me.applications || [];
  return (
    <div className="layout-grid">
      <aside className="profile-rail">
        <section className="profile-card">
          <div className="cover-strip" />
          <div className="avatar-wrap"><Avatar user={me.user} /><span className="online-dot" /></div>
          <h2>{me.user.fullName}</h2>
          <p>{me.user.headline}</p>
          <dl className="quick-stats">
            <div><dt>{t("profileViews")}</dt><dd>{formatNumber(stats.profile_views)}</dd></div>
            <div><dt>{t("connections")}</dt><dd>{formatNumber(stats.connections)}</dd></div>
          </dl>
          <button className="secondary-button" onClick={openBuilder}>{t("editProfile")}</button>
        </section>
        <section className="panel side-panel workspace-panel">
          <h2>{t("workspace")}</h2>
          <button className="panel-link" onClick={() => setView("profile")}><span>↗</span>{t("publicProfile")}</button>
          <button className="panel-link" onClick={() => setView("jobs")}><span>▦</span>{t("savedJobs")}</button>
          <button className="panel-link" onClick={() => setView("network")}><span>◇</span>{t("myNetwork")}</button>
          {me.user.role === "admin" && <button className="panel-link" onClick={() => setView("admin")}><span>▥</span>{t("adminDashboard")}</button>}
        </section>
      </aside>
      <section className="feed">
        <article className="panel post-card">
          <div className="post-head"><div className="company-logo">R</div><div><h2>{t("welcomeTitle")}</h2><p>{t("sub")}</p></div></div>
          <p>{t("welcomeBody")}</p>
          <div className="feature-grid">
            <button className="feature-card" type="button" onClick={openBuilder}><strong>{t("resumeUpload")}</strong><span>{t("resumeUploadBody")}</span></button>
            <button className="feature-card" type="button" onClick={openBuilder}><strong>{t("verifiedCerts")}</strong><span>{t("verifiedCertsBody")}</span></button>
            <button className="feature-card" type="button" onClick={openBuilder}><strong>{t("workTimeline")}</strong><span>{t("workTimelineBody")}</span></button>
          </div>
        </article>
        <article className="panel post-card">
          <div className="post-head"><div className="company-logo accent">✓</div><div>
          <h2>{t("appliedJobs")}</h2>
          <p>{t("whereIApplied")}</p>
          </div></div>
          <div className="job-strip">{applications.length ? applications.slice(0, 4).map((item) => <span key={item.id}>{item.title}</span>) : <span>{t("noAppliedJobs")}</span>}</div>
        </article>
      </section>
      <aside className="insight-rail">
        <section className="panel side-panel strength-panel">
          <h2>{t("profileStrength")}</h2>
          <div className="meter"><span style={{ width: `${strength}%` }} /></div>
          <p>{strength > 82 ? t("strengthGreat") : t("strengthGood")}</p>
        </section>
        <section className="panel side-panel">
          <h2>{t("peopleYouMayKnow")}</h2>
          {["Sara Alami", "Omar Khaled", "Lina Nader"].map((name) => <div className="person-row" key={name}><Avatar user={{ fullName: name }} size="small" /><div><strong>{name}</strong><span>{name === "Sara Alami" ? "UX Lead" : name === "Omar Khaled" ? "Cloud Architect" : "Talent Partner"}</span></div><button>+</button></div>)}
        </section>
      </aside>
    </div>
  );
}

function ProfileBuilder({ t, me, reload, close }) {
  const [form, setForm] = useState({
    fullName: me.user.fullName || "",
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
    await api("/me/profile", {
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
      await api("/me/documents", { method: "POST", body });
      await reload();
    } catch (err) {
      alert(err.message);
    }
  }

  async function uploadAvatar(file) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    await api("/me/avatar", { method: "POST", body });
    await reload();
  }

  async function addExperience() {
    if (!experience.title || !experience.company) return;
    await api("/me/experience", { method: "POST", body: JSON.stringify(experience) });
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
    headline: me.user.headline || "",
    location: me.user.location || "",
    about: me.profile?.about || "",
    skills: (me.profile?.skills || []).join(", ")
  });
  const [experience, setExperience] = useState({ title: "", company: "" });

  async function saveProfile(event) {
    event.preventDefault();
    await api("/me/profile", {
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
      await api("/me/documents", { method: "POST", body });
      await reload();
    } catch (err) {
      alert(err.message);
    }
  }

  async function uploadAvatar(file) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    await api("/me/avatar", { method: "POST", body });
    await reload();
  }

  async function addExperience(event) {
    event.preventDefault();
    await api("/me/experience", { method: "POST", body: JSON.stringify(experience) });
    setExperience({ title: "", company: "" });
    await reload();
  }

  return (
    <div className="profile-page">
      <section className="profile-hero panel">
        <Avatar user={me.user} size="large" />
        <div><h1>{me.user.fullName}</h1><p>{me.user.headline}</p><span>{me.user.location}</span></div>
      </section>
      <form className="panel form-grid" onSubmit={saveProfile}>
        {["fullName", "headline", "location"].map((key) => <label key={key}>{t(key)}<input value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></label>)}
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

function Network({ t }) {
  return <section className="directory-grid">{["Sara Alami", "Omar Khaled", "Lina Nader", "Maya Haddad", "Faisal Noor", "Reem Mansour"].map((name) => <article className="network-card" key={name}><Avatar user={{ fullName: name }} /><h2>{name}</h2><p>{t("network")}</p><button className="secondary-button">Connect</button></article>)}</section>;
}

function Jobs({ t, jobs, reload }) {
  async function apply(jobId) {
    await api(`/jobs/${jobId}/apply`, { method: "POST" });
    await reload();
  }
  return <section className="job-list">{jobs.map((job) => <article className="job-card panel" key={job.id}><div><h2>{job.title}</h2><p>{job.company_name} · {job.location}</p><span>{job.salary_range}</span></div><button className="primary-button" onClick={() => apply(job.id)}>{t("apply")}</button></article>)}</section>;
}

function Admin({ t, admin, users, setUsers, jobs, supportThreads, reload, openSupport }) {
  const [tab, setTab] = useState("overview");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState(null);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [jobForm, setJobForm] = useState({ companyName: "Rawabet Labs", title: "", location: "Remote", type: "Full-time", salaryRange: "", description: "" });
  const [interview, setInterview] = useState({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
  const unreadTotal = supportThreads.reduce((sum, thread) => sum + Number(thread.unread_count || 0), 0);
  const adminTabs = [
    ["overview", t("overview"), "▦"],
    ["users", t("userManagement"), "◎"],
    ["jobs", t("jobManagement"), "▣"],
    ["interviews", t("interviews"), "◌"],
    ["support", t("supportInbox"), "✉"]
  ];
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
        headline: selectedProfile.user.headline,
        location: selectedProfile.user.location,
        role: selectedProfile.user.role,
        plan: selectedProfile.user.plan,
        status: selectedProfile.user.status,
        about: selectedProfile.profile?.about || "",
        skills: typeof selectedProfile.profile?.skills === "string" ? selectedProfile.profile.skills.split(",").map((item) => item.trim()).filter(Boolean) : selectedProfile.profile?.skills || []
      })
    });
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
    await api("/admin/jobs", { method: "POST", body: JSON.stringify(jobForm) });
    setJobForm({ companyName: "Rawabet Labs", title: "", location: "Remote", type: "Full-time", salaryRange: "", description: "" });
    await reload();
  }
  async function scheduleInterview(event) {
    event.preventDefault();
    if (!interview.userId || !interview.scheduledAt) return;
    await api("/admin/interviews", {
      method: "POST",
      body: JSON.stringify({ ...interview, jobId: interview.jobId || null })
    });
    setInterview({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
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
              <Metric label={t("monthlyRevenue")} value={`$${Number(admin.metrics.monthlyRevenue).toLocaleString()}`} />
            </section>
            <section className="admin-layout">
              <article className="panel span-two"><h2>Growth analytics</h2><div className="bar-chart">{admin.growth.map((item) => <div className="bar-group" key={item.month}><span style={{ height: `${Math.min(100, item.users)}%` }} /><small>{item.month}</small></div>)}</div></article>
              <article className="panel"><h2>{t("riskQueue")}</h2><div className="risk-list"><strong>{admin.metrics.pendingDocuments}</strong><span>{t("pendingDocs")}</span></div></article>
            </section>
          </>}

          {tab === "users" && <>
            <section className="panel">
              <div className="section-head"><h2>{t("users")}</h2><input placeholder={t("searchUsers")} value={search} onChange={(e) => searchUsers(e.target.value)} /></div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>{t("users")}</th><th>{t("role")}</th><th>{t("plan")}</th><th>{t("status")}</th><th>{t("attachments")}</th><th>{t("lastActive")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>{users.map((user) => <tr key={user.id}><td><div className="table-user"><Avatar user={user} size="small" /><div><strong>{user.full_name}</strong><span>{user.email}</span></div></div></td><td>{user.role}</td><td>{user.plan}</td><td><span className={`status ${user.status}`}>{user.status}</span></td><td><DocumentLinks t={t} documents={user.documents} avatarUrl={user.avatar_url} compact /></td><td>{new Date(user.last_active_at).toLocaleDateString()}</td><td><select className="action-select" defaultValue="" onChange={(e) => { runUserAction(user, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option><option value="edit">{t("editUser")}</option><option value="verify">{t("verify")}</option><option value="activate">{t("activate")}</option><option value="deactivate">{t("deactivate")}</option><option value="delete">{t("delete")}</option></select></td></tr>)}</tbody>
                </table>
              </div>
            </section>
            {editing && <form className="panel admin-form" onSubmit={saveUser}>
              <h2>{t("editUser")}</h2>
              <input value={editing.full_name || ""} onChange={(e) => setEditing({ ...editing, full_name: e.target.value })} />
              <input value={editing.email || ""} onChange={(e) => setEditing({ ...editing, email: e.target.value })} />
              <input value={editing.headline || ""} onChange={(e) => setEditing({ ...editing, headline: e.target.value })} placeholder={t("headline")} />
              <input value={editing.location || ""} onChange={(e) => setEditing({ ...editing, location: e.target.value })} placeholder={t("location")} />
              <div className="row-fields">
                <select value={editing.role} onChange={(e) => setEditing({ ...editing, role: e.target.value })}><option value="member">member</option><option value="recruiter">recruiter</option><option value="company">company</option><option value="admin">admin</option></select>
                <select value={editing.status} onChange={(e) => setEditing({ ...editing, status: e.target.value })}><option value="active">active</option><option value="verified">verified</option><option value="review">review</option><option value="suspended">suspended</option></select>
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
                <input value={selectedProfile.user.headline || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, headline: e.target.value } })} placeholder={t("headline")} />
                <input value={selectedProfile.user.location || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, location: e.target.value } })} placeholder={t("location")} />
                <input value={selectedProfile.user.plan || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, plan: e.target.value } })} placeholder={t("plan")} />
                <textarea value={selectedProfile.profile?.about || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, profile: { ...(selectedProfile.profile || {}), about: e.target.value } })} placeholder={t("about")} />
                <input value={Array.isArray(selectedProfile.profile?.skills) ? selectedProfile.profile.skills.join(", ") : selectedProfile.profile?.skills || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, profile: { ...(selectedProfile.profile || {}), skills: e.target.value } })} placeholder={t("skills")} />
                <div className="row-fields">
                  <select value={selectedProfile.user.role} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, role: e.target.value } })}><option value="member">member</option><option value="recruiter">recruiter</option><option value="company">company</option><option value="admin">admin</option></select>
                  <select value={selectedProfile.user.status} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, status: e.target.value } })}><option value="active">active</option><option value="verified">verified</option><option value="review">review</option><option value="suspended">suspended</option></select>
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

          {tab === "jobs" && <form className="panel admin-form" onSubmit={addJob}>
            <h2>{t("addJob")}</h2>
            <input placeholder={t("company")} value={jobForm.companyName} onChange={(e) => setJobForm({ ...jobForm, companyName: e.target.value })} />
            <input placeholder={t("title")} value={jobForm.title} onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })} />
            <input placeholder={t("location")} value={jobForm.location} onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })} />
            <input placeholder={t("salary")} value={jobForm.salaryRange} onChange={(e) => setJobForm({ ...jobForm, salaryRange: e.target.value })} />
            <textarea placeholder={t("description")} value={jobForm.description} onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })} />
            <button className="primary-button">{t("addJob")}</button>
          </form>}

          {tab === "interviews" && <form className="panel admin-form" onSubmit={scheduleInterview}>
            <h2>{t("scheduleInterview")}</h2>
            <select value={interview.userId} onChange={(e) => setInterview({ ...interview, userId: e.target.value })}><option value="">{t("users")}</option>{users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}</select>
            <select value={interview.jobId} onChange={(e) => setInterview({ ...interview, jobId: e.target.value })}><option value="">{t("jobs")}</option>{jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}</select>
            <input type="datetime-local" value={interview.scheduledAt} onChange={(e) => setInterview({ ...interview, scheduledAt: e.target.value })} />
            <input placeholder={t("channel")} value={interview.channel} onChange={(e) => setInterview({ ...interview, channel: e.target.value })} />
            <textarea placeholder={t("notes")} value={interview.notes} onChange={(e) => setInterview({ ...interview, notes: e.target.value })} />
            <button className="primary-button">{t("scheduleInterview")}</button>
          </form>}

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

function SupportWindow({ t, me, users, initialUserId = "", onUpdate, close }) {
  const [targetUserId, setTargetUserId] = useState(me.user.role === "admin" ? initialUserId || users[0]?.id || "" : me.user.id);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  async function loadMessages(userId = targetUserId) {
    const query = me.user.role === "admin" && userId ? `?user_id=${userId}` : "";
    setMessages(await api(`/support/messages${query}`));
    await onUpdate?.();
  }
  useEffect(() => {
    if (me.user.role === "admin" && !targetUserId && users[0]?.id) setTargetUserId(users[0].id);
  }, [users.length, targetUserId, me.user.role]);
  useEffect(() => { loadMessages(); }, [targetUserId]);
  async function sendMessage(event) {
    event.preventDefault();
    if (!message.trim()) return;
    await api("/support/messages", { method: "POST", body: JSON.stringify({ message, userId: me.user.role === "admin" ? targetUserId : undefined }) });
    setMessage("");
    await loadMessages();
  }
  return (
    <div className="support-window">
      <header><strong>{t("support")}</strong><button onClick={close}>×</button></header>
      {me.user.role === "admin" && <select value={targetUserId} onChange={(e) => setTargetUserId(e.target.value)}>{users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}</select>}
      <div className="support-messages">
        {messages.map((item) => <p className={`support-bubble ${item.sender_role}`} key={item.id}><strong>{item.sender_role}</strong>{item.message}</p>)}
      </div>
      <form onSubmit={sendMessage}>
        <input placeholder={t("supportMessage")} value={message} onChange={(e) => setMessage(e.target.value)} />
        <button className="primary-button">{t("send")}</button>
      </form>
    </div>
  );
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
  return <article className="metric-card"><span>{label}</span><strong>{value}</strong><small>+12.4%</small></article>;
}

function Avatar({ user, size = "" }) {
  const className = `avatar ${size}`.trim();
  const avatarUrl = user.avatarUrl || user.avatar_url;
  const src = avatarUrl ? assetUrl(avatarUrl) : "";
  if (src) return <img className={className} src={src} alt={user.fullName || "Profile"} />;
  return <div className={className}>{initials(user.fullName || user.full_name)}</div>;
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
  const apiBase = (import.meta.env.VITE_API_URL || "http://localhost:4000/api").replace(/\/api$/, "");
  return `${apiBase}${path}`;
}

createRoot(document.getElementById("root")).render(<App />);
