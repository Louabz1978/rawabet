import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { api, clearToken, getToken, getTokenCreatedAt, setToken } from "./lib/api.js";
import "./styles.css";

const text = {
  en: {
    brand: "Rawabet",
    sub: "Professional Network",
    email: "Email",
    password: "Password",
    repeatPassword: "Repeat password",
    showPassword: "Show password",
    hidePassword: "Hide password",
    passwordsDoNotMatch: "Passwords do not match.",
    login: "Sign in",
    loginSubtitle: "Find jobs, build a verified professional profile, share resumes and skills, and manage your career opportunities in one place.",
    loginTrustOne: "Verified profiles",
    loginTrustTwo: "Job opportunities",
    loginTrustThree: "Resumes and skills",
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
    aboutUs: "About us",
    contactUs: "Contact us",
    contactName: "Name",
    contactSubject: "Subject",
    contactMessage: "Message",
    contactIntro: "Send a question or partnership request to the Rawabet team.",
    contactSuccess: "Your message was sent successfully.",
    aboutTitle: "About Rawabet",
    aboutBodyOne: "Rawabet is a bilingual professional hiring platform built for people and organizations that need verified profiles, resumes, certificates, work history, job applications, interviews, and support in one organized place.",
    aboutBodyTwo: "Professionals can build their profile, upload documents, apply to jobs, answer screening questions, follow application status, and communicate with support. Admins and agents can manage users, jobs, interviews, applications, analytics, and shared candidate profiles.",
    profile: "Profile",
    jobs: "Jobs",
    companies: "Companies",
    backToCompanies: "Back to companies",
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
    welcome: "Future Job is Waiting",
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
    chooseResume: "Choose resume",
    createResumeWithAI: "Create resume with AI",
    smartResume: "Create smart resume",
    smartResumeIntro: "Review and edit the saved resume information from your profile, then download a polished PDF resume.",
    resumeUsesProfile: "Uses saved profile resume fields and work history",
    education: "Education",
    school: "School",
    degree: "Degree",
    field: "Field",
    startYear: "Start year",
    endYear: "End year",
    addEducation: "Add education",
    editEducation: "Edit education",
    certifications: "Certifications",
    tools: "Tools",
    additionalInfo: "Additional information",
    resumeInfo: "Resume information",
    generateResume: "Generate resume PDF",
    courses: "Courses",
    addCourse: "Add course",
    editCourse: "Edit course",
    deleteCourse: "Delete course",
    courseOwner: "Course owner",
    courseAudience: "Course audience",
    adminDefault: "Admin default",
    courseLink: "Course link",
    seeCourse: "See course",
    allUsers: "All users",
    premiumUsers: "Premium users",
    provider: "Provider",
    completionDate: "Completion date",
    agentDirectory: "Agencies",
    searchAgents: "Search agency or agent",
    openAgency: "Open agency",
    agencyName: "Agency name",
    agencyAbout: "Agency about",
    website: "Website",
    backToJobs: "Back to jobs",
    certificate: "Certificate",
    upload: "Upload",
    profilePicture: "Profile picture",
    changePhoto: "Change photo",
    attachments: "Attachments",
    noAttachments: "No attachments yet",
    viewFile: "View file",
    removeAttachment: "Remove",
    downloadResume: "Download resume",
    maxCertificates: "Up to {count} certificates",
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
    current: "Current",
    title: "Title",
    company: "Company",
    type: "Type",
    activeJobs: "Active jobs",
    appliedJobs: "Applied jobs",
    whereIApplied: "Where I applied for",
    noAppliedJobs: "No applications yet",
    appliedOnly: "Applied jobs only",
    allJobs: "All jobs",
    findJob: "Find a job",
    findCompany: "Find a company",
    menu: "Menu",
    companySearch: "Company search",
    allStatuses: "All statuses",
    more: "More",
    upcomingInterviews: "Upcoming interviews",
    clearChat: "Clear chat",
    adminPosts: "Recent Added Jobs",
    noAdminPosts: "No admin posts yet",
    apply: "Apply",
    applyForJob: "Apply for this job",
    adminDashboard: "Admin dashboard",
    totalUsers: "Total users",
    verifiedProfiles: "Verified profiles",
    applications: "Applications",
    agent: "Agent",
    agents: "Agents",
    agentWorkspace: "Agent workspace",
    sharedProfiles: "Shared profiles",
    candidates: "Users",
    scheduledInterviews: "Scheduled interviews",
    agentReports: "Agent reports",
    agentTools: "Agent tools",
    managedApplications: "Managed applications",
    assignedJobs: "Assigned jobs",
    sharedCandidates: "Shared users",
    agentActivity: "Agent activity",
    openProfile: "Profile",
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
    searchApplications: "Search by applicant, job title, company, or job number",
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
    subscriptionPlans: "Subscriptions",
    subscriptionExpires: "Expires",
    subscriptionStatus: "Subscription status",
    renewNow: "Needs renewal",
    expiringSoon: "Expiring soon",
    activeUntil: "Active until",
    noSubscription: "No active subscription",
    premiumPlan: "Premium user",
    agentPlan: "Agent plan",
    premiumPrice: "$7.99 / month",
    agentPrice: "$9.99 / month",
    premiumPlanBody: "For professionals who want stronger visibility, premium profile signals, and access to premium resources.",
    agentPlanBody: "For agencies and companies that want a public company profile, assigned jobs, candidates, interviews, and live user messages.",
    paymentMethod: "Payment method",
    cashPayment: "Cash",
    shamCashPayment: "ShamCash",
    requestPlan: "Request plan",
    planRequests: "Plan requests",
    requestedPlan: "Requested plan",
    approve: "Approve",
    reject: "Reject",
    planRequestSent: "Plan request sent. Admin will review your payment and activate it.",
    saving: "Saving...",
    active: "Active",
    lastActive: "Last active",
    actions: "Actions",
    save: "Save",
    support: "Message",
    supportMessage: "Type a message",
    send: "Send",
    clearingChat: "Clearing...",
    speakLive: "Speak with live support",
    endConversation: "End conversation",
    liveAgentRequest: "I want to speak with live support.",
    liveSupportStarted: "Live support is now connected. Send your message and an admin will reply here.",
    clearFailed: "Could not clear the conversation.",
    editUser: "Edit user",
    addUser: "Add user",
    masterAdmin: "Master admin",
    delete: "Delete",
    verify: "Verify",
    activate: "Activate",
    deactivate: "Deactivate",
    addJob: "Add job",
    editJob: "Edit job",
    deleteJob: "Delete job",
    assignJob: "Assign job",
    assignedAgents: "Assigned agents",
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
    successSaved: "Saved successfully.",
    successCreated: "Created successfully.",
    successUpdated: "Updated successfully.",
    successDeleted: "Deleted successfully.",
    errorTitle: "Something went wrong",
    copyError: "Copy error",
    close: "Close",
    weak: "Weak",
    medium: "Medium",
    strong: "Strong",
    excellent: "Excellent",
    sessionExpiringTitle: "Session expiring",
    sessionExpiringBody: "For security, your session expires after 60 minutes. You will be signed out automatically.",
    stayConnected: "Sign in again",
    agentChat: "Agent chat",
    chatWithAgent: "Chat with agent",
    adminChat: "Admin chat",
    aiAssistant: "AI Assistant",
    message: "Message",
    autoLogoutIn: "Auto logout in",
    signedInElsewhere: "This account was signed in from another device.",
    language: "ع"
  },
  ar: {
    brand: "روابط",
    sub: "شبكة مهنية",
    email: "البريد الإلكتروني",
    password: "كلمة المرور",
    repeatPassword: "تأكيد كلمة المرور",
    showPassword: "إظهار كلمة المرور",
    hidePassword: "إخفاء كلمة المرور",
    passwordsDoNotMatch: "كلمتا المرور غير متطابقتين.",
    login: "تسجيل الدخول",
    loginSubtitle: "ابحث عن الوظائف، وابن ملفا مهنيا موثقا، وشارك سيرتك الذاتية ومهاراتك، وأدر فرصك المهنية في مكان واحد.",
    loginTrustOne: "ملفات موثقة",
    loginTrustTwo: "فرص عمل",
    loginTrustThree: "سير ومهارات",
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
    aboutUs: "من نحن",
    contactUs: "تواصل معنا",
    contactName: "الاسم",
    contactSubject: "الموضوع",
    contactMessage: "الرسالة",
    contactIntro: "أرسل سؤالا أو طلب تعاون إلى فريق روابط.",
    contactSuccess: "تم إرسال رسالتك بنجاح.",
    aboutTitle: "من نحن",
    aboutBodyOne: "روابط منصة توظيف مهنية ثنائية اللغة تساعد الأفراد والجهات على إدارة الملفات الموثقة والسير الذاتية والشهادات والخبرات وطلبات التقديم والمقابلات والدعم في مكان واحد منظم.",
    aboutBodyTwo: "يمكن للمهنيين بناء ملفاتهم ورفع المستندات والتقديم على الوظائف والإجابة عن أسئلة التقديم ومتابعة حالة الطلب والتواصل مع الدعم. كما تساعد الإدارة والوكلاء على إدارة المستخدمين والوظائف والمقابلات والطلبات والتحليلات والمرشحين المشاركين.",
    profile: "الملف",
    jobs: "الوظائف",
    companies: "الشركات",
    backToCompanies: "العودة للشركات",
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
    welcome: "وظيفة المستقبل بانتظارك",
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
    chooseResume: "اختر السيرة الذاتية",
    createResumeWithAI: "إنشاء سيرة بالذكاء الاصطناعي",
    smartResume: "إنشاء سيرة ذكية",
    smartResumeIntro: "راجع وعدّل بيانات السيرة المحفوظة في ملفك، ثم حمّل ملف PDF احترافي.",
    resumeUsesProfile: "يستخدم حقول السيرة المحفوظة وتاريخ العمل",
    education: "التعليم",
    school: "الجامعة أو المدرسة",
    degree: "الشهادة",
    field: "التخصص",
    startYear: "سنة البداية",
    endYear: "سنة النهاية",
    addEducation: "إضافة تعليم",
    editEducation: "تعديل التعليم",
    certifications: "الشهادات",
    tools: "الأدوات",
    additionalInfo: "معلومات إضافية",
    resumeInfo: "معلومات السيرة",
    generateResume: "إنشاء PDF للسيرة",
    courses: "الدورات",
    addCourse: "إضافة دورة",
    editCourse: "تعديل الدورة",
    deleteCourse: "حذف الدورة",
    courseOwner: "مالك الدورة",
    courseAudience: "جمهور الدورة",
    adminDefault: "الإدارة الافتراضية",
    courseLink: "رابط الدورة",
    seeCourse: "شاهد الدورة",
    allUsers: "الجميع",
    premiumUsers: "المستخدمون المميزون",
    provider: "الجهة المقدمة",
    completionDate: "تاريخ الإكمال",
    agentDirectory: "الجهات",
    searchAgents: "ابحث عن جهة أو وكيل",
    openAgency: "فتح الجهة",
    agencyName: "اسم الجهة",
    agencyAbout: "نبذة عن الجهة",
    website: "الموقع الإلكتروني",
    backToJobs: "العودة للوظائف",
    certificate: "الشهادة",
    upload: "رفع",
    profilePicture: "الصورة الشخصية",
    changePhoto: "تغيير الصورة",
    attachments: "المرفقات",
    noAttachments: "لا توجد مرفقات بعد",
    viewFile: "عرض الملف",
    removeAttachment: "حذف",
    downloadResume: "تحميل السيرة",
    maxCertificates: "حتى {count} شهادات",
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
    current: "حالي",
    title: "المسمى",
    company: "الشركة",
    type: "النوع",
    activeJobs: "الوظائف النشطة",
    appliedJobs: "الوظائف المقدمة",
    whereIApplied: "الوظائف التي تقدمت إليها",
    noAppliedJobs: "لا توجد طلبات بعد",
    appliedOnly: "الوظائف المقدمة فقط",
    allJobs: "كل الوظائف",
    findJob: "ابحث عن وظيفة",
    findCompany: "ابحث عن شركة",
    menu: "القائمة",
    companySearch: "البحث باسم الشركة",
    allStatuses: "كل الحالات",
    more: "المزيد",
    upcomingInterviews: "المقابلات القادمة",
    clearChat: "مسح المحادثة",
    adminPosts: "أحدث الوظائف المضافة",
    noAdminPosts: "لا توجد منشورات من الإدارة بعد",
    apply: "تقديم",
    applyForJob: "التقديم على هذه الوظيفة",
    adminDashboard: "لوحة تحكم الإدارة",
    totalUsers: "إجمالي المستخدمين",
    verifiedProfiles: "الملفات الموثقة",
    applications: "طلبات التقديم",
    agent: "وكيل",
    agents: "الوكلاء",
    agentWorkspace: "مساحة الوكيل",
    sharedProfiles: "الملفات المشاركة",
    candidates: "المستخدمون",
    scheduledInterviews: "المقابلات المجدولة",
    agentReports: "تقارير الوكيل",
    agentTools: "أدوات الوكيل",
    managedApplications: "طلبات تحت المتابعة",
    assignedJobs: "الوظائف المعينة",
    sharedCandidates: "المستخدمون المشاركون",
    agentActivity: "نشاط الوكيل",
    openProfile: "الملف",
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
    searchApplications: "ابحث باسم المتقدم أو الوظيفة أو الشركة أو رقم الوظيفة",
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
    subscriptionPlans: "الاشتراك",
    subscriptionExpires: "ينتهي في",
    subscriptionStatus: "حالة الاشتراك",
    renewNow: "بحاجة إلى تجديد",
    expiringSoon: "ينتهي قريبا",
    activeUntil: "نشط حتى",
    noSubscription: "لا يوجد اشتراك نشط",
    premiumPlan: "مستخدم مميز",
    agentPlan: "خطة الوكيل",
    premiumPrice: "7.99$ / شهريا",
    agentPrice: "9.99$ / شهريا",
    premiumPlanBody: "للمهنيين الذين يريدون ظهورا أقوى، إشارة حساب مميز، والوصول إلى موارد مخصصة للمميزين.",
    agentPlanBody: "للجهات والشركات التي تريد ملف شركة عام، وظائف مرتبطة بها، مرشحين، مقابلات، ومراسلة مباشرة مع المستخدمين.",
    paymentMethod: "طريقة الدفع",
    cashPayment: "كاش",
    shamCashPayment: "شام كاش",
    requestPlan: "طلب الخطة",
    planRequests: "طلبات الاشتراك",
    requestedPlan: "الخطة المطلوبة",
    approve: "قبول",
    reject: "رفض",
    planRequestSent: "تم إرسال طلب الخطة. ستراجع الإدارة الدفع وتفعّلها.",
    saving: "جار الحفظ...",
    active: "نشط",
    lastActive: "آخر نشاط",
    actions: "الإجراءات",
    save: "حفظ",
    support: "رسالة",
    supportMessage: "اكتب رسالة",
    send: "إرسال",
    clearingChat: "جار المسح...",
    speakLive: "التحدث مع دعم مباشر",
    endConversation: "إنهاء المحادثة",
    liveAgentRequest: "أريد التحدث مع موظف دعم مباشر.",
    liveSupportStarted: "تم تحويلك إلى الدعم المباشر. اكتب رسالتك وسيقوم المدير بالرد هنا.",
    clearFailed: "تعذر مسح المحادثة.",
    editUser: "تعديل المعلومات",
    addUser: "إضافة مستخدم",
    masterAdmin: "المدير الرئيسي",
    delete: "حذف",
    verify: "توثيق",
    activate: "تفعيل",
    deactivate: "إيقاف",
    addJob: "إضافة وظيفة",
    editJob: "تعديل الوظيفة",
    deleteJob: "حذف الوظيفة",
    assignJob: "تعيين الوظيفة",
    assignedAgents: "الوكلاء المعينون",
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
    successSaved: "تم الحفظ بنجاح.",
    successCreated: "تمت الإضافة بنجاح.",
    successUpdated: "تم التحديث بنجاح.",
    successDeleted: "تم الحذف بنجاح.",
    errorTitle: "حدث خطأ",
    copyError: "نسخ الخطأ",
    close: "إغلاق",
    weak: "ضعيف",
    medium: "متوسط",
    strong: "قوي",
    excellent: "ممتاز",
    sessionExpiringTitle: "ستنتهي الجلسة",
    sessionExpiringBody: "لأمان الحساب، تنتهي الجلسة بعد 60 دقيقة وسيتم تسجيل خروجك تلقائيا.",
    stayConnected: "تسجيل الدخول من جديد",
    agentChat: "محادثة الوكيل",
    chatWithAgent: "تواصل مع الوكيل",
    adminChat: "محادثة الإدارة",
    aiAssistant: "المساعد الذكي",
    message: "رسالة",
    autoLogoutIn: "تسجيل خروج تلقائي خلال",
    signedInElsewhere: "تم تسجيل الدخول إلى هذا الحساب من جهاز آخر.",
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
  pending: { en: "Pending", ar: "معلق" },
  approved: { en: "Approved", ar: "مقبول" },
  cancelled: { en: "Cancelled", ar: "ملغى" },
  paused: { en: "Paused", ar: "متوقف" },
  closed: { en: "Closed", ar: "مغلق" }
};

const APPLICATION_STATUSES = ["submitted", "review", "interview", "accepted", "rejected"];
const INTERVIEW_OUTCOME_STATUSES = ["accepted", "rejected"];
const USER_STATUSES = ["active", "verified", "review", "suspended"];
const JOB_STATUSES = ["active", "paused", "closed"];
const PLAN_OPTIONS = ["free", "premium"];
const USER_ROLES = ["member", "agent", "admin", "master_admin"];
const API_URL = import.meta.env.VITE_API_URL || "/api";
const SESSION_MS = 60 * 60 * 1000;
const SESSION_WARNING_MS = 58 * 60 * 1000;
const SESSION_GRACE_MS = 2 * 60 * 1000;
const SESSION_VALIDATE_MS = 5 * 1000;
const PAGE_SIZE = 15;

function isStaleSessionError(error) {
  return Boolean(error?.staleSession);
}

function isSessionError(error) {
  const message = String(error?.message || error || "");
  return Boolean(error?.isSessionError) || message.includes("another device") || message.includes("Invalid session");
}

function statusLabel(value, lang) {
  return STATUS_LABELS[value]?.[lang] || value || "-";
}

function pageItems(items, page, pageSize = PAGE_SIZE) {
  return items.slice((page - 1) * pageSize, page * pageSize);
}

function PaginationControls({ t, page, total, setPage, pageSize = PAGE_SIZE }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if (total <= pageSize) return null;
  return (
    <div className="pagination panel">
      <button className="secondary-button compact" type="button" disabled={page <= 1} onClick={() => setPage(page - 1)}>{t("previous")}</button>
      <span>{t("page")} {page} / {totalPages}</span>
      <button className="secondary-button compact" type="button" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>{t("next")}</button>
    </div>
  );
}

function analyticsLabel(kind, value, lang, t) {
  const raw = String(value || "").trim();
  const normalized = normalizeStatusValue(raw);
  if (kind === "application") {
    if (raw.toLowerCase() === "approved") return STATUS_LABELS.accepted[lang];
    return STATUS_LABELS[normalized]?.[lang] || raw || "-";
  }
  if (kind === "category") return jobCategoryLabel(raw, lang);
  if (kind === "profile") {
    const profileLabels = {
      excellent: t("excellent"),
      strong: t("strong"),
      medium: t("medium"),
      weak: t("weak")
    };
    return profileLabels[raw.toLowerCase()] || raw || "-";
  }
  return raw || "-";
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

function subscriptionInfo(user = {}, t) {
  const expiresRaw = user.subscriptionExpiresAt || user.subscription_expires_at || "";
  const expiresAt = expiresRaw ? new Date(expiresRaw) : null;
  const isValidDate = expiresAt && !Number.isNaN(expiresAt.getTime());
  const now = new Date();
  const daysLeft = isValidDate ? Math.ceil((expiresAt.getTime() - now.getTime()) / 86400000) : null;
  if (user.plan !== "premium") {
    if (isValidDate && daysLeft <= 0) {
      return { state: "expired", label: t("renewNow"), detail: `${t("subscriptionExpires")}: ${expiresAt.toLocaleDateString()}` };
    }
    return { state: "free", label: t("noSubscription"), detail: "" };
  }
  if (!isValidDate) return { state: "active", label: t("active"), detail: "" };
  if (daysLeft <= 0) return { state: "expired", label: t("renewNow"), detail: `${t("subscriptionExpires")}: ${expiresAt.toLocaleDateString()}` };
  if (daysLeft <= 7) return { state: "soon", label: t("expiringSoon"), detail: `${t("activeUntil")}: ${expiresAt.toLocaleDateString()}` };
  return { state: "active", label: t("active"), detail: `${t("activeUntil")}: ${expiresAt.toLocaleDateString()}` };
}

function roleLabel(value, lang) {
  const labels = {
    member: { en: "User", ar: "مستخدم" },
    agent: { en: "Agent", ar: "وكيل" },
    admin: { en: "Admin", ar: "مدير" },
    master_admin: { en: "Master admin", ar: "مدير رئيسي" }
  };
  return labels[value]?.[lang] || value || "-";
}

function questionsFromText(value = "") {
  return String(value).split("\n").map((item) => item.trim()).filter(Boolean);
}

function questionsToText(value = []) {
  return Array.isArray(value) ? value.join("\n") : "";
}

function questionsToArray(value = []) {
  if (Array.isArray(value)) return value.length ? value.map((item) => String(item || "")) : [""];
  const rows = questionsFromText(value);
  return rows.length ? rows : [""];
}

function compactQuestions(value = []) {
  return questionsToArray(value).map((item) => item.trim()).filter(Boolean);
}

function profileStrengthStatus(strength, t) {
  if (strength >= 85) return { label: t("excellent"), body: t("strengthGreat") };
  if (strength >= 70) return { label: t("strong"), body: t("strengthGood") };
  if (strength >= 40) return { label: t("medium"), body: t("strengthNeedsWork") };
  return { label: t("weak"), body: t("strengthNeedsWork") };
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
  const [adminCourses, setAdminCourses] = useState([]);
  const [adminSubscriptionRequests, setAdminSubscriptionRequests] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentShares, setAgentShares] = useState([]);
  const [agentInterviews, setAgentInterviews] = useState([]);
  const [agentJobs, setAgentJobs] = useState([]);
  const [agentUsers, setAgentUsers] = useState([]);
  const [supportThreads, setSupportThreads] = useState([]);
  const [userAgentThreads, setUserAgentThreads] = useState([]);
  const [supportTarget, setSupportTarget] = useState("");
  const [adminStartTab, setAdminStartTab] = useState("");
  const [jobSearch, setJobSearch] = useState("");
  const [selectedJobId, setSelectedJobId] = useState("");
  const [jobMode, setJobMode] = useState("all");
  const [error, setError] = useState("");
  const [builderOpen, setBuilderOpen] = useState(false);
  const [supportOpen, setSupportOpen] = useState(false);
  const [agentChatOpen, setAgentChatOpen] = useState(false);
  const [agentChatTarget, setAgentChatTarget] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [subscriptionMenuOpen, setSubscriptionMenuOpen] = useState(false);
  const [popup, setPopup] = useState(null);
  const [presenceTick, setPresenceTick] = useState(0);
  const [sessionWarningOpen, setSessionWarningOpen] = useState(false);
  const [sessionCountdown, setSessionCountdown] = useState(SESSION_GRACE_MS / 1000);
  const supportUnreadRef = useRef(0);
  const supportUnreadReadyRef = useRef(false);
  const userAgentUnreadRef = useRef(0);
  const userAgentUnreadReadyRef = useRef(false);
  const presenceBusyRef = useRef(false);
  const presenceListsBusyRef = useRef(false);
  const sessionEndedRef = useRef(false);
  const t = (key) => text[lang][key] || key;
  const isAdminRole = (role) => ["admin", "master_admin"].includes(role);

  function notify(message, type = "success", details = "") {
    setPopup({ message, type, details: details || message, id: Date.now() });
  }

  async function withNotify(task, successMessage = "") {
    try {
      const result = await task();
      if (successMessage) notify(successMessage, "success");
      return result;
    } catch (err) {
      if (isStaleSessionError(err)) return null;
      notify(err.message || String(err), "error", err.stack || err.message || String(err));
      throw err;
    }
  }

  useEffect(() => {
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = lang;
    localStorage.setItem("rawabet_lang", lang);
  }, [lang]);

  useEffect(() => {
    const onUnhandledRejection = (event) => {
      const reason = event.reason;
      if (isStaleSessionError(reason)) {
        event.preventDefault?.();
        return;
      }
      notify(reason?.message || String(reason || "Unexpected error"), "error", reason?.stack || reason?.message || String(reason || ""));
    };
    const onError = (event) => {
      notify(event.message || "Unexpected error", "error", event.error?.stack || event.message || "");
    };
    window.addEventListener("unhandledrejection", onUnhandledRejection);
    window.addEventListener("error", onError);
    return () => {
      window.removeEventListener("unhandledrejection", onUnhandledRejection);
      window.removeEventListener("error", onError);
    };
  }, []);

  async function loadApp() {
    const data = await api("/account");
    setMe(data);
    setSession(data.user);
    if (isAdminRole(data.user.role)) {
      try {
        setJobs(await api("/admin/jobs"));
      } catch {
        setJobs(await api("/jobs"));
      }
      setAgents(await api("/agents"));
    } else if (data.user.role === "agent") {
      setJobs([]);
      setView("agent");
    } else {
      setJobs(await api("/jobs"));
      setAgents(await api("/agents"));
      const threads = await api("/user/agent-chat/threads");
      userAgentUnreadRef.current = threads.reduce((sum, thread) => sum + Number(thread.unread_count || 0), 0);
      userAgentUnreadReadyRef.current = true;
      setUserAgentThreads(threads);
    }
    if (isAdminRole(data.user.role)) {
      setAdmin(await api("/admin/overview"));
      setAdminUsers(await api("/admin/users"));
      setAdminApplications(await api("/admin/applications"));
      setAdminInterviews(await api("/admin/interviews"));
      setAdminCourses(await api("/admin/courses"));
      setAdminSubscriptionRequests(await api("/admin/subscription-requests"));
      const threads = await api("/admin/support/threads");
      supportUnreadRef.current = threads.filter((thread) => Number(thread.unread_count || 0) > 0).length;
      supportUnreadReadyRef.current = true;
      setSupportThreads(threads);
    }
    if (data.user.role === "agent") {
      setAgentShares(await api("/agent/shares"));
      setAgentInterviews(await api("/agent/interviews"));
      setAgentJobs(await api("/agent/jobs"));
      setAgentUsers(await api("/agent/users"));
    }
    return data.user;
  }

  async function loadSupportThreads() {
    if (isAdminRole(session?.role)) {
      const threads = await api("/admin/support/threads");
      const nextUnread = threads.filter((thread) => Number(thread.unread_count || 0) > 0).length;
      if (supportUnreadReadyRef.current && nextUnread > supportUnreadRef.current) playNotificationBeep();
      supportUnreadRef.current = nextUnread;
      supportUnreadReadyRef.current = true;
      setSupportThreads(threads);
    }
  }

  async function touchPresence() {
    if (!session || presenceBusyRef.current) return;
    presenceBusyRef.current = true;
    try {
      const data = await api("/account/presence", { method: "POST" });
      setMe((current) => current ? { ...current, user: { ...current.user, ...(data.user || {}) } } : current);
      setSession((current) => current ? { ...current, ...(data.user || {}) } : current);
    } catch (err) {
      if (isSessionEndedError(err)) {
        handleSessionEnded(err.message);
        return;
      }
      throw err;
    } finally {
      presenceBusyRef.current = false;
    }
  }

  function isSessionEndedError(err) {
    return !isStaleSessionError(err) && isSessionError(err);
  }

  function handleSessionEnded(message) {
    if (sessionEndedRef.current) return;
    sessionEndedRef.current = true;
    if (String(message || "").includes("another device")) {
      notify(message || t("signedInElsewhere"), "error", message || t("signedInElsewhere"));
    }
    logout();
  }

  async function refreshPresenceLists() {
    if (!session || presenceListsBusyRef.current) return;
    presenceListsBusyRef.current = true;
    try {
      if (isAdminRole(session.role)) {
        setAdminApplications(await api("/admin/applications"));
        const threads = await api("/admin/support/threads");
        const nextUnread = threads.filter((thread) => Number(thread.unread_count || 0) > 0).length;
        if (supportUnreadReadyRef.current && nextUnread > supportUnreadRef.current) playNotificationBeep();
        supportUnreadRef.current = nextUnread;
        supportUnreadReadyRef.current = true;
        setSupportThreads(threads);
      } else if (session.role === "agent") {
        setAgentShares(await api("/agent/shares"));
        setAgentInterviews(await api("/agent/interviews"));
        setAgentUsers(await api("/agent/users"));
      } else {
        setAgents(await api("/agents"));
        const threads = await api("/user/agent-chat/threads");
        const nextUnread = threads.reduce((sum, thread) => sum + Number(thread.unread_count || 0), 0);
        if (userAgentUnreadReadyRef.current && nextUnread > userAgentUnreadRef.current) playNotificationBeep();
        userAgentUnreadRef.current = nextUnread;
        userAgentUnreadReadyRef.current = true;
        setUserAgentThreads(threads);
      }
    } finally {
      presenceListsBusyRef.current = false;
    }
  }

  async function stayConnected() {
    logout();
  }

  useEffect(() => {
    if (localStorage.getItem("rawabet_token")) {
      if (!getTokenCreatedAt()) localStorage.setItem("rawabet_token_created_at", String(Date.now()));
      loadApp().catch(() => clearToken());
    }
  }, []);

  useEffect(() => {
    const onSessionEnded = (event) => {
      handleSessionEnded(event.detail || t("signedInElsewhere"));
    };
    window.addEventListener("rawabet:session-ended", onSessionEnded);
    return () => window.removeEventListener("rawabet:session-ended", onSessionEnded);
  }, []);

  useEffect(() => {
    if (!isAdminRole(session?.role)) return undefined;
    const timer = setInterval(() => loadSupportThreads().catch(() => {}), 12000);
    return () => clearInterval(timer);
  }, [session?.role]);

  useEffect(() => {
    if (!session) return undefined;
    touchPresence().catch(() => {});
    refreshPresenceLists().catch(() => {});
    const heartbeat = setInterval(() => touchPresence().catch(() => {}), SESSION_VALIDATE_MS);
    const listRefresh = setInterval(() => refreshPresenceLists().catch(() => {}), 8000);
    const visualTick = setInterval(() => setPresenceTick((tick) => tick + 1), 15000);
    const activeEvents = ["focus", "click", "keydown", "mousemove", "touchstart"];
    const onActivity = () => touchPresence().catch(() => {});
    activeEvents.forEach((eventName) => window.addEventListener(eventName, onActivity, { passive: true }));
    return () => {
      clearInterval(heartbeat);
      clearInterval(listRefresh);
      clearInterval(visualTick);
      activeEvents.forEach((eventName) => window.removeEventListener(eventName, onActivity));
    };
  }, [session?.id, session?.role]);

  useEffect(() => {
    if (!session) return undefined;
    const timer = setInterval(() => {
      const createdAt = getTokenCreatedAt();
      if (!createdAt) return;
      const age = Date.now() - createdAt;
      if (age >= SESSION_MS) {
        logout();
        return;
      }
      if (age >= SESSION_WARNING_MS) {
        setSessionWarningOpen(true);
        setSessionCountdown(Math.max(0, Math.ceil((SESSION_MS - age) / 1000)));
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [session?.id]);

  async function login(email, password) {
    setError("");
    try {
      const data = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      if (data.mfaRequired) return data;
      setToken(data.token);
      sessionEndedRef.current = false;
      try {
        const loadedUser = await loadApp();
        setView(loadedUser.role === "agent" ? "agent" : "home");
      } catch (loadError) {
        clearToken();
        setSession(null);
        setMe(null);
        throw loadError;
      }
    } catch (err) {
      setError(err.message);
      return null;
    }
  }

  async function verifyAndLoad(token) {
    setToken(token);
    sessionEndedRef.current = false;
    try {
      const loadedUser = await loadApp();
      setView(loadedUser.role === "agent" ? "agent" : "home");
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
    setAdminCourses([]);
    setAgents([]);
    setSelectedAgent(null);
    setAgentShares([]);
    setAgentInterviews([]);
    setAgentJobs([]);
    setAgentUsers([]);
    setSupportThreads([]);
    setUserAgentThreads([]);
    setSubscriptionMenuOpen(false);
    supportUnreadRef.current = 0;
    supportUnreadReadyRef.current = false;
    userAgentUnreadRef.current = 0;
    userAgentUnreadReadyRef.current = false;
    setMobileMenuOpen(false);
    setSessionWarningOpen(false);
    setSessionCountdown(SESSION_GRACE_MS / 1000);
  }

  const supportUnread = supportThreads.filter((thread) => Number(thread.unread_count || 0) > 0).length;
  const userAgentUnread = userAgentThreads.reduce((sum, thread) => sum + Number(thread.unread_count || 0), 0);

  function openJob(jobId) {
    setJobMode("all");
    setSelectedJobId(jobId);
    setJobSearch("");
    setView("allJobs");
  }

  function openAppliedJobs() {
    setJobMode("applied");
    setSelectedJobId("");
    setJobSearch("");
    setView("appliedJobs");
    setMobileMenuOpen(false);
  }

  function openAllJobs() {
    setJobMode("all");
    setSelectedJobId("");
    setView("allJobs");
    setMobileMenuOpen(false);
  }

  function openComingInterviews() {
    setSelectedJobId("");
    setView("interviews");
    setMobileMenuOpen(false);
  }

  function openSmartResume() {
    setSelectedJobId("");
    setView("smartResume");
    setMobileMenuOpen(false);
  }

  if (!session || !me) return <Login lang={lang} setLang={setLang} t={t} login={login} verifyAndLoad={verifyAndLoad} error={error} setError={setError} />;
  const isAgent = session.role === "agent";
  const subscriptionActive = !me.user.subscriptionExpiresAt || new Date(me.user.subscriptionExpiresAt) > new Date();
  const canUseSmartResume = !isAgent && !isAdminRole(session.role) && me.user.plan === "premium" && subscriptionActive;

  function openSmartResumeForUser() {
    if (!canUseSmartResume) return;
    openSmartResume();
  }

  function openAgentChat(agent = null) {
    const target = agent || userAgentThreads[0] || null;
    if (!target) return;
    setAgentChatTarget(target);
    setAgentChatOpen(true);
  }

  return (
    <div className="app-shell">
      <header className={`topbar ${isAgent ? "agent-topbar" : ""}`}>
        <button className="icon-button mobile-menu-button" type="button" aria-label={t("menu")} onClick={() => setMobileMenuOpen((current) => !current)}>☰</button>
        <button className="brand" onClick={() => setView(isAgent ? "agent" : "home")}>
          <img className="brand-mark" src="/brand/rawabet-mark.png" alt="" />
          <img className="brand-wordmark" src="/brand/rawabet-wordmark.png" alt="Rawabet - روابط تجمعنا" />
        </button>
        {!isAgent && <label className="search">
          <span>⌕</span>
          <input placeholder={t("search")} value={jobSearch} onChange={(event) => { setJobMode("all"); setJobSearch(event.target.value); setView("allJobs"); }} />
        </label>}
        <nav className="desktop-nav">
          {!isAgent && [
            ["home", "home"],
            ["profile", "profile"],
            ["jobs", "jobs"],
            ["agents", "agents", "companies"]
          ].map(([item, icon, label]) => <button className={`nav-link ${view === item ? "active" : ""}`} onClick={() => setView(item)} key={item}><span><NavIcon name={icon} /></span><b>{t(label || item)}</b></button>)}
          {isAdminRole(session.role) && <button className={`nav-link ${view === "admin" ? "active" : ""}`} onClick={() => setView("admin")}><span><NavIcon name="admin" /></span><b>{t("admin")}</b></button>}
          {isAgent && <button className="nav-link active" onClick={() => setView("agent")}><span><NavIcon name="agents" /></span><b>{t("agentWorkspace")}</b></button>}
        </nav>
        <div className="top-actions">
          {!isAgent && <button className="icon-button mobile-chat-button" type="button" aria-label={isAdminRole(session.role) ? t("support") : t("message")} onClick={() => isAdminRole(session.role) ? (setAdminStartTab("support"), setView("admin")) : openAgentChat()} disabled={!isAdminRole(session.role) && !userAgentThreads.length}>💬{(isAdminRole(session.role) ? supportUnread : userAgentUnread) > 0 && <span>{isAdminRole(session.role) ? supportUnread : userAgentUnread}</span>}</button>}
          {isAgent && <button className="icon-button mobile-chat-button" type="button" aria-label={t("agentChat")} onClick={() => setView("agent-chat")}>💬</button>}
          {!isAgent && <button className="secondary-button compact notify-button message-button" onClick={() => isAdminRole(session.role) ? (setAdminStartTab("support"), setView("admin")) : openAgentChat()} disabled={!isAdminRole(session.role) && !userAgentThreads.length}>{isAdminRole(session.role) ? t("support") : t("message")}{(isAdminRole(session.role) ? supportUnread : userAgentUnread) > 0 && <span>{isAdminRole(session.role) ? supportUnread : userAgentUnread}</span>}</button>}
          {isAgent && <button className="secondary-button compact notify-button" onClick={() => setView("agent-chat")}>{t("agentChat")}</button>}
          {isAgent && <button className="secondary-button compact notify-button" onClick={() => setSupportOpen(true)}>{t("adminChat")}</button>}
          <button className="secondary-button compact" onClick={logout}>{t("logout")}</button>
          <button className="icon-button" onClick={() => setLang(lang === "en" ? "ar" : "en")}>{t("language")}</button>
        </div>
      </header>
      {mobileMenuOpen && <nav className="mobile-drawer-menu" aria-label={t("menu")}>
        {isAdminRole(session.role) && <button type="button" onClick={() => { setView("admin"); setMobileMenuOpen(false); }}>{t("adminDashboard")}</button>}
        {isAgent && <button type="button" onClick={() => { setView("agent"); setMobileMenuOpen(false); }}>{t("agentWorkspace")}</button>}
        {isAgent && <button type="button" onClick={() => { setView("agent-jobs"); setMobileMenuOpen(false); }}>{t("assignedJobs")}</button>}
        {isAgent && <button type="button" onClick={() => { setView("agent-users"); setMobileMenuOpen(false); }}>{t("users")}</button>}
        {isAgent && <button type="button" onClick={() => { setView("agent-chat"); setMobileMenuOpen(false); }}>{t("agentChat")}</button>}
        {isAgent && <button type="button" onClick={() => { setSupportOpen(true); setMobileMenuOpen(false); }}>{t("adminChat")}</button>}
        {!isAgent && <button type="button" onClick={openAppliedJobs}><span>{t("appliedJobs")}</span><b>{formatNumber(me.applications?.length || 0)}</b></button>}
        {!isAgent && <button type="button" onClick={openAllJobs}>{t("findJob")}</button>}
        {!isAgent && <button type="button" onClick={() => { setView("agents"); setMobileMenuOpen(false); }}>{t("findCompany")}</button>}
        {canUseSmartResume && <button type="button" onClick={openSmartResumeForUser}>{t("smartResume")}</button>}
        {!isAgent && <button type="button" onClick={openComingInterviews}>{t("upcomingInterviews")}</button>}
        {!isAdminRole(session.role) && <button type="button" onClick={() => setSubscriptionMenuOpen((current) => !current)}><span>{t("subscriptionPlans")}</span><b>{subscriptionMenuOpen ? "−" : "+"}</b></button>}
        {subscriptionMenuOpen && !isAdminRole(session.role) && <PlanCards t={t} currentRole={session.role} currentPlan={me.user.plan} subscriptionExpiresAt={me.user.subscriptionExpiresAt} notify={notify} menuMode />}
        <button type="button" onClick={logout}>{t("logout")}</button>
      </nav>}

      <main className={view === "admin" || isAgent ? "admin-main" : ""}>
        {isAgent ? <AgentWorkspace t={t} lang={lang} agent={me.user} profile={me.profile || {}} shares={agentShares} users={agentUsers} interviews={agentInterviews} jobs={agentJobs} view={view} setView={setView} reload={loadApp} notify={notify} openAgentChat={openAgentChat} openAdminChat={() => setSupportOpen(true)} /> : <>
          {view === "home" && <Home t={t} lang={lang} me={me} jobs={jobs} agents={agents} setSelectedAgent={setSelectedAgent} setView={setView} openJob={openJob} openAppliedJobs={openAppliedJobs} openBuilder={() => setBuilderOpen(true)} openSmartResume={openSmartResumeForUser} openSupportAssistant={() => setSupportOpen(true)} canUseSmartResume={canUseSmartResume} jobSearch={jobSearch} setJobSearch={setJobSearch} setJobMode={setJobMode} notify={notify} />}
          {view === "profile" && <Profile t={t} me={me} reload={loadApp} notify={notify} />}
          {view === "smartResume" && canUseSmartResume && <SmartResumePage t={t} me={me} reload={loadApp} notify={notify} />}
          {view === "courses" && <CoursesPage t={t} courses={me.courses || []} />}
          {view === "agents" && <AgentsPage t={t} agents={agents} selectedAgent={selectedAgent} setSelectedAgent={setSelectedAgent} openJob={openJob} openAgentChat={openAgentChat} />}
          {view === "jobs" && <Jobs t={t} lang={lang} jobs={jobs} documents={me.documents || []} applications={me.applications || []} interviews={me.interviews || []} search={jobSearch} mode={jobMode} setMode={setJobMode} selectedJobId={selectedJobId} clearSelectedJob={() => setSelectedJobId("")} reload={loadApp} />}
          {view === "allJobs" && <Jobs t={t} lang={lang} jobs={jobs} documents={me.documents || []} applications={me.applications || []} interviews={me.interviews || []} search={jobSearch} mode="all" setMode={(mode) => mode === "applied" ? openAppliedJobs() : openAllJobs()} selectedJobId={selectedJobId} clearSelectedJob={() => setSelectedJobId("")} reload={loadApp} />}
          {view === "appliedJobs" && <Jobs t={t} lang={lang} jobs={jobs} documents={me.documents || []} applications={me.applications || []} interviews={me.interviews || []} search={jobSearch} mode="applied" setMode={(mode) => mode === "all" ? openAllJobs() : openAppliedJobs()} selectedJobId={selectedJobId} clearSelectedJob={() => setSelectedJobId("")} reload={loadApp} />}
          {view === "interviews" && <ComingInterviews t={t} interviews={me.interviews || []} openJob={openJob} />}
          {view === "admin" && isAdminRole(session.role) && <Admin t={t} lang={lang} session={session} admin={admin} users={adminUsers} setUsers={setAdminUsers} jobs={jobs} courses={adminCourses} applications={adminApplications} setApplications={setAdminApplications} interviews={adminInterviews} subscriptionRequests={adminSubscriptionRequests} supportThreads={supportThreads} initialTab={adminStartTab} clearInitialTab={() => setAdminStartTab("")} reload={loadApp} openSupport={(userId) => { setSupportTarget(userId || ""); setSupportOpen(true); }} notify={notify} withNotify={withNotify} />}
        </>}
      </main>
      <MobileBottomNav t={t} view={view} role={session.role} setView={setView} setAdminStartTab={setAdminStartTab} openAllJobs={openAllJobs} openComingInterviews={openComingInterviews} isAdmin={isAdminRole(session.role)} />
      {!isAgent && builderOpen && <ProfileBuilder t={t} me={me} reload={loadApp} close={() => setBuilderOpen(false)} notify={notify} />}
      {supportOpen && <SupportWindow t={t} me={me} users={adminUsers} initialUserId={supportTarget} onUpdate={loadSupportThreads} close={() => { setSupportOpen(false); setSupportTarget(""); }} />}
      {agentChatOpen && !isAgent && agentChatTarget && <UserAgentChatWindow t={t} agent={agentChatTarget} threads={userAgentThreads} setAgent={setAgentChatTarget} onUpdate={async () => { const threads = await api("/user/agent-chat/threads"); userAgentUnreadRef.current = threads.reduce((sum, thread) => sum + Number(thread.unread_count || 0), 0); setUserAgentThreads(threads); }} close={() => { setAgentChatOpen(false); setAgentChatTarget(null); }} />}
      {popup && <ToastPopup t={t} popup={popup} close={() => setPopup(null)} />}
      {sessionWarningOpen && <SessionWarningModal t={t} seconds={sessionCountdown} stayConnected={stayConnected} logout={logout} />}
      <AppFooter />
    </div>
  );
}

function SessionWarningModal({ t, seconds, stayConnected, logout }) {
  return (
    <div className="builder-backdrop session-warning-backdrop" role="presentation">
      <section className="session-warning-modal" role="dialog" aria-modal="true" aria-live="assertive">
        <h2>{t("sessionExpiringTitle")}</h2>
        <p>{t("sessionExpiringBody")}</p>
        <strong>{t("autoLogoutIn")} {Math.max(0, seconds)}s</strong>
        <div className="modal-actions">
          <button className="secondary-button" type="button" onClick={logout}>{t("logout")}</button>
          <button className="primary-button" type="button" onClick={stayConnected}>{t("stayConnected")}</button>
        </div>
      </section>
    </div>
  );
}

function ToastPopup({ t, popup, close }) {
  const isError = popup.type === "error";
  return (
    <section className={`toast-popup ${isError ? "error-popup" : "success-popup"}`} role="alertdialog" aria-live="assertive">
      <div>
        <strong>{isError ? t("errorTitle") : t("successSaved")}</strong>
        <button className="icon-button" type="button" onClick={close} aria-label={t("close")}>×</button>
      </div>
      <p>{popup.message}</p>
      {isError && <button className="secondary-button compact" type="button" onClick={() => navigator.clipboard?.writeText(popup.details || popup.message)}>{t("copyError")}</button>}
    </section>
  );
}

function AdminModal({ title, close, children }) {
  return (
    <div className="builder-backdrop admin-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && close()}>
      <section className="builder-modal admin-modal" role="dialog" aria-modal="true">
        <header className="builder-head">
          <h2>{title}</h2>
          <button className="icon-button" type="button" onClick={close} aria-label="Close">×</button>
        </header>
        {children}
      </section>
    </div>
  );
}

function QuestionRows({ t, questions, onChange }) {
  const rows = questionsToArray(questions);
  function update(index, value) {
    onChange(rows.map((row, rowIndex) => rowIndex === index ? value : row));
  }
  function remove(index) {
    const next = rows.filter((_, rowIndex) => rowIndex !== index);
    onChange(next.length ? next : [""]);
  }
  return (
    <div className="question-row-editor">
      <strong>{t("screeningQuestions")}</strong>
      {rows.map((question, index) => (
        <div className="question-row" key={index}>
          <input placeholder={`${t("screeningQuestions")} ${index + 1}`} value={question} onChange={(event) => update(index, event.target.value)} />
          {rows.length > 1 && <button className="icon-button" type="button" onClick={() => remove(index)} aria-label={t("delete")}>×</button>}
        </div>
      ))}
      <button className="secondary-button compact" type="button" onClick={() => onChange([...rows, ""])}>+</button>
    </div>
  );
}

function Login({ lang, setLang, t, login, verifyAndLoad, error, setError }) {
  const [mode, setMode] = useState("login");
  const [publicPage, setPublicPage] = useState("home");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [dob, setDob] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactSubject, setContactSubject] = useState("");
  const [contactMessage, setContactMessage] = useState("");
  const [otp, setOtp] = useState("");
  const [mfaChallengeId, setMfaChallengeId] = useState("");
  const [notice, setNotice] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [sendingContact, setSendingContact] = useState(false);

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
      const data = await login(email, password);
      if (data?.mfaRequired) {
        setMfaChallengeId(data.challengeId);
        setNotice(data.devOtp ? `${data.message} OTP: ${data.devOtp}` : data.message || t("checkEmail"));
        setOtp("");
        setMode("mfa");
      }
    } finally {
      setLoggingIn(false);
    }
  }

  async function register(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    if (password !== repeatPassword) {
      setError(t("passwordsDoNotMatch"));
      return;
    }
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

  async function verifyMfa(event) {
    event.preventDefault();
    setError("");
    setVerifying(true);
    try {
      const data = await api("/auth/verify-mfa", { method: "POST", body: JSON.stringify({ challengeId: mfaChallengeId, otp }) });
      await verifyAndLoad(data.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setVerifying(false);
    }
  }

  async function submitContact(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setSendingContact(true);
    try {
      const data = await api("/contact", {
        method: "POST",
        body: JSON.stringify({
          name: contactName,
          email: contactEmail,
          subject: contactSubject,
          message: contactMessage
        })
      });
      setNotice(data.message || t("contactSuccess"));
      setContactName("");
      setContactEmail("");
      setContactSubject("");
      setContactMessage("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingContact(false);
    }
  }

  return (
    <main className={`login-page login-page-${publicPage} login-mode-${mode} ${lang === "ar" ? "login-page-rtl" : ""}`}>
      <header className="login-top">
        <img className="login-top-logo" src="/brand/rawabet-logo-lockup-cropped.png" alt="Rawabet - روابط تجمعنا" />
        <div className="login-public-actions">
          <nav className="login-public-nav" aria-label="Public pages">
            <button type="button" className={publicPage === "home" ? "active" : ""} onClick={() => { setPublicPage("home"); setError(""); setNotice(""); }}>{t("home")}</button>
            <button type="button" className={publicPage === "about" ? "active" : ""} onClick={() => { setPublicPage("about"); setError(""); setNotice(""); }}>{t("aboutUs")}</button>
            <button type="button" className={publicPage === "contact" ? "active" : ""} onClick={() => { setPublicPage("contact"); setError(""); setNotice(""); }}>{t("contactUs")}</button>
          </nav>
          <button type="button" className="icon-button login-language-button" onClick={() => setLang((current) => current === "en" ? "ar" : "en")}>{t("language")}</button>
        </div>
      </header>
      <section className="login-stage">
        <div className="login-copy">
          <div className="login-heading">
            <p>{t("welcomeTitle")}</p>
            <h1>{t("welcome")}</h1>
            <span>{t("loginSubtitle")}</span>
          </div>
          {publicPage === "about" && <section className="login-info-card">
            <h2>{t("aboutTitle")}</h2>
            <p>{t("aboutBodyOne")}</p>
            <p>{t("aboutBodyTwo")}</p>
          </section>}

          {publicPage === "contact" && <form className="login-card login-contact-card" onSubmit={submitContact}>
            <p className="login-contact-intro">{t("contactIntro")}</p>
            <label>{t("contactName")}<input value={contactName} onChange={(event) => setContactName(event.target.value)} required /></label>
            <label>{t("email")}<input type="email" value={contactEmail} onChange={(event) => setContactEmail(event.target.value)} required /></label>
            <label>{t("contactSubject")}<input value={contactSubject} onChange={(event) => setContactSubject(event.target.value)} /></label>
            <label>{t("contactMessage")}<textarea rows="4" value={contactMessage} onChange={(event) => setContactMessage(event.target.value)} required /></label>
            {notice && <p className="notice">{notice}</p>}
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={sendingContact}>{sendingContact && <span className="spinner" aria-hidden="true"></span>}{t("send")}</button>
          </form>}

          {publicPage === "home" && mode === "login" && <form className="login-card" onSubmit={submitLogin} autoComplete="off">
            <div className="login-card-head">
              <strong>{t("login")}</strong>
              <span>{t("needAccount")}</span>
            </div>
            <label>{t("email")}<input name="rawabet-login-email" autoComplete="new-password" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <PasswordField
              label={t("password")}
              name="rawabet-login-password"
              value={password}
              onChange={setPassword}
              visible={showLoginPassword}
              setVisible={setShowLoginPassword}
              t={t}
            />
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={loggingIn}>{loggingIn && <span className="spinner" aria-hidden="true"></span>}{t("login")}</button>
            <button className="auth-switch" type="button" onClick={() => { setMode("register"); setError(""); }}>{t("needAccount")}</button>
          </form>}

          {publicPage === "home" && mode === "register" && <form className="login-card" onSubmit={register}>
            <div className="login-card-head">
              <strong>{t("createAccount")}</strong>
              <span>{t("checkEmail")}</span>
            </div>
            <label>{t("fullName")}<input value={fullName} onChange={(event) => setFullName(event.target.value)} required /></label>
            <label>{t("email")}<input value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>{t("phone")}<input value={phone} onChange={(event) => setPhone(event.target.value)} required /></label>
            <label>{t("dob")}<input type="date" value={dob} onChange={(event) => setDob(event.target.value)} required /></label>
            <PasswordField label={t("password")} value={password} onChange={setPassword} visible={showRegisterPassword} setVisible={setShowRegisterPassword} t={t} required />
            <PasswordField label={t("repeatPassword")} value={repeatPassword} onChange={setRepeatPassword} visible={showRepeatPassword} setVisible={setShowRepeatPassword} t={t} required />
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={registering}>{registering && <span className="spinner" aria-hidden="true"></span>}{t("createAccount")}</button>
            <button className="auth-switch" type="button" disabled={registering} onClick={() => { setMode("login"); setError(""); }}>{t("haveAccount")} {t("login")}</button>
          </form>}

          {publicPage === "home" && mode === "verify" && <form className="login-card" onSubmit={verify}>
            <div className="login-card-head">
              <strong>{t("verifyEmail")}</strong>
              <span>{t("checkEmail")}</span>
            </div>
            <label>{t("email")}<input value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>{t("verificationCode")}<input value={otp} onChange={(event) => setOtp(event.target.value)} required /></label>
            {notice && <p className="notice">{notice}</p>}
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={verifying}>{verifying && <span className="spinner" aria-hidden="true"></span>}{t("verifyEmail")}</button>
            <button className="auth-switch" type="button" disabled={verifying} onClick={() => { setMode("login"); setError(""); }}>{t("haveAccount")} {t("login")}</button>
          </form>}

          {publicPage === "home" && mode === "mfa" && <form className="login-card" onSubmit={verifyMfa}>
            <div className="login-card-head">
              <strong>{t("verifyEmail")}</strong>
              <span>{t("checkEmail")}</span>
            </div>
            <label>{t("email")}<input value={email} readOnly /></label>
            <label>{t("verificationCode")}<input value={otp} onChange={(event) => setOtp(event.target.value)} required /></label>
            {notice && <p className="notice">{notice}</p>}
            {error && <p className="error">{error}</p>}
            <button className="primary-button loading-button" disabled={verifying}>{verifying && <span className="spinner" aria-hidden="true"></span>}{t("verifyEmail")}</button>
            <button className="auth-switch" type="button" disabled={verifying} onClick={() => { setMode("login"); setError(""); setMfaChallengeId(""); }}>{t("haveAccount")} {t("login")}</button>
          </form>}
        </div>
        <div className="login-visual">
          <div className="login-visual-card">
            <img src="/brand/login-hero.svg" alt="" />
            <div className="login-trust-strip">
              <span>{t("loginTrustOne")}</span>
              <span>{t("loginTrustTwo")}</span>
              <span>{t("loginTrustThree")}</span>
            </div>
          </div>
        </div>
      </section>
      <AppFooter />
    </main>
  );
}

function AppFooter() {
  return (
    <footer className="app-footer">
      <span className="footer-brand">
        <span>v1.1.0 © 2026 Rawabet. All rights reserved.</span>
      </span>
    </footer>
  );
}

function Home({ t, lang, me, jobs, agents = [], setSelectedAgent, setView, openJob, openAppliedJobs, openBuilder, openSmartResume, openSupportAssistant, canUseSmartResume = true, jobSearch, setJobSearch, setJobMode, notify }) {
  const strength = Number(me.profile?.profile_strength ?? 0);
  const strengthState = profileStrengthStatus(strength, t);
  const applications = me.applications || [];
  const priorityApplications = applications.filter((item) => ["interview", "review"].includes(normalizeStatusValue(item.status)));
  const skills = Array.isArray(me.profile?.skills) ? me.profile.skills.filter(Boolean) : [];
  const experiences = me.experiences || [];
  const interviews = me.interviews || [];
  const scheduledJobIds = new Set(interviews.map((item) => item.job_id).filter(Boolean));
  const applicationStatusByJob = new Map(applications.map((item) => [item.job_id, normalizeStatusValue(item.status)]));
  const jobFrameClass = (jobId) => {
    const status = applicationStatusByJob.get(jobId);
    if (scheduledJobIds.has(jobId) || status === "interview") return "interview-frame";
    if (status === "accepted") return "accepted-frame";
    return "";
  };
  const orderedJobs = [...jobs].sort((a, b) => Number(scheduledJobIds.has(b.id)) - Number(scheduledJobIds.has(a.id))).slice(0, 10);
  const previewAgents = agents.slice(0, 7);
  function openAllJobsFromHome() {
    setJobMode("all");
    setView("jobs");
  }
  return (
    <div className="layout-grid">
      <section className="mobile-home-priority">
        <section className="panel side-panel strength-panel">
          <h2>{t("profileStrength")}</h2>
          <b className="strength-label">{strengthState.label}</b>
          <div className="meter"><span style={{ width: `${strength}%` }} /></div>
          <p>{strengthState.body}</p>
        </section>
        <section className="panel side-panel applied-summary-panel">
          <h2>{t("profileViews")}</h2>
          <strong className="side-stat">{formatNumber(applications.length)}</strong>
          <div className="job-strip side-job-strip">{priorityApplications.length ? priorityApplications.map((item) => <span className="application-chip" key={item.id}>{item.title}<b className={`status ${normalizeStatusValue(item.status)}`}>{statusLabel(normalizeStatusValue(item.status), lang)}</b></span>) : <span>{t("noAppliedJobs")}</span>}</div>
          {!!applications.length && <button className="panel-link more-link" type="button" onClick={openAppliedJobs}><span>↗</span>{t("more")}</button>}
        </section>
      </section>
      <aside className="profile-rail">
        <section className="profile-card">
          <div className="cover-strip" />
          <div className="avatar-wrap"><Avatar user={me.user} /></div>
          <h2>{me.user.fullName}</h2>
          <p>{me.user.headline}</p>
          <button className="secondary-button" onClick={() => setView("profile")}>{t("editProfileAction")}</button>
        </section>
        <section className="panel side-panel applied-summary-panel desktop-applied-summary-panel">
          <h2>{t("profileViews")}</h2>
          <strong className="side-stat">{formatNumber(applications.length)}</strong>
          <div className="job-strip side-job-strip">{priorityApplications.length ? priorityApplications.map((item) => <span className="application-chip" key={item.id}>{item.title}<b className={`status ${normalizeStatusValue(item.status)}`}>{statusLabel(normalizeStatusValue(item.status), lang)}</b></span>) : <span>{t("noAppliedJobs")}</span>}</div>
          {!!applications.length && <button className="panel-link more-link" type="button" onClick={openAppliedJobs}><span>↗</span>{t("more")}</button>}
        </section>
        {!!interviews.length && <section className="panel side-panel interview-panel">
          <h2>{t("upcomingInterviews")}</h2>
          {interviews.slice(0, 3).map((interview) => <button className="panel-link interview-link" type="button" onClick={() => setView("interviews")} key={interview.id}><span>◌</span><div><strong>{interview.job_title || t("job")}</strong><small>{new Date(interview.scheduled_at).toLocaleString()}</small></div></button>)}
        </section>}
        <section className="panel side-panel workspace-panel">
          <h2>{t("workspace")}</h2>
          <button className="panel-link" onClick={() => setView("profile")}><span>↗</span>{t("publicProfile")}</button>
          <button className="panel-link" onClick={openSupportAssistant}><span>✦</span>{t("aiAssistant")}</button>
          {canUseSmartResume && <button className="panel-link" onClick={openSmartResume}><span>◈</span>{t("smartResume")}</button>}
          <button className="panel-link desktop-only-workspace-link" onClick={() => setView("courses")}><span>▤</span>{t("courses")}</button>
          <button className="panel-link" onClick={() => setView("allJobs")}><span>▦</span>{t("savedJobs")}</button>
          {["admin", "master_admin"].includes(me.user.role) && <button className="panel-link" onClick={() => setView("admin")}><span>▥</span>{t("adminDashboard")}</button>}
        </section>
      </aside>
      <section className="feed">
        <article className="panel post-card">
          <div className="post-head"><div className="company-logo">R</div><div><h2>{t("adminPosts")}</h2><p>{t("jobs")}</p></div></div>
          <label className="search mobile-home-search">
            <span>⌕</span>
            <input placeholder={t("search")} value={jobSearch} onChange={(event) => { setJobMode("all"); setJobSearch(event.target.value); setView("jobs"); }} />
          </label>
          <div className="admin-post-list">
            {orderedJobs.length ? orderedJobs.map((job) => (
              <article className={["admin-post", scheduledJobIds.has(job.id) ? "highlighted-job" : "", jobFrameClass(job.id)].filter(Boolean).join(" ")} key={job.id}>
                <strong>{job.title}</strong>
                <span>{job.salary_range || "-"} · {job.company_name}</span>
                <button className="secondary-button compact" type="button" onClick={() => openJob(job.id)}>{t("more")}</button>
              </article>
            )) : <p>{t("noAdminPosts")}</p>}
          </div>
          {jobs.length > 10 && <button className="panel-link more-link" type="button" onClick={openAllJobsFromHome}><span>↗</span>{t("more")}</button>}
        </article>
      </section>
      <aside className="insight-rail">
        <section className="panel side-panel strength-panel">
          <h2>{t("profileStrength")}</h2>
          <b className="strength-label">{strengthState.label}</b>
          <div className="meter"><span style={{ width: `${strength}%` }} /></div>
          <p>{strengthState.body}</p>
        </section>
        <section className="panel side-panel profile-snapshot-panel">
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
        {!!agents.length && <section className="panel side-panel companies-panel">
          <h2>{t("agentDirectory")}</h2>
          <div className="agency-list compact-agency-list">
            {previewAgents.map((agent) => (
              <button className="agency-row" type="button" key={agent.id} onClick={() => { setSelectedAgent(agent); setView("agents"); }}>
                <Avatar user={{ full_name: agent.full_name, avatar_url: agent.avatar_url, plan: agent.plan, last_active_at: agent.last_active_at }} size="small" />
                <span><strong>{agent.agency_name || agent.full_name}</strong><small>{agent.open_jobs || 0} {t("activeJobs")}</small></span>
              </button>
            ))}
          </div>
          {agents.length > 7 && <button className="panel-link more-link" type="button" onClick={() => setView("agents")}><span>↗</span>{t("more")}</button>}
        </section>}
      </aside>
    </div>
  );
}

function PlanCards({ t, currentRole = "member", currentPlan = "free", subscriptionExpiresAt = "", notify, menuMode = false, profileMode = false }) {
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [submittingPlan, setSubmittingPlan] = useState("");
  const subInfo = subscriptionInfo({ plan: currentPlan, subscriptionExpiresAt }, t);
  const plans = [
    {
      id: "premium",
      title: t("premiumPlan"),
      price: t("premiumPrice"),
      body: t("premiumPlanBody"),
      active: currentPlan === "premium"
    },
    {
      id: "agent",
      title: t("agentPlan"),
      price: t("agentPrice"),
      body: t("agentPlanBody"),
      active: currentRole === "agent"
    }
  ].filter((plan) => currentRole === "agent" ? plan.id === "agent" : plan.id === "premium");
  const primaryPlan = plans[0];
  async function requestPlan(plan) {
    setSubmittingPlan(plan);
    try {
      await api("/account/subscription-requests", {
        method: "POST",
        body: JSON.stringify({ plan, paymentMethod })
      });
      notify?.(t("planRequestSent"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    } finally {
      setSubmittingPlan("");
    }
  }
  return (
    <section className={menuMode ? "plan-panel menu-plan-panel" : profileMode ? "panel plan-panel profile-plan-panel" : "panel side-panel plan-panel"}>
      <div className="subscription-card-head">
        <div>
          <h2>{t("subscriptionPlans")}</h2>
          {primaryPlan && <span>{primaryPlan.title} · {primaryPlan.price}</span>}
        </div>
        <span className={`subscription-badge ${subInfo.state}`}>{subInfo.label}</span>
      </div>
      {subInfo.detail && <small className="subscription-detail">{subInfo.detail}</small>}
      <div className="payment-methods" role="group" aria-label={t("paymentMethod")}>
        <button className={paymentMethod === "cash" ? "active" : ""} type="button" onClick={() => setPaymentMethod("cash")}>{t("cashPayment")}</button>
        <button className={paymentMethod === "shamcash" ? "active shamcash-choice" : "shamcash-choice"} type="button" onClick={() => setPaymentMethod("shamcash")}><img src="/brand/shamcash.png" alt="" />{t("shamCashPayment")}</button>
      </div>
      {profileMode && primaryPlan ? (
        <button className="secondary-button compact subscription-request-button" type="button" disabled={primaryPlan.active || submittingPlan === primaryPlan.id} onClick={() => requestPlan(primaryPlan.id)}>
          {submittingPlan === primaryPlan.id ? t("saving") : primaryPlan.active ? t("active") : t("requestPlan")}
        </button>
      ) : null}
      {!profileMode && (
      <div className="plan-card-list">
        {plans.map((plan) => (
          <article className={plan.active ? "plan-card active" : "plan-card"} key={plan.id}>
            <div><strong>{plan.title}</strong><b>{plan.price}</b></div>
            <p>{plan.body}</p>
            <button className="secondary-button compact" type="button" disabled={plan.active || submittingPlan === plan.id} onClick={() => requestPlan(plan.id)}>
              {submittingPlan === plan.id ? t("saving") : plan.active ? t("active") : t("requestPlan")}
            </button>
          </article>
        ))}
      </div>
      )}
    </section>
  );
}

function SubscriptionStatus({ user, t }) {
  const info = subscriptionInfo(user, t);
  return (
    <div className="subscription-cell">
      <span className={`subscription-badge ${info.state}`}>{info.label}</span>
      {info.detail && <small>{info.detail}</small>}
    </div>
  );
}

function ApplicationResumeLink({ application, t }) {
  const url = application?.resume_file_url || application?.resumeFileUrl;
  const name = application?.resume_file_name || application?.resumeFileName || t("resume");
  if (!url) return <span className="muted-inline">-</span>;
  return <a className="attachment-link compact-link" href={assetUrl(url)} target="_blank" rel="noreferrer">{name}</a>;
}

function NavIcon({ name }) {
  const common = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2.15", strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": "true" };
  const paths = {
    home: <><path d="M3.5 10.5 12 3.25l8.5 7.25" /><path d="M5.25 9.75V20.5h13.5V9.75" /><path d="M9.5 20.5v-6h5v6" /></>,
    profile: <><circle cx="12" cy="7.75" r="3.75" /><path d="M4.75 20.25c1.35-4.1 3.8-6.15 7.25-6.15s5.9 2.05 7.25 6.15" /></>,
    jobs: <><rect x="4" y="7.5" width="16" height="12.5" rx="2.2" /><path d="M9 7.5V5.8A1.8 1.8 0 0 1 10.8 4h2.4A1.8 1.8 0 0 1 15 5.8v1.7" /><path d="M4 12.25h16" /><path d="M10.5 15h3" /></>,
    interviews: <><rect x="4.25" y="5.25" width="15.5" height="15" rx="2.2" /><path d="M8 3.5v4M16 3.5v4M4.25 10h15.5" /><path d="M8 14h4.5M8 17h7.5" /></>,
    courses: <><path d="M3.5 6.75 12 3.25l8.5 3.5-8.5 3.5-8.5-3.5Z" /><path d="M6.5 9.1v4.4c2.9 2.15 8.1 2.15 11 0V9.1" /><path d="M20.5 7v6.25" /></>,
    agents: <><rect x="4.25" y="6.75" width="15.5" height="13.5" rx="2" /><path d="M8 6.75V4.5h8v2.25" /><path d="M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15h.01" /></>,
    admin: <><rect x="4" y="4" width="16" height="16" rx="2.5" /><path d="M8 9h8M8 12h8M8 15h5" /></>,
    support: <><path d="M5 6.75A3.25 3.25 0 0 1 8.25 3.5h7.5A3.25 3.25 0 0 1 19 6.75v5.5a3.25 3.25 0 0 1-3.25 3.25H11l-4.4 4v-4.1A3.25 3.25 0 0 1 5 12.25v-5.5Z" /><path d="M8.5 8.5h7M8.5 11.5h4.5" /></>
  };
  return <svg {...common}>{paths[name]}</svg>;
}

function MobileBottomNav({ t, view, role, setView, setAdminStartTab, openAllJobs, openComingInterviews, isAdmin = false }) {
  function openAdminTab(tab) {
    setAdminStartTab?.(tab);
    setView("admin");
  }
  const adminItems = [
    { id: "admin-overview", icon: "home", label: t("overview"), action: () => openAdminTab("overview") },
    { id: "admin-users", icon: "profile", label: t("userManagement"), action: () => openAdminTab("users") },
    { id: "admin-jobs", icon: "jobs", label: t("jobManagement"), action: () => openAdminTab("jobs") },
    { id: "admin-applications", icon: "admin", label: t("applications"), action: () => openAdminTab("applications") },
    { id: "admin-interviews", icon: "interviews", label: t("interviews"), action: () => openAdminTab("interviews") },
    { id: "admin-support", icon: "support", label: t("supportInbox"), action: () => openAdminTab("support") }
  ];
  const agentItems = [
    { id: "agent", icon: "home", label: t("overview"), action: () => setView("agent") },
    { id: "agent-jobs", icon: "jobs", label: t("assignedJobs"), action: () => setView("agent-jobs") },
    { id: "agent-users", icon: "profile", label: t("users"), action: () => setView("agent-users") },
    { id: "agent-applications", icon: "admin", label: t("applications"), action: () => setView("agent-applications") },
    { id: "agent-chat", icon: "support", label: t("agentChat"), action: () => setView("agent-chat") },
    { id: "agent-interviews", icon: "interviews", label: t("scheduledInterviews"), action: () => setView("agent-interviews") }
  ];
  const userItems = [
    ...(isAdmin ? [{ id: "admin", icon: "admin", label: t("admin"), action: () => setView("admin") }] : []),
    { id: "home", icon: "home", label: t("home"), action: () => setView("home") },
    { id: "profile", icon: "profile", label: t("profile"), action: () => setView("profile") },
    { id: "allJobs", icon: "jobs", label: t("jobs"), action: openAllJobs },
    { id: "interviews", icon: "interviews", label: t("upcomingInterviews"), action: openComingInterviews },
    { id: "courses", icon: "courses", label: t("courses"), action: () => setView("courses") },
    { id: "agents", icon: "agents", label: t("companies"), action: () => setView("agents") }
  ];
  const items = role === "agent" ? agentItems : isAdmin ? adminItems : userItems;
  return (
    <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
      {items.map((item) => <button className={view === item.id || (item.id === "allJobs" && view === "jobs") ? "active" : ""} type="button" onClick={item.action} aria-label={item.label} title={item.label} key={item.id}><span><NavIcon name={item.icon} /></span></button>)}
    </nav>
  );
}

function CoursesPage({ t, courses = [] }) {
  const [page, setPage] = useState(1);
  const pagedCourses = pageItems(courses, page);
  return (
    <section className="courses-page">
      <div className="panel section-head mobile-page-head">
        <h2>{t("courses")}</h2>
        <span className="status">{courses.length}</span>
      </div>
      {courses.length ? pagedCourses.map((course) => (
        <article className="panel course-card" key={course.id}>
          <h2>{course.title}</h2>
          <p>{course.provider || "-"}</p>
          {course.completion_date && <span>{course.completion_date}</span>}
          {course.notes && <small>{course.notes}</small>}
          {course.certificate_url && <a className="secondary-button compact" href={assetUrl(course.certificate_url)} target="_blank" rel="noreferrer">{t("seeCourse")}</a>}
        </article>
      )) : <section className="panel empty-state"><h2>{t("courses")}</h2><p>{t("noAttachments")}</p></section>}
      <PaginationControls t={t} page={page} total={courses.length} setPage={setPage} />
    </section>
  );
}

function ComingInterviews({ t, interviews = [], openJob }) {
  const [page, setPage] = useState(1);
  const pagedInterviews = pageItems(interviews, page);
  return (
    <section className="interviews-page">
      <div className="panel section-head mobile-page-head">
        <h2>{t("upcomingInterviews")}</h2>
        <span className="status">{interviews.length}</span>
      </div>
      {interviews.length ? pagedInterviews.map((interview) => (
        <article className="panel interview-page-card highlighted-job" key={interview.id}>
          <div>
            <h2>{interview.job_title || t("job")}</h2>
            <p>{interview.company_name || "-"} · {interview.location || "-"}</p>
            <span>{new Date(interview.scheduled_at).toLocaleString()}</span>
          </div>
          {interview.channel && <small>{interview.channel}</small>}
          {interview.notes && <p>{interview.notes}</p>}
          {interview.job_id && <button className="secondary-button compact" type="button" onClick={() => openJob(interview.job_id)}>{t("jobDetails")}</button>}
        </article>
      )) : <section className="panel empty-state"><h2>{t("upcomingInterviews")}</h2><p>-</p></section>}
      <PaginationControls t={t} page={page} total={interviews.length} setPage={setPage} />
    </section>
  );
}

function AgentsPage({ t, agents = [], selectedAgent, setSelectedAgent, openJob, openAgentChat }) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [detail, setDetail] = useState(null);
  const visibleAgents = agents.filter((agent) => `${agent.full_name || ""} ${agent.agency_name || ""}`.toLowerCase().includes(search.toLowerCase()));
  const pagedAgents = pageItems(visibleAgents, page);
  useEffect(() => setPage(1), [search]);
  useEffect(() => {
    if (!selectedAgent?.id) return;
    setPage(1);
    api(`/agents/${selectedAgent.id}`).then(setDetail).catch(() => setDetail(null));
  }, [selectedAgent?.id]);
  if (selectedAgent) {
    const agent = detail?.agent || selectedAgent;
    const jobs = detail?.jobs || [];
    const pagedJobs = pageItems(jobs, page);
    return (
      <section className="agency-page">
        <div className="section-head"><button className="secondary-button compact" onClick={() => { setSelectedAgent(null); setDetail(null); }}>{t("backToCompanies")}</button></div>
        <section className="profile-hero panel">
          <Avatar user={{ full_name: agent.full_name, avatar_url: agent.avatar_url, plan: agent.plan, last_active_at: agent.last_active_at }} size="large" />
          <div><h1>{agent.agency_name || agent.full_name}</h1><p>{agent.full_name}</p><span>{agent.location || "-"}</span>{agent.website && <a href={assetUrl(agent.website)} target="_blank" rel="noreferrer">{agent.website}</a>}<p className="agency-about-detail">{agent.agency_about || agent.about || agent.headline || "-"}</p>{openAgentChat && <button className="secondary-button compact" type="button" onClick={() => openAgentChat(agent)}>{t("chatWithAgent")}</button>}</div>
        </section>
        <section className="panel">
          <div className="section-head"><h2>{t("activeJobs")}</h2><span className="status">{jobs.length}</span></div>
          <div className="admin-post-list">
            {jobs.length ? pagedJobs.map((job) => <article className="admin-post" key={job.id}><strong>{job.title}</strong><span>#{job.job_number || "-"} · {job.salary_range || "-"} · {job.location}</span><button className="secondary-button compact" onClick={() => openJob(job.id)}>{t("jobDetails")}</button></article>) : <p>{t("noJobsMatching")}</p>}
          </div>
          <PaginationControls t={t} page={page} total={jobs.length} setPage={setPage} />
        </section>
      </section>
    );
  }
  return (
    <section className="agency-page">
      <section className="panel">
        <div className="section-head"><h2>{t("agentDirectory")}</h2><input placeholder={t("searchAgents")} value={search} onChange={(e) => setSearch(e.target.value)} /></div>
        <div className="agent-profile-grid-list">
          {pagedAgents.map((agent) => <button className="agent-profile-tile" type="button" key={agent.id} onClick={() => setSelectedAgent(agent)}><Avatar user={{ full_name: agent.full_name, avatar_url: agent.avatar_url, plan: agent.plan, last_active_at: agent.last_active_at }} size="large" /><strong>{agent.agency_name || agent.full_name}</strong><span>{agent.headline || agent.location || "-"}</span><small>{agent.open_jobs || 0} {t("activeJobs")}</small></button>)}
        </div>
        <PaginationControls t={t} page={page} total={visibleAgents.length} setPage={setPage} />
      </section>
    </section>
  );
}

function ProfileBuilder({ t, me, reload, close, notify }) {
  const isPremium = me.user.plan === "premium" && (!me.user.subscriptionExpiresAt || new Date(me.user.subscriptionExpiresAt) > new Date());
  const resumeLimit = isPremium ? 2 : 1;
  const certificateLimit = isPremium ? 5 : 1;
  const [form, setForm] = useState({
    fullName: me.user.fullName || "",
    phone: me.user.phone || "",
    dob: me.user.dob || "",
    headline: me.user.headline || "",
    location: me.user.location || "",
    about: me.profile?.about || "",
    skills: (me.profile?.skills || []).join(", "),
    resumeEducation: me.profile?.resume_education || "",
    resumeCertifications: me.profile?.resume_certifications || "",
    resumeTools: me.profile?.resume_tools || "",
    resumeAdditionalInfo: me.profile?.resume_additional_info || ""
  });
  const [experience, setExperience] = useState({ title: "", company: "", location: "", startDate: "", endDate: "", isCurrent: false, description: "" });
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
      notify?.(err.message, "error", err.stack || err.message);
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
    setExperience({ title: "", company: "", location: "", startDate: "", endDate: "", isCurrent: false, description: "" });
    await reload();
  }

  async function deleteAttachment(documentId) {
    await api(`/account/documents/${documentId}`, { method: "DELETE" });
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
            <label>{t("resume")}<input type="file" accept=".pdf,.doc,.docx" onChange={(e) => upload("resume", e.target.files[0])} /><span>{resumeLimit}</span></label>
            <label>{t("certificate")}<input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e) => upload("certificate", e.target.files[0])} /><span>{t("maxCertificates").replace("{count}", certificateLimit)}</span></label>
            <div className="upload-preview">
              <Avatar user={me.user} size="large" />
              <div><strong>{t("filesStayLocal")}</strong><p>{t("filesStayLocalBody")}</p></div>
            </div>
            <DocumentLinks t={t} documents={me.documents} avatarUrl={me.user.avatarUrl} onDelete={deleteAttachment} />
          </section>

          <section className="builder-panel span">
            <h3>{t("careerHistory")}</h3>
            <div className="row-fields">
              <input placeholder={t("title")} value={experience.title} onChange={(e) => setExperience({ ...experience, title: e.target.value })} />
              <input placeholder={t("company")} value={experience.company} onChange={(e) => setExperience({ ...experience, company: e.target.value })} />
              <input placeholder={t("location")} value={experience.location} onChange={(e) => setExperience({ ...experience, location: e.target.value })} />
              <input type="date" value={experience.startDate} onChange={(e) => setExperience({ ...experience, startDate: e.target.value })} />
              <input type="date" value={experience.endDate} disabled={experience.isCurrent} onChange={(e) => setExperience({ ...experience, endDate: e.target.value })} />
              <label className="inline-check"><input type="checkbox" checked={experience.isCurrent} onChange={(e) => setExperience({ ...experience, isCurrent: e.target.checked, endDate: e.target.checked ? "" : experience.endDate })} />{t("current")}</label>
              <textarea className="span" placeholder={t("description")} value={experience.description} onChange={(e) => setExperience({ ...experience, description: e.target.value })} />
              <button className="secondary-button" type="button" onClick={addExperience}>{t("addExperience")}</button>
            </div>
            <div className="timeline-list">
              {me.experiences.map((item) => <div className="timeline-item" key={item.id}><strong>{item.title}</strong><span>{item.company}{item.start_date || item.end_date ? ` · ${[item.start_date, item.is_current ? "Present" : item.end_date].filter(Boolean).join(" - ")}` : ""}</span></div>)}
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

function SmartResumePage({ t, me, reload, notify }) {
  return (
    <div className="profile-page">
      <SmartResumePanel t={t} me={me} reload={reload} notify={notify} />
    </div>
  );
}

function SmartResumePanel({ t, me, reload, notify }) {
  const [resumeBuilder, setResumeBuilder] = useState({
    summary: me.profile?.about || "",
    education: "",
    certifications: me.profile?.resume_certifications || "",
    tools: me.profile?.resume_tools || "",
    languages: Array.isArray(me.profile?.languages) ? me.profile.languages.join("\n") : "Arabic\nEnglish",
    additionalInfo: me.profile?.resume_additional_info || ""
  });
  const [buildingResume, setBuildingResume] = useState(false);
  const skills = Array.isArray(me.profile?.skills) ? me.profile.skills : [];

  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || "").split(",")[1] || "");
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  async function saveResumeOnMobile(blob) {
    const [{ Capacitor }, { Filesystem, Directory }, { Share }] = await Promise.all([
      import("@capacitor/core"),
      import("@capacitor/filesystem"),
      import("@capacitor/share")
    ]);
    if (!Capacitor.isNativePlatform()) return false;
    const fileName = `rawabet-smart-resume-${Date.now()}.pdf`;
    const data = await blobToBase64(blob);
    let saved;
    try {
      saved = await Filesystem.writeFile({
        path: fileName,
        data,
        directory: Directory.Documents,
        recursive: true
      });
    } catch {
      saved = await Filesystem.writeFile({
        path: fileName,
        data,
        directory: Directory.Cache,
        recursive: true
      });
    }
    const fileUri = saved.uri || (await Filesystem.getUri({ path: fileName, directory: Directory.Documents }).catch(() => null))?.uri;
    await Share.share({
      title: "Rawabet smart resume",
      text: "Rawabet smart resume PDF",
      url: fileUri,
      dialogTitle: "Download or share resume"
    });
    return true;
  }

  async function generateResume(event) {
    event.preventDefault();
    setBuildingResume(true);
    try {
      const response = await fetch(`${API_URL}/account/resume-builder`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {})
        },
        body: JSON.stringify(resumeBuilder)
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || data.message || "Request failed");
      }
      const blob = await response.blob();
      if (!blob.size) throw new Error("Resume PDF was empty. Please try again.");
      if (blob.type && !blob.type.includes("pdf")) {
        const message = await blob.text().catch(() => "");
        throw new Error(message || "Resume PDF could not be generated.");
      }
      if (await saveResumeOnMobile(blob)) {
        return;
      }
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "rawabet-smart-resume.pdf";
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 30000);
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    } finally {
      setBuildingResume(false);
    }
  }

  return (
    <section className="panel smart-resume-panel">
      <div className="section-head">
        <div>
          <h2>{t("smartResume")}</h2>
          <p>{t("smartResumeIntro")}</p>
        </div>
        <span className="status">{t("resumeUsesProfile")}</span>
      </div>
      <div className="resume-source-grid">
        <article>
          <strong>{t("skills")}</strong>
          <div className="chips">{skills.length ? skills.map((skill) => <span key={skill}>{skill}</span>) : <span>{t("skills")}</span>}</div>
        </article>
        <article>
          <strong>{t("workTimeline")}</strong>
          {(me.experiences || []).length ? me.experiences.map((item) => <div className="timeline-item compact-timeline" key={item.id}><strong>{item.title}</strong><span>{item.company}{item.start_date || item.end_date ? ` · ${[item.start_date, item.is_current ? "Present" : item.end_date].filter(Boolean).join(" - ")}` : ""}</span></div>) : <p>{t("addExperience")}</p>}
        </article>
        <article>
          <strong>{t("education")}</strong>
          {(me.education || []).length ? me.education.map((item) => <div className="timeline-item compact-timeline" key={item.id}><strong>{item.degree}</strong><span>{[item.field, item.school, [item.start_year, item.end_year].filter(Boolean).join(" - ")].filter(Boolean).join(" · ")}</span></div>) : <p>{t("addEducation")}</p>}
        </article>
      </div>
      <form className="form-grid smart-resume-form" onSubmit={generateResume}>
        <label>{t("language")}<textarea rows="3" value={resumeBuilder.languages} onChange={(e) => setResumeBuilder({ ...resumeBuilder, languages: e.target.value })} /></label>
        <label className="span">{t("about")}<textarea rows="4" value={resumeBuilder.summary} onChange={(e) => setResumeBuilder({ ...resumeBuilder, summary: e.target.value })} /></label>
        <label>{t("certifications")}<textarea rows="5" value={resumeBuilder.certifications} onChange={(e) => setResumeBuilder({ ...resumeBuilder, certifications: e.target.value })} /></label>
        <label>{t("tools")}<textarea rows="5" value={resumeBuilder.tools} onChange={(e) => setResumeBuilder({ ...resumeBuilder, tools: e.target.value })} /></label>
        <label>{t("additionalInfo")}<textarea rows="5" value={resumeBuilder.additionalInfo} onChange={(e) => setResumeBuilder({ ...resumeBuilder, additionalInfo: e.target.value })} /></label>
        <button className="primary-button loading-button span" disabled={buildingResume}>{buildingResume && <span className="spinner" aria-hidden="true"></span>}{t("downloadResume")}</button>
      </form>
    </section>
  );
}

function Profile({ t, me, reload, notify }) {
  const isPremium = me.user.plan === "premium" && (!me.user.subscriptionExpiresAt || new Date(me.user.subscriptionExpiresAt) > new Date());
  const resumeLimit = isPremium ? 2 : 1;
  const certificateLimit = isPremium ? 5 : 1;
  const [form, setForm] = useState({
    fullName: me.user.fullName || "",
    phone: me.user.phone || "",
    dob: me.user.dob || "",
    headline: me.user.headline || "",
    location: me.user.location || "",
    about: me.profile?.about || "",
    skills: Array.isArray(me.profile?.skills) ? me.profile.skills : [],
    resumeEducation: me.profile?.resume_education || "",
    resumeCertifications: me.profile?.resume_certifications || "",
    resumeTools: me.profile?.resume_tools || "",
    resumeAdditionalInfo: me.profile?.resume_additional_info || ""
  });
  const [newSkill, setNewSkill] = useState("");
  const [experience, setExperience] = useState({ title: "", company: "", location: "", startDate: "", endDate: "", isCurrent: false, description: "" });
  const [editingExperienceId, setEditingExperienceId] = useState("");
  const [education, setEducation] = useState({ school: "", degree: "", field: "", startYear: "", endYear: "" });
  const [editingEducationId, setEditingEducationId] = useState("");

  async function saveProfile(event) {
    event.preventDefault();
    await api("/account/profile", {
      method: "PUT",
      body: JSON.stringify({ ...form, skills: form.skills.map((item) => item.trim()).filter(Boolean) })
    });
    await reload();
    notify?.(t("successSaved"), "success");
  }

  function updateSkill(index, value) {
    setForm({ ...form, skills: form.skills.map((skill, skillIndex) => skillIndex === index ? value : skill) });
  }

  function removeSkill(index) {
    setForm({ ...form, skills: form.skills.filter((_, skillIndex) => skillIndex !== index) });
  }

  function addSkill() {
    const skill = newSkill.trim();
    if (!skill) return;
    setForm({ ...form, skills: [...form.skills, skill] });
    setNewSkill("");
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
      notify?.(err.message, "error", err.stack || err.message);
    }
  }

  async function uploadAvatar(file) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    await api("/account/avatar", { method: "POST", body });
    await reload();
    notify?.(t("successUpdated"), "success");
  }

  async function addExperience(event) {
    event.preventDefault();
    if (!experience.title.trim() || !experience.company.trim()) return;
    try {
      if (editingExperienceId) {
        await api(`/account/experience/${editingExperienceId}`, { method: "PUT", body: JSON.stringify(experience) });
      } else {
        await api("/account/experience", { method: "POST", body: JSON.stringify(experience) });
      }
      setExperience({ title: "", company: "", location: "", startDate: "", endDate: "", isCurrent: false, description: "" });
      setEditingExperienceId("");
      await reload();
      notify?.(t("successSaved"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }

  function startEditExperience(item) {
    setEditingExperienceId(item.id);
    setExperience({
      title: item.title || "",
      company: item.company || "",
      location: item.location || "",
      startDate: item.start_date || "",
      endDate: item.end_date || "",
      isCurrent: !!item.is_current,
      description: item.description || ""
    });
  }

  function cancelEditExperience() {
    setEditingExperienceId("");
    setExperience({ title: "", company: "", location: "", startDate: "", endDate: "", isCurrent: false, description: "" });
  }

  async function removeExperience(id) {
    try {
      await api(`/account/experience/${id}`, { method: "DELETE" });
      if (editingExperienceId === id) cancelEditExperience();
      await reload();
      notify?.(t("successDeleted"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }

  async function saveEducation(event) {
    event.preventDefault();
    if (!education.school.trim() || !education.degree.trim()) return;
    try {
      if (editingEducationId) {
        await api(`/account/education/${editingEducationId}`, { method: "PUT", body: JSON.stringify(education) });
      } else {
        await api("/account/education", { method: "POST", body: JSON.stringify(education) });
      }
      setEducation({ school: "", degree: "", field: "", startYear: "", endYear: "" });
      setEditingEducationId("");
      await reload();
      notify?.(t("successSaved"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }

  function startEditEducation(item) {
    setEditingEducationId(item.id);
    setEducation({
      school: item.school || "",
      degree: item.degree || "",
      field: item.field || "",
      startYear: item.start_year || "",
      endYear: item.end_year || ""
    });
  }

  function cancelEditEducation() {
    setEditingEducationId("");
    setEducation({ school: "", degree: "", field: "", startYear: "", endYear: "" });
  }

  async function removeEducation(id) {
    try {
      await api(`/account/education/${id}`, { method: "DELETE" });
      if (editingEducationId === id) cancelEditEducation();
      await reload();
      notify?.(t("successDeleted"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }

  async function deleteAttachment(documentId) {
    await api(`/account/documents/${documentId}`, { method: "DELETE" });
    await reload();
    notify?.(t("successDeleted"), "success");
  }

  return (
    <div className="profile-page">
      <section className="profile-hero panel">
        <Avatar user={me.user} size="large" />
        <div><h1>{me.user.fullName}</h1><p>{me.user.headline}</p><span>{me.user.location}</span><span>{t("dob")}: {me.user.dob || "-"}</span>{me.user.plan === "premium" && <SubscriptionStatus user={me.user} t={t} />}</div>
      </section>
      <PlanCards t={t} currentRole={me.user.role} currentPlan={me.user.plan} subscriptionExpiresAt={me.user.subscriptionExpiresAt} notify={notify} profileMode />
      <form className="panel form-grid" onSubmit={saveProfile}>
        {["fullName", "phone", "headline", "location"].map((key) => <label key={key}>{t(key)}<input value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></label>)}
        <label>{t("dob")}<input type="date" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} /></label>
        <label className="span">{t("about")}<textarea value={form.about} onChange={(e) => setForm({ ...form, about: e.target.value })} /></label>
        <div className="span skill-editor">
          <strong>{t("skills")}</strong>
          <div className="skill-edit-list">
            {form.skills.map((skill, index) => (
              <div className="skill-edit-row" key={`${skill}-${index}`}>
                <input value={skill} onChange={(e) => updateSkill(index, e.target.value)} />
                <button className="icon-button" type="button" aria-label={t("removeAttachment")} onClick={() => removeSkill(index)}>×</button>
              </div>
            ))}
          </div>
          <div className="skill-add-row">
            <input value={newSkill} placeholder={t("skills")} onChange={(e) => setNewSkill(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addSkill(); } }} />
            <button className="secondary-button compact" type="button" onClick={addSkill}>+</button>
          </div>
        </div>
        <label>{t("certifications")}<textarea rows="5" value={form.resumeCertifications} onChange={(e) => setForm({ ...form, resumeCertifications: e.target.value })} /></label>
        <label>{t("tools")}<textarea rows="5" value={form.resumeTools} onChange={(e) => setForm({ ...form, resumeTools: e.target.value })} /></label>
        <label>{t("additionalInfo")}<textarea rows="5" value={form.resumeAdditionalInfo} onChange={(e) => setForm({ ...form, resumeAdditionalInfo: e.target.value })} /></label>
        <button className="primary-button profile-save-button">{t("editProfile")}</button>
      </form>
      <section className="panel upload-grid">
        <label>{t("profilePicture")}<input type="file" accept="image/*" onChange={(e) => uploadAvatar(e.target.files[0])} /></label>
        <label>{t("resume")}<input type="file" accept=".pdf,.doc,.docx" onChange={(e) => upload("resume", e.target.files[0])} /><span>{resumeLimit}</span></label>
        <label>{t("certificate")}<input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e) => upload("certificate", e.target.files[0])} /><span>{t("maxCertificates").replace("{count}", certificateLimit)}</span></label>
        <div className="span"><DocumentLinks t={t} documents={me.documents} avatarUrl={me.user.avatarUrl} onDelete={deleteAttachment} /></div>
      </section>
      <section className="panel">
        <h2>{t("experience")}</h2>
        <form className="row-fields" onSubmit={addExperience}>
          <input placeholder={t("title")} value={experience.title} onChange={(e) => setExperience({ ...experience, title: e.target.value })} />
          <input placeholder={t("company")} value={experience.company} onChange={(e) => setExperience({ ...experience, company: e.target.value })} />
          <input placeholder={t("location")} value={experience.location} onChange={(e) => setExperience({ ...experience, location: e.target.value })} />
          <input type="date" value={experience.startDate} onChange={(e) => setExperience({ ...experience, startDate: e.target.value })} />
          <input type="date" value={experience.endDate} disabled={experience.isCurrent} onChange={(e) => setExperience({ ...experience, endDate: e.target.value })} />
          <label className="inline-check"><input type="checkbox" checked={experience.isCurrent} onChange={(e) => setExperience({ ...experience, isCurrent: e.target.checked, endDate: e.target.checked ? "" : experience.endDate })} />{t("current")}</label>
          <textarea className="span" placeholder={t("description")} value={experience.description} onChange={(e) => setExperience({ ...experience, description: e.target.value })} />
          <button className="secondary-button">{editingExperienceId ? t("save") : t("addExperience")}</button>
          {editingExperienceId && <button className="secondary-button" type="button" onClick={cancelEditExperience}>{t("cancel")}</button>}
        </form>
        <div className="experience-edit-list">
          {me.experiences.map((item) => <div className="timeline-item experience-edit-item" key={item.id}><div><strong>{item.title}</strong><span>{item.company}{item.start_date || item.end_date ? ` · ${[item.start_date, item.is_current ? "Present" : item.end_date].filter(Boolean).join(" - ")}` : ""}</span>{item.description && <p>{item.description}</p>}</div><div className="experience-actions"><button className="secondary-button compact" type="button" onClick={() => startEditExperience(item)}>{t("editUser")}</button><button className="secondary-button compact danger-button" type="button" onClick={() => removeExperience(item.id)}>{t("delete")}</button></div></div>)}
        </div>
      </section>
      <section className="panel">
        <h2>{t("education")}</h2>
        <form className="row-fields" onSubmit={saveEducation}>
          <input placeholder={t("degree")} value={education.degree} onChange={(e) => setEducation({ ...education, degree: e.target.value })} />
          <input placeholder={t("school")} value={education.school} onChange={(e) => setEducation({ ...education, school: e.target.value })} />
          <input placeholder={t("field")} value={education.field} onChange={(e) => setEducation({ ...education, field: e.target.value })} />
          <input inputMode="numeric" placeholder={t("startYear")} value={education.startYear} onChange={(e) => setEducation({ ...education, startYear: e.target.value })} />
          <input inputMode="numeric" placeholder={t("endYear")} value={education.endYear} onChange={(e) => setEducation({ ...education, endYear: e.target.value })} />
          <button className="secondary-button">{editingEducationId ? t("save") : t("addEducation")}</button>
          {editingEducationId && <button className="secondary-button" type="button" onClick={cancelEditEducation}>{t("cancel")}</button>}
        </form>
        <div className="experience-edit-list">
          {(me.education || []).map((item) => (
            <div className="timeline-item experience-edit-item" key={item.id}>
              <div>
                <strong>{item.degree}</strong>
                <span>{[item.field, item.school, [item.start_year, item.end_year].filter(Boolean).join(" - ")].filter(Boolean).join(" · ")}</span>
              </div>
              <div className="experience-actions">
                <button className="secondary-button compact" type="button" onClick={() => startEditEducation(item)}>{t("editEducation")}</button>
                <button className="secondary-button compact danger-button" type="button" onClick={() => removeEducation(item.id)}>{t("delete")}</button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Jobs({ t, lang, jobs, documents = [], applications, interviews = [], search = "", mode = "all", setMode, selectedJobId = "", clearSelectedJob, reload }) {
  const [openJobId, setOpenJobId] = useState("");
  const [questionJobId, setQuestionJobId] = useState("");
  const [answerDrafts, setAnswerDrafts] = useState({});
  const [resumeSelections, setResumeSelections] = useState({});
  const [applyError, setApplyError] = useState("");
  const [category, setCategory] = useState("");
  const [salaryRange, setSalaryRange] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [companySearch, setCompanySearch] = useState("");
  const [page, setPage] = useState(1);
  const appliedByJob = new Map(applications.map((item) => [item.job_id, item]));
  const resumes = documents.filter((item) => item.kind === "resume");
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
      setPage(Math.max(1, Math.ceil((index + 1) / PAGE_SIZE)));
      setOpenJobId(selectedJobId);
      setTimeout(() => document.getElementById(`job-${selectedJobId}`)?.scrollIntoView({ behavior: "smooth", block: "center" }), 80);
    }
    clearSelectedJob?.();
  }, [selectedJobId]);
  const pageSize = PAGE_SIZE;
  const totalPages = Math.max(1, Math.ceil(visibleJobs.length / pageSize));
  const pagedJobs = visibleJobs.slice((page - 1) * pageSize, page * pageSize);
  async function apply(job) {
    const questions = job.screening_questions || [];
    const answers = questions.map((question) => ({ question, answer: (answerDrafts[job.id]?.[question] || "").trim() }));
    const selectedResume = resumeSelections[job.id] || resumes[0]?.id || null;
    if (questions.length && answers.some((item) => !item.answer)) {
      setQuestionJobId(job.id);
      setOpenJobId(job.id);
      setApplyError(t("answerRequired"));
      return;
    }
    await api(`/jobs/${job.id}/apply`, { method: "POST", body: JSON.stringify({ answers, resumeDocumentId: selectedResume }) });
    setQuestionJobId("");
    setApplyError("");
    await reload();
  }
  function openJobDetails(jobId) {
    setOpenJobId(jobId);
    setQuestionJobId("");
    setApplyError("");
  }
  const detailJob = openJobId ? visibleJobs.find((job) => job.id === openJobId) : null;
  if (detailJob) {
    const application = appliedByJob.get(detailJob.id);
    const applicationStatus = detailJob.applicationStatus || application?.status;
    const normalizedApplicationStatus = normalizeStatusValue(applicationStatus);
    const isScheduled = scheduledJobIds.has(detailJob.id);
    const detailFrameClass = isScheduled || normalizedApplicationStatus === "interview" ? "interview-frame" : normalizedApplicationStatus === "accepted" ? "accepted-frame" : "";
    const questions = detailJob.screening_questions || [];
    return <section className="job-detail-page">
      <button className="secondary-button compact" type="button" onClick={() => { setOpenJobId(""); setQuestionJobId(""); setApplyError(""); }}>{t("backToJobs")}</button>
      <article className={["job-card panel highlighted-job", detailFrameClass].filter(Boolean).join(" ")}>
        <div>
          <h2>{detailJob.title}</h2>
          <small className="job-public-id">{t("jobId")}: #{detailJob.job_number || "-"}</small>
          <p>{detailJob.company_name} · {jobCategoryLabel(detailJob.category, lang)} · {detailJob.location}</p>
          <span>{detailJob.salary_range}</span>
          {applicationStatus && <small className={`application-status status ${applicationStatus}`}>{t("applicationStatus")}: {statusLabel(applicationStatus, lang)}</small>}
        </div>
        <section className="job-details">
          <dl>
            <div><dt>{t("company")}</dt><dd>{detailJob.company_name}</dd></div>
            <div><dt>{t("category")}</dt><dd>{jobCategoryLabel(detailJob.category, lang)}</dd></div>
            <div><dt>{t("location")}</dt><dd>{detailJob.location}</dd></div>
            <div><dt>{t("salary")}</dt><dd>{detailJob.salary_range || "-"}</dd></div>
            <div><dt>{t("type")}</dt><dd>{detailJob.type}</dd></div>
          </dl>
          <h3>{t("description")}</h3>
          <p>{detailJob.description || "-"}</p>
        </section>
        {!applicationStatus && questionJobId !== detailJob.id && <div className="job-actions job-detail-actions">
          <button className="primary-button compact" type="button" onClick={() => { setQuestionJobId(detailJob.id); setApplyError(""); }}>{t("applyForJob")}</button>
        </div>}
        {!applicationStatus && questionJobId === detailJob.id && <section className="job-apply-questions">
          <h3>{t("apply")}</h3>
          <label>{t("chooseResume")}
            <select value={resumeSelections[detailJob.id] || resumes[0]?.id || ""} onChange={(event) => setResumeSelections({ ...resumeSelections, [detailJob.id]: event.target.value })}>
              <option value="">{resumes.length ? t("chooseResume") : t("resume")}</option>
              {resumes.map((resume) => <option value={resume.id} key={resume.id}>{resume.file_name || resume.fileName}</option>)}
            </select>
          </label>
          {questions.map((question) => <label key={question}>{question}<textarea value={answerDrafts[detailJob.id]?.[question] || ""} onChange={(event) => setAnswerDrafts({ ...answerDrafts, [detailJob.id]: { ...(answerDrafts[detailJob.id] || {}), [question]: event.target.value } })} /></label>)}
          {applyError && <p className="error">{applyError}</p>}
          <button className="primary-button compact" type="button" onClick={() => apply(detailJob)}>{t("apply")}</button>
        </section>}
      </article>
    </section>;
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
    const normalizedApplicationStatus = normalizeStatusValue(applicationStatus);
    const isScheduled = scheduledJobIds.has(job.id);
    const questions = job.screening_questions || [];
    const statusFrameClass = isScheduled || normalizedApplicationStatus === "interview" ? "interview-frame" : normalizedApplicationStatus === "accepted" ? "accepted-frame" : "";
    return <article
      id={`job-${job.id}`}
      className={["job-card panel clickable-job-card", isScheduled || openJobId === job.id ? "highlighted-job" : "", statusFrameClass].filter(Boolean).join(" ")}
      key={job.id}
      role="button"
      tabIndex={0}
      onClick={() => openJobDetails(job.id)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openJobDetails(job.id);
        }
      }}
    >
      <div>
        <h2>{job.title}</h2>
        <small className="job-public-id">{t("jobId")}: #{job.job_number || "-"}</small>
        <p>{job.company_name} · {jobCategoryLabel(job.category, lang)} · {job.location}</p>
        <span>{job.salary_range}</span>
        {isScheduled && <small className="application-status status interview">{t("upcomingInterviews")}</small>}
        {applicationStatus && <small className={`application-status status ${applicationStatus}`}>{t("applicationStatus")}: {statusLabel(applicationStatus, lang)}</small>}
      </div>
    </article>;
  }) : <article className="panel"><p>{t("noJobsMatching")}</p></article>}
    {visibleJobs.length > pageSize && <div className="pagination panel">
      <button className="secondary-button compact" type="button" disabled={page <= 1} onClick={() => setPage(page - 1)}>{t("previous")}</button>
      <span>{t("page")} {page} / {totalPages}</span>
      <button className="secondary-button compact" type="button" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>{t("next")}</button>
    </div>}
  </section>;
}

function Admin({ t, lang, session, admin, users, setUsers, jobs, courses = [], applications, setApplications, interviews = [], subscriptionRequests = [], supportThreads, initialTab, clearInitialTab, reload, openSupport, notify, withNotify }) {
  const [tab, setTab] = useState("overview");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState(null);
  const emptyUserForm = { fullName: "", email: "", password: "", phone: "", dob: "", headline: "", location: "", role: "member", plan: "free", status: "active" };
  const emptyCourseForm = { targetAudience: "all", addedById: "", title: "", provider: "", completionDate: "", certificateUrl: "", notes: "" };
  const [newUser, setNewUser] = useState(emptyUserForm);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [adminCourseForm, setAdminCourseForm] = useState(emptyCourseForm);
  const [editingCourse, setEditingCourse] = useState(null);
  const [jobAdminSearch, setJobAdminSearch] = useState("");
  const [adminPage, setAdminPage] = useState(1);
  const emptyJobForm = { companyName: "مختبرات روابط", title: "", category: "General", location: "عن بعد", type: "دوام كامل", salaryRange: "", description: "", screeningQuestions: [""] };
  const [jobForm, setJobForm] = useState(emptyJobForm);
  const [showAddJobModal, setShowAddJobModal] = useState(false);
  const [newJobAgentId, setNewJobAgentId] = useState("");
  const [editingJobAgentId, setEditingJobAgentId] = useState("");
  const [editingJob, setEditingJob] = useState(null);
  const [applicationSearch, setApplicationSearch] = useState("");
  const [interview, setInterview] = useState({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
  const [schedulingInterview, setSchedulingInterview] = useState(false);
  const unreadTotal = supportThreads.filter((thread) => Number(thread.unread_count || 0) > 0).length;
  const adminTabs = [
    ["overview", t("overview"), "▦"],
    ["users", t("userManagement"), "◎"],
    ["jobs", t("jobManagement"), "▣"],
    ["courses", t("courses"), "▤"],
    ["applications", t("applicationManagement"), "◈"],
    ["interviews", t("interviews"), "◌"],
    ["support", t("supportInbox"), "✉"]
  ];
  const normalizedJobAdminSearch = jobAdminSearch.trim().toLowerCase();
  const adminVisibleJobs = jobs.filter((job) => {
    if (!normalizedJobAdminSearch) return true;
    return `${job.job_number || ""} ${job.title || ""} ${job.company_name || ""}`.toLowerCase().includes(normalizedJobAdminSearch);
  });
  const normalizedApplicationSearch = applicationSearch.trim().toLowerCase();
  const visibleApplications = applications.filter((application) => {
    if (!normalizedApplicationSearch) return true;
    return `${application.full_name || ""} ${application.email || ""} ${application.job_title || ""} ${application.company_name || ""} ${application.job_number || ""}`.toLowerCase().includes(normalizedApplicationSearch);
  });
  const pagedSubscriptionRequests = pageItems(subscriptionRequests, adminPage);
  const pagedUsers = pageItems(users, adminPage);
  const pagedCourses = pageItems(courses, adminPage);
  const pagedAdminVisibleJobs = pageItems(adminVisibleJobs, adminPage);
  const pagedVisibleApplications = pageItems(visibleApplications, adminPage);
  const pagedInterviews = pageItems(interviews, adminPage);
  const pagedSupportThreads = pageItems(supportThreads, adminPage);
  const activeAdminTotal = tab === "overview" ? subscriptionRequests.length
    : tab === "users" ? users.length
    : tab === "courses" ? courses.length
    : tab === "jobs" ? adminVisibleJobs.length
    : tab === "applications" ? visibleApplications.length
    : tab === "interviews" ? interviews.length
    : tab === "support" ? supportThreads.length
    : 0;
  const agents = users.filter((user) => user.role === "agent");
  const isMasterAdmin = session?.role === "master_admin";
  const editableRoles = USER_ROLES.filter((role) => isMasterAdmin || role !== "master_admin");
  const selectedProfilePremium = selectedProfile?.user?.plan === "premium" && (!selectedProfile?.user?.subscription_expires_at || new Date(selectedProfile.user.subscription_expires_at) > new Date());
  const selectedProfileResumeLimit = selectedProfilePremium ? 2 : 1;
  const selectedProfileCertificateLimit = selectedProfilePremium ? 5 : 1;
  useEffect(() => {
    if (initialTab) {
      setTab(initialTab);
      clearInitialTab?.();
    }
  }, [initialTab]);
  useEffect(() => {
    setAdminPage(1);
  }, [tab, search, jobAdminSearch, applicationSearch]);
  useEffect(() => {
    if (tab !== "users") return undefined;
    const timer = setInterval(() => searchUsers(search).catch(() => {}), 8000);
    return () => clearInterval(timer);
  }, [tab, search]);
  async function searchUsers(value) {
    setSearch(value);
    setUsers(await api(`/admin/users?search=${encodeURIComponent(value)}`));
  }
  async function patchUser(user, patch) {
    await api(`/admin/users/${user.id}`, { method: "PATCH", body: JSON.stringify(patch) });
    await searchUsers(search);
    notify?.(t("successUpdated"), "success");
  }
  async function createUser(event) {
    event.preventDefault();
    try {
      await api("/admin/users", { method: "POST", body: JSON.stringify(newUser) });
      setNewUser(emptyUserForm);
      setShowAddUserModal(false);
      await reload();
      await searchUsers(search);
      notify?.(t("successCreated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }
  async function deleteUser(user) {
    if (!confirm(`Delete ${user.full_name}?`)) return;
    await api(`/admin/users/${user.id}`, { method: "DELETE" });
    await searchUsers(search);
    notify?.(t("successDeleted"), "success");
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
    notify?.(t("successUpdated"), "success");
  }
  async function uploadSelectedAttachment(kind, file) {
    if (!file || !selectedProfile) return;
    const body = new FormData();
    body.append("kind", kind);
    body.append("file", file);
    try {
      await api(`/admin/users/${selectedProfile.user.id}/documents`, { method: "POST", body });
      await refreshSelectedProfile();
      notify?.(t("successUpdated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
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
  function coursePayload(extra = {}) {
    const payload = { ...adminCourseForm, ...extra };
    if (!payload.addedById) delete payload.addedById;
    if (!payload.userId) delete payload.userId;
    if (!payload.completionDate) delete payload.completionDate;
    return payload;
  }
  async function addSelectedCourse(event) {
    event.preventDefault();
    if (!selectedProfile?.user?.id || !adminCourseForm.title) return;
    try {
      await api("/courses", { method: "POST", body: JSON.stringify(coursePayload({ targetAudience: "user", userId: selectedProfile.user.id })) });
      setAdminCourseForm(emptyCourseForm);
      await refreshSelectedProfile();
      notify?.(t("successCreated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }
  async function addAdminCourse(event) {
    event.preventDefault();
    if (!adminCourseForm.title) return;
    try {
      await api("/courses", { method: "POST", body: JSON.stringify(coursePayload()) });
      setAdminCourseForm(emptyCourseForm);
      await reload();
      notify?.(t("successCreated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }
  async function saveAdminCourse(event) {
    event.preventDefault();
    if (!editingCourse || !adminCourseForm.title) return;
    try {
      await api(`/admin/courses/${editingCourse.id}`, { method: "PATCH", body: JSON.stringify(coursePayload()) });
      setEditingCourse(null);
      setAdminCourseForm(emptyCourseForm);
      await reload();
      notify?.(t("successUpdated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
  }
  function startEditCourse(course) {
    setEditingCourse(course);
    setAdminCourseForm({
      targetAudience: course.target_audience || "all",
      addedById: course.added_by || "",
      title: course.title || "",
      provider: course.provider || "",
      completionDate: course.completion_date ? String(course.completion_date).slice(0, 10) : "",
      certificateUrl: course.certificate_url || "",
      notes: course.notes || ""
    });
  }
  function cancelEditCourse() {
    setEditingCourse(null);
    setAdminCourseForm(emptyCourseForm);
  }
  async function deleteCourse(course) {
    if (!confirm(`${t("deleteCourse")}: ${course.title}?`)) return;
    await api(`/admin/courses/${course.id}`, { method: "DELETE" });
    if (editingCourse?.id === course.id) cancelEditCourse();
    await reload();
    notify?.(t("successDeleted"), "success");
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
    await searchUsers(search);
    notify?.(t("successUpdated"), "success");
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
      screeningQuestions: questionsToArray(job.screening_questions)
    });
    setEditingJobAgentId("");
    setTimeout(() => document.getElementById("edit-job-form")?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
  }
  async function runJobAction(job, action) {
    if (!action) return;
    if (action === "edit") startEditJob(job);
    if (action === "delete") await deleteJob(job);
  }
  async function saveJob(event) {
    event.preventDefault();
    const updatedJob = await api(`/admin/jobs/${editingJob.id}`, { method: "PATCH", body: JSON.stringify({ ...editingJob, screeningQuestions: compactQuestions(editingJob.screeningQuestions) }) });
    if (editingJobAgentId) await assignJob(updatedJob, editingJobAgentId);
    setEditingJob(null);
    setEditingJobAgentId("");
    await reload();
    notify?.(t("successUpdated"), "success");
  }
  async function deleteJob(job) {
    if (!confirm(`${t("deleteJob")}: ${job.title}?`)) return;
    await api(`/admin/jobs/${job.id}`, { method: "DELETE" });
    if (editingJob?.id === job.id) setEditingJob(null);
    await reload();
    notify?.(t("successDeleted"), "success");
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
  async function assignJob(job, agentId) {
    if (!agentId) return;
    await api("/admin/job-assignments", {
      method: "POST",
      body: JSON.stringify({ jobId: job.id, agentId })
    });
    await reload();
  }
  async function addJob(event) {
    event.preventDefault();
    try {
      const createdJob = await api("/admin/jobs", { method: "POST", body: JSON.stringify({ ...jobForm, screeningQuestions: compactQuestions(jobForm.screeningQuestions) }) });
      if (newJobAgentId) await assignJob(createdJob, newJobAgentId);
      setJobForm(emptyJobForm);
      setNewJobAgentId("");
      setShowAddJobModal(false);
      await reload();
      notify?.(t("successCreated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
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
        notify?.(`${t("interviewEmailSent")} ${result.recipientEmail}`, "success");
      } else {
        notify?.(`${t("interviewEmailFailed")}: ${result.emailError || "-"}`, "error", result.emailError || "-");
      }
      setInterview({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
      await reload();
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
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
  async function updateSubscriptionRequest(request, status) {
    await api(`/admin/subscription-requests/${request.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    });
    await reload();
    notify?.(t("successUpdated"), "success");
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
              <AnalyticsList title={t("applicationOutcomes")} data={admin.analytics?.applicationOutcomes || []} labelFormatter={(label) => analyticsLabel("application", label, lang, t)} />
              <AnalyticsList title={t("jobCategories")} data={admin.analytics?.jobCategories || []} labelFormatter={(label) => analyticsLabel("category", label, lang, t)} />
              <AnalyticsList title={t("profileHealth")} data={admin.analytics?.profileHealth || []} labelFormatter={(label) => analyticsLabel("profile", label, lang, t)} />
            </section>
            <section className="panel">
              <div className="section-head"><h2>{t("planRequests")}</h2></div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>{t("users")}</th><th>{t("requestedPlan")}</th><th>{t("paymentMethod")}</th><th>{t("subscriptionStatus")}</th><th>{t("status")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>
                    {subscriptionRequests.length ? pagedSubscriptionRequests.map((request) => (
                      <tr key={request.id}>
                        <td><div className="table-user"><Avatar user={{ full_name: request.full_name }} size="small" /><div><strong>{request.full_name}</strong><span>{request.email}</span></div></div></td>
                        <td><strong>{request.requested_plan === "agent" ? t("agentPlan") : t("premiumPlan")}</strong><span className="muted-inline">{Number(request.amount).toFixed(2)} {request.currency}</span></td>
                        <td>{request.payment_method === "shamcash" ? t("shamCashPayment") : t("cashPayment")}</td>
                        <td><SubscriptionStatus user={{ plan: request.plan, subscription_expires_at: request.subscription_expires_at }} t={t} /></td>
                        <td><span className={`status ${request.status}`}>{statusLabel(request.status, lang)}</span></td>
                        <td>
                          <div className="row-actions">
                            <button className="secondary-button compact" type="button" disabled={request.status !== "pending"} onClick={() => updateSubscriptionRequest(request, "approved")}>{t("approve")}</button>
                            <button className="secondary-button compact" type="button" disabled={request.status !== "pending"} onClick={() => updateSubscriptionRequest(request, "rejected")}>{t("reject")}</button>
                          </div>
                        </td>
                      </tr>
                    )) : <tr><td colSpan="6">{t("emptyState")}</td></tr>}
                  </tbody>
                </table>
              </div>
            </section>
          </>}

          {tab === "users" && <>
            <section className="panel">
              <div className="section-head"><h2>{t("users")}</h2><div className="section-actions"><input placeholder={t("searchUsers")} value={search} onChange={(e) => searchUsers(e.target.value)} /><button className="primary-button compact" type="button" onClick={() => setShowAddUserModal(true)}>{t("addUser")}</button></div></div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>{t("users")}</th><th>{t("role")}</th><th>{t("plan")}</th><th>{t("subscriptionStatus")}</th><th>{t("status")}</th><th>{t("attachments")}</th><th>{t("lastActive")}</th><th>{t("shareWithAgent")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>{pagedUsers.map((user) => <tr key={user.id}><td><button className="table-user table-user-button" type="button" onClick={() => openUserProfile(user)}><Avatar user={user} size="small" /><div><strong>{user.full_name}</strong><span>{user.email}</span></div></button></td><td>{roleLabel(user.role, lang)}</td><td><select className="plan-select" value={user.plan || "free"} onChange={(e) => patchUser(user, { plan: e.target.value })}>{PLAN_OPTIONS.map((plan) => <option value={plan} key={plan}>{planLabel(plan, lang)}</option>)}</select></td><td><SubscriptionStatus user={user} t={t} /></td><td><span className={`status ${user.status}`}>{statusLabel(user.status, lang)}</span></td><td><DocumentLinks t={t} documents={user.documents} avatarUrl={user.avatar_url} compact /></td><td>{new Date(user.last_active_at).toLocaleDateString()}</td><td><select className="action-select" defaultValue="" disabled={!agents.length} onChange={async (e) => { await shareUser(user, e.target.value); e.target.value = ""; }}><option value="">{agents.length ? t("shareWithAgent") : t("agent")}</option>{agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}</select></td><td><select className="action-select" defaultValue="" onChange={(e) => { runUserAction(user, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option><option value="edit">{t("editUser")}</option><option value="verify">{t("verify")}</option><option value="activate">{t("activate")}</option><option value="deactivate">{t("deactivate")}</option>{(isMasterAdmin || !["admin", "master_admin"].includes(user.role)) && <option value="delete">{t("delete")}</option>}</select></td></tr>)}</tbody>
                </table>
              </div>
            </section>
            {showAddUserModal && <AdminModal title={t("addUser")} close={() => setShowAddUserModal(false)}>
              <form className="admin-form modal-form" onSubmit={createUser}>
                <input placeholder={t("fullName")} value={newUser.fullName} onChange={(e) => setNewUser({ ...newUser, fullName: e.target.value })} required />
                <input placeholder={t("email")} value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} required />
                <input type="password" placeholder={t("password")} value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} required autoComplete="new-password" />
                <input placeholder={t("phone")} value={newUser.phone} onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })} />
                <input type="date" value={newUser.dob} onChange={(e) => setNewUser({ ...newUser, dob: e.target.value })} />
                <input placeholder={t("headline")} value={newUser.headline} onChange={(e) => setNewUser({ ...newUser, headline: e.target.value })} />
                <input placeholder={t("location")} value={newUser.location} onChange={(e) => setNewUser({ ...newUser, location: e.target.value })} />
                <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>{editableRoles.map((role) => <option value={role} key={role}>{roleLabel(role, lang)}</option>)}</select>
                <select value={newUser.plan} onChange={(e) => setNewUser({ ...newUser, plan: e.target.value })}>{PLAN_OPTIONS.map((plan) => <option value={plan} key={plan}>{planLabel(plan, lang)}</option>)}</select>
                <select value={newUser.status} onChange={(e) => setNewUser({ ...newUser, status: e.target.value })}>{USER_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select>
                <div className="modal-actions"><button className="secondary-button" type="button" onClick={() => setShowAddUserModal(false)}>{t("cancel")}</button><button className="primary-button">{t("addUser")}</button></div>
              </form>
            </AdminModal>}
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
                <select value={editing.role} onChange={(e) => setEditing({ ...editing, role: e.target.value })}>{editableRoles.map((role) => <option value={role} key={role}>{roleLabel(role, lang)}</option>)}</select>
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
                <div className="span admin-subscription-inline"><strong>{t("subscriptionStatus")}</strong><SubscriptionStatus user={selectedProfile.user} t={t} /></div>
                <textarea value={selectedProfile.profile?.about || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, profile: { ...(selectedProfile.profile || {}), about: e.target.value } })} placeholder={t("about")} />
                <input value={Array.isArray(selectedProfile.profile?.skills) ? selectedProfile.profile.skills.join(", ") : selectedProfile.profile?.skills || ""} onChange={(e) => setSelectedProfile({ ...selectedProfile, profile: { ...(selectedProfile.profile || {}), skills: e.target.value } })} placeholder={t("skills")} />
                <div className="row-fields">
                  <select value={selectedProfile.user.role} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, role: e.target.value } })}>{editableRoles.map((role) => <option value={role} key={role}>{roleLabel(role, lang)}</option>)}</select>
                  <select value={selectedProfile.user.status} onChange={(e) => setSelectedProfile({ ...selectedProfile, user: { ...selectedProfile.user, status: e.target.value } })}>{USER_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select>
                  <button className="primary-button">{t("save")}</button>
                </div>
              </form>
              <section className="panel admin-form">
                <h2>{t("attachments")}</h2>
                <label>{t("profilePicture")}<input type="file" accept="image/*" onChange={(e) => uploadSelectedAvatar(e.target.files[0])} /></label>
                <label>{t("resume")}<input type="file" accept=".pdf,.doc,.docx" onChange={(e) => uploadSelectedAttachment("resume", e.target.files[0])} /><span>{selectedProfileResumeLimit}</span></label>
                <label>{t("certificate")}<input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e) => uploadSelectedAttachment("certificate", e.target.files[0])} /><span>{t("maxCertificates").replace("{count}", selectedProfileCertificateLimit)}</span></label>
                <DocumentLinks t={t} documents={selectedProfile.documents} avatarUrl={selectedProfile.user.avatar_url} onDelete={deleteSelectedAttachment} />
              </section>
              <section className="panel admin-profile-applications">
                <div className="section-head">
                  <h2>{t("appliedJobs")}</h2>
                  <span className="status">{selectedProfile.applications?.length || 0}</span>
                </div>
                <div className="profile-application-list">
                  {(selectedProfile.applications || []).length ? selectedProfile.applications.map((application) => (
                    <article className="profile-application-row" key={application.id}>
                      <div>
                        <strong>{application.job_title}</strong>
                        <span>#{application.job_number || "-"} · {application.company_name} · {application.location || "-"}</span>
                        <small>{application.salary_range || "-"} · {new Date(application.created_at).toLocaleDateString()}</small>
                        <small>{t("resume")}: <ApplicationResumeLink application={application} t={t} /></small>
                      </div>
                      <b className={`status ${normalizeStatusValue(application.status)}`}>{statusLabel(normalizeStatusValue(application.status), lang)}</b>
                    </article>
                  )) : <p>{t("noAppliedJobs")}</p>}
                </div>
              </section>
            </section>
            <section className="panel">
              <h2>{t("about")}</h2>
              <p>{selectedProfile.profile?.about || "-"}</p>
              <div className="chips">{(Array.isArray(selectedProfile.profile?.skills) ? selectedProfile.profile.skills : String(selectedProfile.profile?.skills || "").split(",").map((item) => item.trim()).filter(Boolean)).map((skill) => <span key={skill}>{skill}</span>)}</div>
            </section>
            <section className="panel">
              <h2>{t("experience")}</h2>
              {(selectedProfile.experiences || []).map((item) => <div className="timeline-item" key={item.id}><strong>{item.title}</strong><span>{item.company}</span></div>)}
            </section>
          </section>}

          {tab === "courses" && <section className="panel course-admin-panel">
            <div className="section-head">
              <div>
                <h2>{editingCourse ? t("editCourse") : t("addCourse")}</h2>
                <p>{t("courseAudience")} · {t("courseOwner")}: {t("adminDefault")}</p>
              </div>
            </div>
            <form className="admin-form course-admin-form" onSubmit={editingCourse ? saveAdminCourse : addAdminCourse}>
              <select value={adminCourseForm.targetAudience} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, targetAudience: e.target.value })}>
                <option value="all">{t("allUsers")}</option>
                <option value="premium">{t("premiumUsers")}</option>
                <option value="agents">{t("agents")}</option>
              </select>
              <select value={adminCourseForm.addedById} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, addedById: e.target.value })}>
                <option value="">{t("adminDefault")}</option>
                {agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}
              </select>
              <input placeholder={t("title")} value={adminCourseForm.title} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, title: e.target.value })} required />
              <input placeholder={t("provider")} value={adminCourseForm.provider} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, provider: e.target.value })} />
              <input type="date" value={adminCourseForm.completionDate} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, completionDate: e.target.value })} />
              <input placeholder={t("courseLink")} value={adminCourseForm.certificateUrl} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, certificateUrl: e.target.value })} />
              <textarea className="span" placeholder={t("notes")} value={adminCourseForm.notes} onChange={(e) => setAdminCourseForm({ ...adminCourseForm, notes: e.target.value })} />
              <button className="primary-button">{editingCourse ? t("save") : t("addCourse")}</button>
              {editingCourse && <button className="secondary-button" type="button" onClick={cancelEditCourse}>{t("cancel")}</button>}
            </form>
            <section className="course-admin-list">
              <div className="section-head">
                <h2>{t("courses")}</h2>
                <span className="status">{courses.length}</span>
              </div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>{t("title")}</th><th>{t("courseAudience")}</th><th>{t("courseOwner")}</th><th>{t("provider")}</th><th>{t("courseLink")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>{pagedCourses.map((course) => (
                    <tr key={course.id}>
                      <td><strong>{course.title}</strong>{course.notes && <span>{course.notes}</span>}</td>
                      <td>{course.target_audience === "premium" ? t("premiumUsers") : course.target_audience === "agents" ? t("agents") : course.target_audience === "user" ? course.user_name || t("users") : t("allUsers")}</td>
                      <td>{course.owner_name || t("adminDefault")}</td>
                      <td>{course.provider || "-"}</td>
                      <td>{course.certificate_url ? <a href={assetUrl(course.certificate_url)} target="_blank" rel="noreferrer">{t("seeCourse")}</a> : "-"}</td>
                      <td><select className="action-select" defaultValue="" onChange={(e) => { if (e.target.value === "edit") startEditCourse(course); if (e.target.value === "delete") deleteCourse(course); e.target.value = ""; }}><option value="">{t("chooseAction")}</option><option value="edit">{t("editCourse")}</option><option value="delete">{t("deleteCourse")}</option></select></td>
                    </tr>
                  ))}</tbody>
                </table>
              </div>
            </section>
          </section>}

          {tab === "jobs" && <section className="job-admin-grid">
            <div className="section-head panel job-admin-toolbar">
              <h2>{t("jobManagement")}</h2>
              <button className="primary-button compact" type="button" onClick={() => setShowAddJobModal(true)}>{t("addJob")}</button>
            </div>
            {showAddJobModal && <AdminModal title={t("addJob")} close={() => setShowAddJobModal(false)}>
              <form className="admin-form job-editor-form modal-job-form" onSubmit={addJob}>
                <input placeholder={t("company")} value={jobForm.companyName} onChange={(e) => setJobForm({ ...jobForm, companyName: e.target.value })} />
                <input placeholder={t("title")} value={jobForm.title} onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })} />
                <select value={jobForm.category} onChange={(e) => setJobForm({ ...jobForm, category: e.target.value })}>
                  {JOB_CATEGORIES.map((item) => <option value={item.value} key={item.value}>{item[lang]}</option>)}
                </select>
                <input placeholder={t("location")} value={jobForm.location} onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })} />
                <input placeholder={t("salary")} value={jobForm.salaryRange} onChange={(e) => setJobForm({ ...jobForm, salaryRange: e.target.value })} />
                <select value={newJobAgentId} onChange={(e) => setNewJobAgentId(e.target.value)}>
                  <option value="">{agents.length ? t("assignJob") : t("agent")}</option>
                  {agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}
                </select>
                <textarea placeholder={t("description")} value={jobForm.description} onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })} />
                <QuestionRows t={t} questions={jobForm.screeningQuestions} onChange={(screeningQuestions) => setJobForm({ ...jobForm, screeningQuestions })} />
                <div className="modal-actions"><button className="secondary-button" type="button" onClick={() => setShowAddJobModal(false)}>{t("cancel")}</button><button className="primary-button">{t("addJob")}</button></div>
              </form>
            </AdminModal>}

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
              <select value={editingJobAgentId} onChange={(e) => setEditingJobAgentId(e.target.value)}>
                <option value="">{agents.length ? t("assignJob") : t("agent")}</option>
                {agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}
              </select>
              <textarea placeholder={t("description")} value={editingJob.description} onChange={(e) => setEditingJob({ ...editingJob, description: e.target.value })} />
              <QuestionRows t={t} questions={editingJob.screeningQuestions || [""]} onChange={(screeningQuestions) => setEditingJob({ ...editingJob, screeningQuestions })} />
              <div className="row-fields">
                <button className="primary-button">{t("save")}</button>
                <button className="secondary-button" type="button" onClick={() => setEditingJob(null)}>{t("cancel")}</button>
              </div>
            </form>}

            <section className="panel span-two job-management-card">
              <div className="section-head"><h2>{t("jobManagement")}</h2><input placeholder={t("searchJobs")} value={jobAdminSearch} onChange={(e) => setJobAdminSearch(e.target.value)} /><span className="status">{adminVisibleJobs.length}</span></div>
              <div className="table-wrap job-table-wrap">
                <table>
                  <thead><tr><th>{t("jobId")}</th><th>{t("job")}</th><th>{t("category")}</th><th>{t("location")}</th><th>{t("assignedAgents")}</th><th>{t("status")}</th><th>{t("assignJob")}</th><th>{t("actions")}</th></tr></thead>
                  <tbody>{pagedAdminVisibleJobs.map((job) => <tr key={job.id}>
                    <td><strong className="job-number">#{job.job_number || "-"}</strong></td>
                    <td><strong>{job.title}</strong><span>{job.company_name}</span></td>
                    <td>{jobCategoryLabel(job.category, lang)}</td>
                    <td>{job.location}</td>
                    <td>{(Array.isArray(job.assigned_agents) ? job.assigned_agents : []).map((agent) => agent.full_name).join(", ") || "-"}</td>
                    <td><span className={`status ${job.status}`}>{statusLabel(job.status, lang)}</span></td>
                    <td><select className="action-select" defaultValue="" disabled={!agents.length} onChange={async (e) => { await assignJob(job, e.target.value); e.target.value = ""; }}><option value="">{agents.length ? t("assignJob") : t("agent")}</option>{agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}</select></td>
                    <td><select className="action-select" defaultValue="" onChange={(e) => { runJobAction(job, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option><option value="edit">{t("editJob")}</option><option value="delete">{t("deleteJob")}</option></select></td>
                  </tr>)}</tbody>
                </table>
              </div>
            </section>
          </section>}

          {tab === "applications" && <section className="panel">
            <div className="section-head"><h2>{t("applications")}</h2><div className="section-actions"><input placeholder={t("searchApplications")} value={applicationSearch} onChange={(e) => setApplicationSearch(e.target.value)} /><span className="status">{visibleApplications.length}</span></div></div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>{t("applicant")}</th><th>{t("job")}</th><th>{t("location")}</th><th>{t("resume")}</th><th>{t("submittedAnswers")}</th><th>{t("applicationStatus")}</th><th>{t("shareWithAgent")}</th><th>{t("actions")}</th></tr></thead>
                <tbody>{pagedVisibleApplications.map((application) => <tr key={application.id}><td><button className="table-user table-user-button" type="button" onClick={() => openUserProfile({ id: application.user_id })}><Avatar user={{ full_name: application.full_name, avatar_url: application.avatar_url, plan: application.plan, last_active_at: application.last_active_at }} size="small" /><div><strong>{application.full_name}</strong><span>{application.email}</span></div></button></td><td><strong>{application.job_title}</strong><span>#{application.job_number || "-"} · {application.company_name}</span></td><td>{application.location}</td><td><ApplicationResumeLink application={application} t={t} /></td><td><ApplicationAnswers t={t} answers={application.screening_answers} /></td><td><span className={`status ${application.status}`}>{statusLabel(application.status, lang)}</span></td><td><select className="action-select" defaultValue="" disabled={!agents.length} onChange={async (e) => { await shareApplication(application, e.target.value); e.target.value = ""; }}><option value="">{agents.length ? t("shareWithAgent") : t("agent")}</option>{agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.full_name}</option>)}</select></td><td><select className="action-select" defaultValue="" onChange={(e) => { updateApplicationStatus(application, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option>{APPLICATION_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select></td></tr>)}</tbody>
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
                {interviews.length ? pagedInterviews.map((item) => <article className="interview-admin-item" key={item.id}>
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
              {pagedSupportThreads.map((thread) => <article className={Number(thread.unread_count) > 0 ? "support-thread unread" : "support-thread"} key={thread.user_id}>
                <Avatar user={{ full_name: thread.full_name, avatar_url: thread.avatar_url, plan: thread.plan, last_active_at: thread.last_active_at }} size="small" />
                <div><strong>{thread.full_name}</strong><span>{thread.email}</span><p>{thread.last_message}</p></div>
                <div className="support-thread-actions">{Number(thread.unread_count) > 0 && <b>{thread.unread_count}</b>}<button className="secondary-button compact" onClick={() => openSupport(thread.user_id)}>{t("openChat")}</button></div>
              </article>)}
            </div>
          </section>}
          <PaginationControls t={t} page={adminPage} total={activeAdminTotal} setPage={setAdminPage} />
        </div>
      </section>
    </div>
  );
}

function AgentWorkspace({ t, lang, agent, profile = {}, shares = [], users = [], interviews = [], jobs = [], view = "agent", setView, reload, notify, openAgentChat, openAdminChat }) {
  const [tab, setTab] = useState("profile");
  const [selectedShareId, setSelectedShareId] = useState("");
  const [selectedJob, setSelectedJob] = useState(null);
  const [chatUserId, setChatUserId] = useState("");
  const [interview, setInterview] = useState({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
  const [agentProfileForm, setAgentProfileForm] = useState({ headline: agent?.headline || "", location: agent?.location || "", about: profile?.about || "", agencyName: profile?.agency_name || "", agencyAbout: profile?.agency_about || "", website: profile?.website || "" });
  const [courseForm, setCourseForm] = useState({ userId: "", title: "", provider: "", completionDate: "", certificateUrl: "", notes: "" });
  const agentCompanyName = profile?.agency_name || agent?.full_name || "";
  const emptyAgentJobForm = { companyName: agentCompanyName, title: "", category: "General", location: agent?.location || "عن بعد", type: "دوام كامل", salaryRange: "", description: "", status: "active", screeningQuestions: [""] };
  const [agentJobForm, setAgentJobForm] = useState(emptyAgentJobForm);
  const [showAddJobModal, setShowAddJobModal] = useState(false);
  const [schedulingInterview, setSchedulingInterview] = useState(false);
  const [agentPage, setAgentPage] = useState(1);
  const userDirectory = Array.from(new Map([...shares, ...users].map((share) => [share.user_id, share])).values());
  const selectedShare = [...shares, ...users].find((share) => share.share_id === selectedShareId);
  const applicationShares = shares.filter((share) => share.share_type === "application");
  const uniqueCandidates = userDirectory;
  const pagedAgentJobs = pageItems(jobs, agentPage);
  const pagedUniqueCandidates = pageItems(uniqueCandidates, agentPage);
  const pagedApplicationShares = pageItems(applicationShares, agentPage);
  const pagedAgentInterviews = pageItems(interviews, agentPage);
  const activeAgentTotal = tab === "jobs" ? jobs.length
    : tab === "users" ? uniqueCandidates.length
    : tab === "applications" ? applicationShares.length
    : tab === "interviews" ? interviews.length
    : 0;
  const statusCounts = APPLICATION_STATUSES.map((status) => ({
    label: statusLabel(status, lang),
    value: applicationShares.filter((share) => normalizeStatusValue(share.application_status) === status).length
  })).filter((item) => item.value > 0);
  const activityData = [
    { label: t("users"), value: uniqueCandidates.length },
    { label: t("managedApplications"), value: applicationShares.length },
    { label: t("scheduledInterviews"), value: interviews.length },
    { label: t("assignedJobs"), value: jobs.length }
  ];
  const agentTabs = [
    ["profile", t("profile"), "◉"],
    ["overview", t("overview"), "▦"],
    ["jobs", t("assignedJobs"), "▣"],
    ["users", t("users"), "◎"],
    ["applications", t("applications"), "◈"],
    ["chat", t("agentChat"), "✉"],
    ["courses", t("courses"), "▤"],
    ["schedule", t("scheduleInterview"), "◌"],
    ["interviews", t("scheduledInterviews"), "▣"]
  ];
  useEffect(() => {
    const viewTabMap = {
      agent: "overview",
      "agent-jobs": "jobs",
      "agent-users": "users",
      "agent-applications": "applications",
      "agent-chat": "chat",
      "agent-interviews": "interviews"
    };
    if (viewTabMap[view] && viewTabMap[view] !== tab) setTab(viewTabMap[view]);
  }, [view]);
  useEffect(() => {
    setAgentPage(1);
  }, [tab]);
  function selectAgentTab(id) {
    setTab(id);
    const tabViewMap = {
      overview: "agent",
      jobs: "agent-jobs",
      users: "agent-users",
      applications: "agent-applications",
      chat: "agent-chat",
      interviews: "agent-interviews"
    };
    if (tabViewMap[id]) setView?.(tabViewMap[id]);
  }
  async function refreshAgent() {
    await reload?.();
  }
  async function saveAgentProfile(event) {
    event.preventDefault();
    await api("/agent/profile", { method: "PUT", body: JSON.stringify(agentProfileForm) });
    await refreshAgent();
  }
  async function uploadAgentAvatar(file) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    await api("/account/avatar", { method: "POST", body });
    await refreshAgent();
  }
  async function addCourse(event) {
    event.preventDefault();
    if (!courseForm.userId || !courseForm.title) return;
    await api("/courses", { method: "POST", body: JSON.stringify(courseForm) });
    setCourseForm({ userId: "", title: "", provider: "", completionDate: "", certificateUrl: "", notes: "" });
    await refreshAgent();
  }
  async function addAgentJob(event) {
    event.preventDefault();
    try {
      await api("/agent/jobs", { method: "POST", body: JSON.stringify({ ...agentJobForm, screeningQuestions: compactQuestions(agentJobForm.screeningQuestions) }) });
      setAgentJobForm(emptyAgentJobForm);
      setShowAddJobModal(false);
      await refreshAgent();
      notify?.(t("successCreated"), "success");
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    }
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
      setTab("schedule");
      setTimeout(() => document.getElementById("agent-schedule-interview-form")?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
      return;
    }
    await api(`/agent/applications/${application.application_id}`, { method: "PATCH", body: JSON.stringify({ status: nextStatus }) });
    await refreshAgent();
  }
  async function updateInterviewStatus(item, status) {
    const nextStatus = normalizeStatusValue(status);
    if (!nextStatus) return;
    await api(`/agent/interviews/${item.id}`, { method: "PATCH", body: JSON.stringify({ status: nextStatus }) });
    await refreshAgent();
  }
  async function scheduleInterview(event) {
    event.preventDefault();
    if (!interview.userId || !interview.scheduledAt) return;
    setSchedulingInterview(true);
    try {
      const result = await api("/agent/interviews", {
        method: "POST",
        body: JSON.stringify({ ...interview, jobId: interview.jobId || null })
      });
      if (result.emailSent) {
        notify?.(`${t("interviewEmailSent")} ${result.recipientEmail}`, "success");
      } else {
        notify?.(`${t("interviewEmailFailed")}: ${result.emailError || "-"}`, "error", result.emailError || "-");
      }
      setInterview({ userId: "", jobId: "", scheduledAt: "", channel: "Video call", notes: "" });
      await refreshAgent();
    } catch (err) {
      notify?.(err.message, "error", err.stack || err.message);
    } finally {
      setSchedulingInterview(false);
    }
  }
  function startScheduleForShare(share) {
    setInterview({
      userId: share.user_id,
      jobId: share.job_id || "",
      scheduledAt: "",
      channel: interview.channel || "Video call",
      notes: share.job_title ? `${share.full_name} - ${share.job_title}` : share.full_name
    });
    setTab("schedule");
  }
  if (selectedShare) {
    const skills = Array.isArray(selectedShare.skills) ? selectedShare.skills : [];
    const experiences = Array.isArray(selectedShare.experiences) ? selectedShare.experiences : [];
    const isApplicationShare = selectedShare.share_type === "application";
    return (
      <section className="agent-page">
        <div className="section-head">
          <div>
            <h2>{selectedShare.full_name}</h2>
            <p>{selectedShare.email}</p>
          </div>
          <div className="section-actions">
            <button className="secondary-button compact" type="button" onClick={() => { setChatUserId(selectedShare.user_id); setSelectedShareId(""); selectAgentTab("chat"); }}>{t("message")}</button>
            <button className="secondary-button compact" type="button" onClick={() => setSelectedShareId("")}>{t("backToUsers")}</button>
          </div>
        </div>
        <article className="panel agent-share-card">
          <header className="agent-profile-head">
            <Avatar user={{ full_name: selectedShare.full_name, avatar_url: selectedShare.avatar_url, plan: selectedShare.plan, last_active_at: selectedShare.last_active_at }} size="large" />
            <div>
              <h2>{selectedShare.full_name}</h2>
              <p>{selectedShare.headline || "-"}</p>
              <span>{selectedShare.user_location || "-"}</span>
              {selectedShare.plan === "premium" && <SubscriptionStatus user={selectedShare} t={t} />}
            </div>
            <div className="agent-job-summary">
              {isApplicationShare ? <>
                <strong>{selectedShare.job_title}</strong>
                <span>{t("jobId")}: #{selectedShare.job_number || "-"}</span>
                <span>{selectedShare.company_name} · {selectedShare.salary_range || "-"}</span>
                <span>{t("resume")}: <ApplicationResumeLink application={selectedShare} t={t} /></span>
                <b className={`status ${selectedShare.application_status}`}>{statusLabel(selectedShare.application_status, lang)}</b>
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
                <div><dt>{t("phone")}</dt><dd>{selectedShare.phone || "-"}</dd></div>
                <div><dt>{t("dob")}</dt><dd>{selectedShare.dob || "-"}</dd></div>
                <div><dt>{t("location")}</dt><dd>{selectedShare.user_location || "-"}</dd></div>
                <div><dt>{t("about")}</dt><dd>{selectedShare.about || "-"}</dd></div>
              </dl>
              <div className="chips">{skills.length ? skills.map((skill) => <span key={skill}>{skill}</span>) : <span>{t("skills")}</span>}</div>
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
              <p className="muted-text">{t("resume")}: <ApplicationResumeLink application={selectedShare} t={t} /></p>
              <ApplicationAnswers t={t} answers={selectedShare.screening_answers} />
            </section>}
          </div>
        </article>
      </section>
    );
  }

  return (
    <section className="agent-page admin-page">
      <section className="admin-heading"><div><p>{t("agent")}</p><h1>{t("agentWorkspace")}</h1></div><button className="primary-button">{t("agentTools")}</button></section>
      <section className="admin-console">
        <aside className="admin-menu panel">
          {agentTabs.map(([id, label, icon]) => <button className={tab === id ? "active" : ""} type="button" onClick={() => selectAgentTab(id)} key={id}><span>{icon}</span>{label}</button>)}
        </aside>
        <div className="admin-content">
          {tab === "profile" && <section className="admin-profile-view">
            <section className="profile-hero panel">
              <Avatar user={agent} size="large" />
              <div><h1>{profile?.agency_name || agent?.full_name || t("agent")}</h1><p>{agent?.headline || t("agentWorkspace")}</p><span>{agent?.email}</span>{agent?.plan === "premium" && <SubscriptionStatus user={agent} t={t} />}</div>
            </section>
            <PlanCards t={t} currentRole={agent?.role} currentPlan={agent?.plan} subscriptionExpiresAt={agent?.subscriptionExpiresAt} notify={notify} profileMode />
            <section className="panel admin-form">
              <h2>{t("profilePicture")}</h2>
              <label>{t("profilePicture")}<input type="file" accept="image/*" onChange={(e) => uploadAgentAvatar(e.target.files[0])} /></label>
            </section>
            <form className="panel form-grid" onSubmit={saveAgentProfile}>
              <h2 className="span">{t("profileDetails")}</h2>
              <label>{t("agencyName")}<input value={agentProfileForm.agencyName} onChange={(e) => setAgentProfileForm({ ...agentProfileForm, agencyName: e.target.value })} /></label>
              <label>{t("headline")}<input value={agentProfileForm.headline} onChange={(e) => setAgentProfileForm({ ...agentProfileForm, headline: e.target.value })} /></label>
              <label>{t("location")}<input value={agentProfileForm.location} onChange={(e) => setAgentProfileForm({ ...agentProfileForm, location: e.target.value })} /></label>
              <label>{t("website")}<input value={agentProfileForm.website} onChange={(e) => setAgentProfileForm({ ...agentProfileForm, website: e.target.value })} /></label>
              <label className="span">{t("agencyAbout")}<textarea value={agentProfileForm.agencyAbout} onChange={(e) => setAgentProfileForm({ ...agentProfileForm, agencyAbout: e.target.value })} /></label>
              <button className="primary-button">{t("save")}</button>
            </form>
            <section className="metric-grid">
              <Metric label={t("users")} value={uniqueCandidates.length} />
              <Metric label={t("managedApplications")} value={applicationShares.length} />
              <Metric label={t("scheduledInterviews")} value={interviews.length} />
              <Metric label={t("assignedJobs")} value={jobs.length} />
            </section>
          </section>}

          {tab === "overview" && <>
            <section className="metric-grid">
              <Metric label={t("users")} value={uniqueCandidates.length} />
              <Metric label={t("managedApplications")} value={applicationShares.length} />
              <Metric label={t("scheduledInterviews")} value={interviews.length} />
              <Metric label={t("assignedJobs")} value={jobs.length} />
            </section>
            <section className="analytics-grid">
              <AnalyticsList title={t("applicationOutcomes")} data={statusCounts} />
              <AnalyticsBars title={t("agentActivity")} data={activityData} />
              <article className="panel">
                <h2>{t("agentTools")}</h2>
                <div className="agent-tool-list">
                  <button className="secondary-button" type="button" onClick={() => setTab("users")}>{t("users")}</button>
                  <button className="secondary-button" type="button" onClick={() => setTab("applications")}>{t("applications")}</button>
                  <button className="secondary-button" type="button" onClick={openAdminChat}>{t("adminChat")}</button>
                  <button className="secondary-button" type="button" onClick={() => setTab("schedule")}>{t("scheduleInterview")}</button>
                </div>
              </article>
            </section>
          </>}

          {tab === "jobs" && <section className="panel">
            <div className="section-head"><h2>{t("assignedJobs")}</h2><div className="section-actions"><button className="primary-button compact" type="button" onClick={() => setShowAddJobModal(true)}>{t("addJob")}</button><span className="status">{jobs.length}</span></div></div>
            {showAddJobModal && <AdminModal title={t("addJob")} close={() => setShowAddJobModal(false)}>
              <form className="admin-form job-editor-form modal-job-form" onSubmit={addAgentJob}>
                <label className="readonly-field">{t("company")}<span>{agentCompanyName || "-"}</span></label>
                <input placeholder={t("title")} value={agentJobForm.title} onChange={(e) => setAgentJobForm({ ...agentJobForm, title: e.target.value })} />
                <select value={agentJobForm.category} onChange={(e) => setAgentJobForm({ ...agentJobForm, category: e.target.value })}>
                  {JOB_CATEGORIES.map((item) => <option value={item.value} key={item.value}>{item[lang]}</option>)}
                </select>
                <input placeholder={t("location")} value={agentJobForm.location} onChange={(e) => setAgentJobForm({ ...agentJobForm, location: e.target.value })} />
                <input placeholder={t("type")} value={agentJobForm.type} onChange={(e) => setAgentJobForm({ ...agentJobForm, type: e.target.value })} />
                <input placeholder={t("salary")} value={agentJobForm.salaryRange} onChange={(e) => setAgentJobForm({ ...agentJobForm, salaryRange: e.target.value })} />
                <select value={agentJobForm.status} onChange={(e) => setAgentJobForm({ ...agentJobForm, status: e.target.value })}>{JOB_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select>
                <textarea placeholder={t("description")} value={agentJobForm.description} onChange={(e) => setAgentJobForm({ ...agentJobForm, description: e.target.value })} />
                <QuestionRows t={t} questions={agentJobForm.screeningQuestions} onChange={(screeningQuestions) => setAgentJobForm({ ...agentJobForm, screeningQuestions })} />
                <div className="modal-actions"><button className="secondary-button" type="button" onClick={() => setShowAddJobModal(false)}>{t("cancel")}</button><button className="primary-button">{t("addJob")}</button></div>
              </form>
            </AdminModal>}
            {selectedJob && <article className="panel agent-job-detail">
              <div className="section-head">
                <div><h2>{selectedJob.title}</h2><p>#{selectedJob.job_number || "-"} · {selectedJob.company_name}</p></div>
                <button className="icon-button job-detail-close" type="button" aria-label={t("cancel")} title={t("cancel")} onClick={() => setSelectedJob(null)}>×</button>
              </div>
              <dl className="profile-facts">
                <div><dt>{t("category")}</dt><dd>{jobCategoryLabel(selectedJob.category, lang)}</dd></div>
                <div><dt>{t("location")}</dt><dd>{selectedJob.location || "-"}</dd></div>
                <div><dt>{t("type")}</dt><dd>{selectedJob.type || "-"}</dd></div>
                <div><dt>{t("salary")}</dt><dd>{selectedJob.salary_range || "-"}</dd></div>
                <div><dt>{t("status")}</dt><dd><span className={`status ${selectedJob.status}`}>{statusLabel(selectedJob.status, lang)}</span></dd></div>
              </dl>
              <p>{selectedJob.description || "-"}</p>
              <div>
                <h3>{t("screeningQuestions")}</h3>
                <ul className="plain-list">{questionsToArray(selectedJob.screening_questions).filter(Boolean).map((question) => <li key={question}>{question}</li>)}</ul>
              </div>
            </article>}
            <div className="admin-post-list">
              {jobs.length ? pagedAgentJobs.map((job) => (
                <article className="admin-post agent-assigned-job" key={job.id}>
                  <strong>{job.title}</strong>
                  <span>#{job.job_number || "-"} · {job.company_name} · {job.salary_range || "-"}</span>
                  <p>{job.description || "-"}</p>
                  <button className="secondary-button compact" type="button" onClick={() => setSelectedJob(job)}>{t("jobDetails")}</button>
                </article>
              )) : <p>{t("noJobsMatching")}</p>}
            </div>
          </section>}

          {tab === "users" && <section className="panel">
            <div className="section-head"><h2>{t("users")}</h2><span className="status">{uniqueCandidates.length}</span></div>
            {uniqueCandidates.length ? <div className="table-wrap">
              <table>
                <thead><tr><th>{t("users")}</th><th>{t("title")}</th><th>{t("location")}</th><th>{t("plan")}</th><th>{t("attachments")}</th><th>{t("lastActive")}</th><th>{t("message")}</th></tr></thead>
                <tbody>{pagedUniqueCandidates.map((share) => (
                  <tr key={share.share_id}>
                    <td><button className="table-user table-user-button" type="button" onClick={() => setSelectedShareId(share.share_id)}><Avatar user={{ full_name: share.full_name, avatar_url: share.avatar_url, plan: share.plan, last_active_at: share.last_active_at }} size="small" /><div><strong>{share.full_name}</strong><span>{share.email}</span></div></button></td>
                    <td>{share.headline || share.job_title || "-"}</td>
                    <td>{share.user_location || "-"}</td>
                    <td>{planLabel(share.plan || "free", lang)}</td>
                    <td><DocumentLinks t={t} documents={share.documents} avatarUrl={share.avatar_url} compact /></td>
                    <td>{share.last_active_at ? new Date(share.last_active_at).toLocaleDateString() : "-"}</td>
                    <td><button className="secondary-button compact" type="button" onClick={() => { setChatUserId(share.user_id); selectAgentTab("chat"); }}>{t("message")}</button></td>
                  </tr>
                ))}</tbody>
              </table>
            </div> : <p>{t("noSharedProfiles")}</p>}
          </section>}

          {tab === "applications" && <section className="panel">
            <div className="section-head"><h2>{t("applications")}</h2><span className="status">{applicationShares.length}</span></div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>{t("applicant")}</th><th>{t("job")}</th><th>{t("resume")}</th><th>{t("submittedAnswers")}</th><th>{t("applicationStatus")}</th><th>{t("actions")}</th></tr></thead>
                <tbody>{pagedApplicationShares.map((application) => (
                  <tr key={application.share_id}>
                    <td><div className="table-user"><Avatar user={{ full_name: application.full_name, avatar_url: application.avatar_url, plan: application.plan, last_active_at: application.last_active_at }} size="small" /><div><button className="link-button" type="button" onClick={() => setSelectedShareId(application.share_id)}>{application.full_name}</button><span>{application.email}</span></div></div></td>
                    <td><strong>{application.job_title}</strong><span>#{application.job_number || "-"} · {application.company_name}</span></td>
                    <td><ApplicationResumeLink application={application} t={t} /></td>
                    <td><ApplicationAnswers t={t} answers={application.screening_answers} /></td>
                    <td><span className={`status ${application.application_status}`}>{statusLabel(application.application_status, lang)}</span></td>
                    <td><select className="action-select" defaultValue="" onChange={(e) => { updateApplicationStatus(application, e.target.value); e.target.value = ""; }}><option value="">{t("chooseAction")}</option>{APPLICATION_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}</select></td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          </section>}

          {tab === "chat" && <AgentChatPanel t={t} users={uniqueCandidates} initialUserId={chatUserId} />}

          {tab === "schedule" && <form id="agent-schedule-interview-form" className="panel admin-form" onSubmit={scheduleInterview}>
            <h2>{t("scheduleInterview")}</h2>
            <select value={interview.userId} onChange={(e) => setInterview({ ...interview, userId: e.target.value, jobId: "" })}><option value="">{t("users")}</option>{uniqueCandidates.map((share) => <option key={share.user_id} value={share.user_id}>{share.full_name} - {share.email}</option>)}</select>
            <select value={interview.jobId} onChange={(e) => setInterview({ ...interview, jobId: e.target.value })}><option value="">{t("jobs")}</option>{applicationShares.filter((share) => !interview.userId || share.user_id === interview.userId).map((share) => <option key={share.application_id} value={share.job_id}>{share.job_title} - {share.company_name}</option>)}</select>
            <input type="datetime-local" value={interview.scheduledAt} onChange={(e) => setInterview({ ...interview, scheduledAt: e.target.value })} />
            <input placeholder={t("channel")} value={interview.channel} onChange={(e) => setInterview({ ...interview, channel: e.target.value })} />
            <textarea placeholder={t("notes")} value={interview.notes} onChange={(e) => setInterview({ ...interview, notes: e.target.value })} />
            <button className="primary-button loading-button" disabled={schedulingInterview}>{schedulingInterview && <span className="spinner" aria-hidden="true"></span>}{t("scheduleInterview")}</button>
          </form>}

          {tab === "courses" && <form className="panel admin-form" onSubmit={addCourse}>
            <h2>{t("addCourse")}</h2>
            <select value={courseForm.userId} onChange={(e) => setCourseForm({ ...courseForm, userId: e.target.value })}><option value="">{t("users")}</option>{uniqueCandidates.map((share) => <option value={share.user_id} key={share.user_id}>{share.full_name}</option>)}</select>
            <input placeholder={t("title")} value={courseForm.title} onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })} />
            <input placeholder={t("provider")} value={courseForm.provider} onChange={(e) => setCourseForm({ ...courseForm, provider: e.target.value })} />
            <input type="date" value={courseForm.completionDate} onChange={(e) => setCourseForm({ ...courseForm, completionDate: e.target.value })} />
            <input placeholder={t("viewFile")} value={courseForm.certificateUrl} onChange={(e) => setCourseForm({ ...courseForm, certificateUrl: e.target.value })} />
            <textarea placeholder={t("notes")} value={courseForm.notes} onChange={(e) => setCourseForm({ ...courseForm, notes: e.target.value })} />
            <button className="secondary-button">{t("addCourse")}</button>
          </form>}

          {tab === "interviews" && <section className="panel">
            <div className="section-head"><h2>{t("scheduledInterviews")}</h2><span className="status">{interviews.length}</span></div>
            <div className="interview-admin-list">
              {interviews.length ? pagedAgentInterviews.map((item) => <article className="interview-admin-item" key={item.id}>
                <div><strong>{item.full_name}</strong><span>{item.email}</span></div>
                <div><strong>{item.job_title || t("job")}</strong><span>{item.company_name || "-"}</span></div>
                <div><strong>{new Date(item.scheduled_at).toLocaleString()}</strong><span>{item.channel}</span></div>
                <select className="action-select" defaultValue="" onChange={(e) => { updateInterviewStatus(item, e.target.value); e.target.value = ""; }}>
                  <option value="">{t("interviewOutcome")}</option>
                  {INTERVIEW_OUTCOME_STATUSES.map((status) => <option value={status} key={status}>{statusLabel(status, lang)}</option>)}
                </select>
              </article>) : <p>{t("noAppliedJobs")}</p>}
            </div>
          </section>}

          <PaginationControls t={t} page={agentPage} total={activeAgentTotal} setPage={setAgentPage} />
        </div>
      </section>
    </section>
  );
}

function AgentChatPanel({ t, users = [], initialUserId = "" }) {
  const [threads, setThreads] = useState([]);
  const [targetUserId, setTargetUserId] = useState(initialUserId || "");
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [chatError, setChatError] = useState("");
  const messagesRef = useRef(null);
  const latestMessageIdRef = useRef("");
  async function loadThreads() {
    const data = await api("/agent/chat/threads");
    setThreads(data);
    if (!targetUserId && data[0]?.user_id) setTargetUserId(data[0].user_id);
  }
  async function loadMessages(userId = targetUserId) {
    if (!userId) return;
    const data = await api(`/agent/chat/messages?user_id=${encodeURIComponent(userId)}`);
    setMessages(data);
    await loadThreads();
  }
  useEffect(() => { loadThreads().catch(() => {}); }, []);
  useEffect(() => {
    if (initialUserId && initialUserId !== targetUserId) setTargetUserId(initialUserId);
  }, [initialUserId]);
  useEffect(() => { loadMessages().catch(() => {}); }, [targetUserId]);
  useEffect(() => {
    const timer = setInterval(() => loadMessages().catch(() => {}), 3500);
    return () => clearInterval(timer);
  }, [targetUserId]);
  useEffect(() => {
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    const latest = messages[messages.length - 1];
    if (latest && latest.id !== latestMessageIdRef.current) {
      if (latestMessageIdRef.current && latest.sender_role === "user") playNotificationBeep();
      latestMessageIdRef.current = latest.id;
    }
  }, [messages.length]);
  async function sendMessage(event) {
    event.preventDefault();
    if (!message.trim() || !targetUserId) return;
    setSending(true);
    try {
      await api("/agent/chat/messages", { method: "POST", body: JSON.stringify({ userId: targetUserId, message }) });
      setMessage("");
      await loadMessages();
    } finally {
      setSending(false);
    }
  }
  async function clearChat() {
    if (!targetUserId) return;
    setClearing(true);
    setChatError("");
    try {
      await api(`/agent/chat/messages?user_id=${encodeURIComponent(targetUserId)}`, { method: "DELETE" });
      setMessages([]);
      await loadThreads();
    } catch (err) {
      setChatError(err.message || t("clearFailed"));
    } finally {
      setClearing(false);
    }
  }
  const visibleThreads = threads.length ? threads : users.map((user) => ({
    user_id: user.user_id,
    full_name: user.full_name,
    email: user.email,
    avatar_url: user.avatar_url,
    plan: user.plan,
    last_active_at: user.last_active_at
  }));
  return (
    <section className="panel agent-chat-panel">
      <div className="section-head"><h2>{t("agentChat")}</h2><div className="inline-actions"><span className="status">{visibleThreads.length}</span><button className="secondary-button compact" type="button" onClick={clearChat} disabled={clearing || !targetUserId}>{clearing ? t("clearingChat") : t("clearChat")}</button></div></div>
      <div className="agent-chat-layout">
        <aside className="agent-chat-threads">
          {visibleThreads.map((thread) => (
            <button className={targetUserId === thread.user_id ? "active" : ""} type="button" key={thread.user_id} onClick={() => setTargetUserId(thread.user_id)}>
              <Avatar user={{ full_name: thread.full_name, avatar_url: thread.avatar_url, plan: thread.plan, last_active_at: thread.last_active_at }} size="small" />
              <span><strong>{thread.full_name}</strong><small>{thread.last_message || thread.email}</small></span>
              {Number(thread.unread_count || 0) > 0 && <b>{thread.unread_count}</b>}
            </button>
          ))}
        </aside>
        <div className="agent-chat-conversation">
          <div className="support-messages" ref={messagesRef}>
            {messages.map((item) => <SupportBubble item={item} t={t} key={item.id} />)}
            {!messages.length && <p className="muted-text">{t("agentChat")}</p>}
          </div>
          {chatError && <p className="error support-error">{chatError}</p>}
          <form onSubmit={sendMessage}>
            <input placeholder={t("supportMessage")} value={message} onChange={(e) => setMessage(e.target.value)} />
            <button className="primary-button" disabled={sending || !targetUserId}>{t("send")}</button>
          </form>
        </div>
      </div>
    </section>
  );
}

function UserAgentChatWindow({ t, agent, threads = [], setAgent, onUpdate, close }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [chatError, setChatError] = useState("");
  const messagesRef = useRef(null);
  const initializedMessagesRef = useRef(false);
  const latestMessageIdRef = useRef("");
  async function loadMessages() {
    if (!agent?.id) return;
    setMessages(await api(`/user/agent-chat/messages?agent_id=${encodeURIComponent(agent.id)}`));
    const update = onUpdate?.();
    update?.catch?.(() => {});
  }
  useEffect(() => {
    loadMessages().catch(() => {});
    const timer = setInterval(() => loadMessages().catch(() => {}), 3500);
    return () => clearInterval(timer);
  }, [agent?.id]);
  useEffect(() => {
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    const latest = messages[messages.length - 1];
    if (!latest) return;
    if (!initializedMessagesRef.current) {
      initializedMessagesRef.current = true;
      latestMessageIdRef.current = latest.id;
      return;
    }
    if (latest.id !== latestMessageIdRef.current) {
      if (latest.sender_role === "agent") playNotificationBeep();
      latestMessageIdRef.current = latest.id;
    }
  }, [messages.length]);
  async function sendMessage(event) {
    event.preventDefault();
    if (!message.trim() || !agent?.id) return;
    setSending(true);
    try {
      await api("/user/agent-chat/messages", { method: "POST", body: JSON.stringify({ userId: agent.id, message }) });
      setMessage("");
      await loadMessages();
    } finally {
      setSending(false);
    }
  }
  async function clearChat() {
    if (!agent?.id) return;
    setClearing(true);
    setChatError("");
    try {
      await api(`/user/agent-chat/messages?agent_id=${encodeURIComponent(agent.id)}`, { method: "DELETE" });
      setMessages([]);
      const update = onUpdate?.();
      update?.catch?.(() => {});
    } catch (err) {
      setChatError(err.message || t("clearFailed"));
    } finally {
      setClearing(false);
    }
  }
  return (
    <div className="support-window agent-user-chat-window">
      <header>
        <strong>{agent.agency_name || agent.full_name || t("agentChat")}</strong>
        <div><button type="button" onClick={clearChat} disabled={clearing}>{clearing ? t("clearingChat") : t("clearChat")}</button><button type="button" onClick={close}>×</button></div>
      </header>
      {threads.length > 1 && <div className="user-agent-thread-row">
        {threads.map((thread) => (
          <button className={thread.id === agent.id ? "active" : ""} type="button" key={thread.id} onClick={() => setAgent?.(thread)}>
            <Avatar user={{ full_name: thread.agency_name || thread.full_name, avatar_url: thread.avatar_url }} size="small" />
            <span>{thread.agency_name || thread.full_name}</span>
            {Number(thread.unread_count || 0) > 0 && <b>{thread.unread_count}</b>}
          </button>
        ))}
      </div>}
      <div className="support-messages" ref={messagesRef}>
        {messages.map((item) => <SupportBubble item={item} t={t} key={item.id} />)}
        {!messages.length && <p className="muted-text">{t("chatWithAgent")}</p>}
      </div>
      {chatError && <p className="error support-error">{chatError}</p>}
      <form onSubmit={sendMessage}>
        <input placeholder={t("supportMessage")} value={message} onChange={(e) => setMessage(e.target.value)} />
        <button className="primary-button" disabled={sending}>{t("send")}</button>
      </form>
    </div>
  );
}

function SupportWindow({ t, me, users, initialUserId = "", onUpdate, close }) {
  const isSupportAdmin = ["admin", "master_admin"].includes(me.user.role);
  const isAgentSupport = me.user.role === "agent";
  const [targetUserId, setTargetUserId] = useState(isSupportAdmin ? initialUserId || users[0]?.id || "" : me.user.id);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [chatError, setChatError] = useState("");
  const messagesRef = useRef(null);
  const initializedMessagesRef = useRef(false);
  const latestMessageIdRef = useRef("");
  async function loadMessages(userId = targetUserId) {
    if (!userId) return;
    const query = isSupportAdmin && userId ? `?user_id=${userId}` : "";
    setMessages(await api(`/support/messages${query}`));
    await onUpdate?.();
  }
  useEffect(() => {
    if (isSupportAdmin && !targetUserId && users[0]?.id) setTargetUserId(users[0].id);
  }, [users.length, targetUserId, isSupportAdmin]);
  useEffect(() => {
    if (isSupportAdmin && initialUserId && initialUserId !== targetUserId) setTargetUserId(initialUserId);
  }, [initialUserId, isSupportAdmin, targetUserId]);
  useEffect(() => { loadMessages(); }, [targetUserId]);
  useEffect(() => {
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    const latest = messages[messages.length - 1];
    if (!latest) return;
    if (!initializedMessagesRef.current) {
      initializedMessagesRef.current = true;
      latestMessageIdRef.current = latest.id;
      return;
    }
    if (latest.id !== latestMessageIdRef.current) {
      const ownRole = isSupportAdmin ? "admin" : "user";
      if (["admin", "user"].includes(latest.sender_role) && latest.sender_role !== ownRole) playNotificationBeep();
      latestMessageIdRef.current = latest.id;
    }
  }, [messages.length]);
  useEffect(() => {
    const timer = setInterval(() => {
      loadMessages().catch(() => {});
    }, 3500);
    return () => clearInterval(timer);
  }, [targetUserId, isSupportAdmin]);
  async function sendMessage(event) {
    event.preventDefault();
    if (!message.trim()) return;
    setSending(true);
    try {
      await api("/support/messages", { method: "POST", body: JSON.stringify({ message, userId: isSupportAdmin ? targetUserId : undefined }) });
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
        body: JSON.stringify({ userId: isSupportAdmin ? targetUserId : undefined })
      });
      await loadMessages();
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
      await api("/support/messages", { method: "POST", body: JSON.stringify({ message: t("liveAgentRequest"), userId: isSupportAdmin ? targetUserId : undefined }) });
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
  const liveMode = messages.some((item) => item.sender_role === "user" && /دعم مباشر|live support|live agent|human|موظف/i.test(item.message || ""));
  const showBotOptions = !liveMode && lastMessage?.sender_role === "bot" && /دعم مباشر|live support|end the conversation|إنهاء المحادثة|end the conversation/i.test(lastMessage.message || "");
  return (
    <div className="support-window">
      <header><strong>{isSupportAdmin ? t("supportInbox") : isAgentSupport ? t("adminChat") : t("aiAssistant")}</strong><div><button type="button" onClick={clearChat} disabled={clearing}>{clearing ? t("clearingChat") : t("clearChat")}</button><button onClick={close}>×</button></div></header>
      {isSupportAdmin && <select value={targetUserId} onChange={(e) => setTargetUserId(e.target.value)}>{users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}</select>}
      <div className="support-messages" ref={messagesRef}>
        {messages.map((item) => <SupportBubble item={item} t={t} key={item.id} />)}
      </div>
      {liveMode && !isSupportAdmin && !isAgentSupport && <p className="notice support-live-note">{t("liveSupportStarted")}</p>}
      {showBotOptions && !isAgentSupport && <div className="support-options">
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

function SupportBubble({ item, t }) {
  const lines = String(item.message || "").split(/\r?\n/).filter((line) => line.trim());
  return (
    <div className={`support-bubble ${item.sender_role}`}>
      <strong>{item.sender_role === "bot" ? t?.("message") || "Message" : item.sender_role}</strong>
      <span>
        {lines.length ? lines.map((line, index) => <span className="support-line" key={`${item.id}-${index}`}>{line}</span>) : <span className="support-line">-</span>}
      </span>
    </div>
  );
}

function PasswordField({ label, name, value, onChange, visible, setVisible, t, required = false }) {
  return (
    <label>{label}
      <span className="password-field">
        <input
          name={name}
          autoComplete="new-password"
          type={visible ? "text" : "password"}
          value={value}
          required={required}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="button"
          className="password-toggle"
          aria-label={visible ? t("hidePassword") : t("showPassword")}
          title={visible ? t("hidePassword") : t("showPassword")}
          onClick={() => setVisible((current) => !current)}
        >
          {visible ? "◉" : "○"}
        </button>
      </span>
    </label>
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

function AnalyticsList({ title, data = [], labelFormatter = (label) => label }) {
  const total = data.reduce((sum, item) => sum + Number(item.value || 0), 0);
  return (
    <article className="panel analytics-card">
      <h2>{title}</h2>
      <div className="analytics-list">
        {data.length ? data.map((item) => {
          const value = Number(item.value || 0);
          const percent = total ? Math.round((value / total) * 100) : 0;
          return <div className="analytics-row" key={item.label}><span>{labelFormatter(item.label)}</span><strong>{value}</strong><div><i style={{ width: `${percent}%` }} /></div></div>;
        }) : <p>0</p>}
      </div>
    </article>
  );
}

function Avatar({ user, size = "" }) {
  const [failed, setFailed] = useState(false);
  const online = isUserOnline(user);
  const premium = user?.plan === "premium";
  const className = `avatar ${size} ${premium ? "premium" : ""}`.trim();
  const avatarUrl = user?.avatarUrl || user?.avatar_url;
  const src = avatarUrl ? assetUrl(avatarUrl) : "";
  const name = user?.fullName || user?.full_name || "";
  useEffect(() => setFailed(false), [src]);
  const avatar = src && !failed ? <img className={className} src={src} alt={name || "Profile"} onError={() => setFailed(true)} /> : <div className={className}>{initials(name)}</div>;
  if (!online) return avatar;
  return <span className={`avatar-status-wrap ${size}`.trim()}>{avatar}<span className="online-dot" /></span>;
}

function initials(name = "") {
  return name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

function isUserOnline(user = {}) {
  const value = user.lastActiveAt || user.last_active_at;
  if (!value) return false;
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return false;
  return Date.now() - timestamp < 90 * 1000;
}

function formatNumber(value = 0) {
  return Number(value || 0).toLocaleString();
}

function playNotificationBeep() {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const context = new AudioContextClass();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.type = "sine";
    oscillator.frequency.value = 880;
    gain.gain.setValueAtTime(0.0001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.08, context.currentTime + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.18);
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + 0.2);
    window.setTimeout(() => context.close?.(), 260);
  } catch {
    // Notification sound is best-effort; browsers may block audio before user interaction.
  }
}

function assetUrl(path = "") {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const apiBase = (import.meta.env.VITE_API_URL || "/api").replace(/\/api$/, "");
  return `${apiBase}${path}`;
}

createRoot(document.getElementById("root")).render(<App />);
