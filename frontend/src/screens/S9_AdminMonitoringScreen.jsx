import React, { useState, useEffect } from 'react';
import {
  Activity,
  Globe,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ExternalLink,
  History,
  FileText,
  Sparkles,
  Search,
  Filter,
  ArrowLeft,
  ChevronRight,
  Play,
  Check,
  X,
  ShieldCheck,
  Layers,
  Cpu,
  FileCheck,
  Clock,
  Database
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import {
  fetchAgentsStatus,
  fetchAgentRuns,
  triggerAgentDiscover,
  triggerAgentCrawl,
  triggerAgentMonitor,
  fetchDiscoveredSources,
  fetchAgentUpdates,
  approveAgentUpdate,
  rejectAgentUpdate,
  fetchSchemeVersions,
  fetchMonitoringOverview,
  fetchAllSchemes,
  fetchAdminSession,
  loginAdmin,
  logoutAdmin
} from '../services/api';

const AGENT_METADATA = {
  source_discovery: {
    titleEn: '1. Source Discovery Agent',
    titleHi: '1. स्रोत खोज एजेंट (Source Discovery)',
    descEn: 'References myScheme scheme pages for the locally curated catalogue.',
    descHi: 'स्थानीय योजना सूची के लिए myScheme योजना पृष्ठों का संदर्भ लेता है।',
    icon: Globe,
  },
  crawling: {
    titleEn: '2. Crawling Agent',
    titleHi: '2. क्रॉलिंग एजेंट (Crawling Agent)',
    descEn: 'Fetches HTML & PDFs via legacy-resilient SSL HTTPX client; parses clean text using BeautifulSoup & PyMuPDF.',
    descHi: 'एसएसएल-सक्षम क्लाइंट से वेबपेज व पीडीएफ डाउनलोड कर टेक्स्ट निकालता है।',
    icon: FileText,
  },
  change_detection: {
    titleEn: '3. Change Detection Agent',
    titleHi: '3. परिवर्तन पहचान एजेंट (Change Detection)',
    descEn: 'Computes cryptographic SHA-256 hashes, maintains snapshot history, and detects textual diffs.',
    descHi: 'SHA-256 हैश तुलना से नए व संशोधित नियमों की सटीक पहचान करता है।',
    icon: Activity,
  },
  information_extraction: {
    titleEn: '4. Information Extraction Agent',
    titleHi: '4. सूचना निष्कर्षण एजेंट (Extraction)',
    descEn: 'Extracts eligibility criteria, benefits, documents, and steps via Gemini + deterministic fallback.',
    descHi: 'पात्रता, लाभ, आवश्यक दस्तावेज और आवेदन प्रक्रिया की निष्पक्ष निष्कर्षण करता है।',
    icon: Sparkles,
  },
  classification: {
    titleEn: '5. Classification Agent',
    titleHi: '5. वर्गीकरण एजेंट (Classification)',
    descEn: 'Categorizes updates: NEW_SCHEME, ELIGIBILITY_CHANGE, BENEFIT_CHANGE, DOCUMENT_CHANGE, DEADLINE_CHANGE.',
    descHi: 'परिवर्तनों को नीतिगत श्रेणियों (पात्रता, लाभ, दस्तावेज, अंतिम तिथि) में बांटता है।',
    icon: Layers,
  },
  evidence_validation: {
    titleEn: '6. Evidence Validation Agent',
    titleHi: '6. साक्ष्य सत्यापन एजेंट (Evidence Validation)',
    descEn: 'Verifies exact quote citations against crawled source, flags UNKNOWNs, and computes confidence score.',
    descHi: 'दावों का मूल स्रोत से मिलान करता है और अनिश्चित तथ्यों को UNKNOWN चिह्नित करता है।',
    icon: FileCheck,
  },
  policy_review_gate: {
    titleEn: '7. Policy Review Gate',
    titleHi: '7. नीति समीक्षा द्वार (Policy Review Gate)',
    descEn: 'Human-in-the-loop safety firewall. Prevents unauthorized rule modifications to citizen eligibility.',
    descHi: 'मानव स्वीकृति द्वार: बिना जांच व अनुमोदन के कोई भी नियम सीधे लागू नहीं होता।',
    icon: ShieldCheck,
  },
  publishing_service: {
    titleEn: '8. Publishing Service',
    titleHi: '8. प्रकाशन सेवा (Publishing Service)',
    descEn: 'Atomically commits approved changes to the SQLite catalog and records immutable scheme versions.',
    descHi: 'स्वीकृत योजनाओं को कैटलॉग में अपडेट करता है और अपरिवर्तनीय संस्करण सुरक्षित रखता है।',
    icon: Database,
  },
  monitoring_agent: {
    titleEn: '9. Monitoring Agent',
    titleHi: '9. निगरानी समन्वयक (Monitoring Agent)',
    descEn: 'Coordinates end-to-end monitoring cycles, periodic rechecking, and execution logging.',
    descHi: 'सभी 9 एजेंटों के चक्र को समन्वित करता है और नियमित निगरानी सुनिश्चित करता है।',
    icon: Cpu,
  },
};

export default function S9_AdminMonitoringScreen() {
  const { language } = useLanguage();
  const { setCurrentScreen } = useSession();
  const [authChecked, setAuthChecked] = useState(false);
  const [adminUser, setAdminUser] = useState(null);
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authBusy, setAuthBusy] = useState(false);

  // Navigation tab
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'agents', 'sources', 'updates', 'history'

  // Data states
  const [overview, setOverview] = useState({
    total_discovered_sources: 0,
    successfully_monitored_sources: 0,
    schemes_discovered: 0,
    pending_updates: 0,
    approved_updates: 0,
    failed_agent_runs: 0,
  });
  const [agentsStatus, setAgentsStatus] = useState({});
  const [sources, setSources] = useState([]);
  const [updates, setUpdates] = useState([]);
  const [agentRuns, setAgentRuns] = useState([]);
  const [schemeCatalog, setSchemeCatalog] = useState([]);

  // Filter & Search states
  const [sourceFilter, setSourceFilter] = useState('all');
  const [updateFilter, setUpdateFilter] = useState('PENDING');
  const [searchSourceText, setSearchSourceText] = useState('');

  // Version history states
  const [selectedSchemeId, setSelectedSchemeId] = useState('');
  const [schemeVersions, setSchemeVersions] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Loading & Action states
  const [isLoading, setIsLoading] = useState(false);
  const [isActionRunning, setIsActionRunning] = useState(false);
  const [actionNotification, setActionNotification] = useState(null);

  // Reject Modal state
  const [rejectingUpdateId, setRejectingUpdateId] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  useEffect(() => {
    fetchAdminSession()
      .then((session) => {
        if (session.authenticated) {
          setAdminUser(session.username);
          loadAllData();
        } else if (!session.configured) {
          setAuthError(language === 'hi' ? 'प्रशासक लॉगिन कॉन्फ़िगर नहीं है। सर्वर पर सुरक्षित ADMIN_* मान सेट करें।' : 'Admin login is not configured. Set secure ADMIN_* values on the server.');
        }
      })
      .catch((err) => setAuthError(err.message))
      .finally(() => setAuthChecked(true));
  }, []);

  useEffect(() => {
    const onSessionExpired = () => {
      setAdminUser(null);
      setSources([]); setUpdates([]); setAgentRuns([]); setSchemeCatalog([]); setSchemeVersions([]);
      setAuthError(language === 'hi' ? 'प्रशासक सत्र समाप्त हो गया। फिर से लॉगिन करें।' : 'Admin session expired. Please sign in again.');
    };
    window.addEventListener('admin-session-expired', onSessionExpired);
    return () => window.removeEventListener('admin-session-expired', onSessionExpired);
  }, [language]);

  const handleAdminLogin = async (event) => {
    event.preventDefault();
    setAuthBusy(true);
    setAuthError('');
    try {
      const session = await loginAdmin(loginUsername, loginPassword);
      setAdminUser(session.username);
      setLoginPassword('');
      await loadAllData();
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthBusy(false);
    }
  };

  const handleAdminLogout = async () => {
    try { await logoutAdmin(); } finally {
      setAdminUser(null);
      setSources([]); setUpdates([]); setAgentRuns([]); setSchemeCatalog([]); setSchemeVersions([]);
      setCurrentScreen('S0');
    }
  };

  const loadAllData = async () => {
    setIsLoading(true);
    try {
      const [ovData, agData, srcData, updData, runsData, schemesData] = await Promise.allSettled([
        fetchMonitoringOverview(),
        fetchAgentsStatus(),
        fetchDiscoveredSources(),
        fetchAgentUpdates(),
        fetchAgentRuns(25),
        fetchAllSchemes(),
      ]);
      const failedLoads = [ovData, agData, srcData, updData, runsData, schemesData]
        .filter((result) => result.status === 'rejected');
      if (failedLoads.length) {
        setActionNotification({
          type: 'error',
          message: `${failedLoads.length} monitoring data request(s) failed. ${failedLoads[0].reason?.message || 'Check the backend connection and refresh.'}`,
        });
      }

      if (ovData.status === 'fulfilled' && ovData.value?.overview) {
        setOverview(ovData.value.overview);
      }
      if (agData.status === 'fulfilled' && agData.value?.agents) {
        setAgentsStatus(agData.value.agents);
      }
      if (srcData.status === 'fulfilled' && srcData.value?.sources) {
        setSources(srcData.value.sources);
      }
      if (updData.status === 'fulfilled' && updData.value?.updates) {
        setUpdates(updData.value.updates);
      }
      if (runsData.status === 'fulfilled' && runsData.value?.runs) {
        setAgentRuns(runsData.value.runs);
      }
      if (schemesData.status === 'fulfilled' && Array.isArray(schemesData.value)) {
        setSchemeCatalog(schemesData.value);
        if (schemesData.value.length > 0 && !selectedSchemeId) {
          setSelectedSchemeId(schemesData.value[0].id);
          loadSchemeVersions(schemesData.value[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to load monitoring data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSchemeVersions = async (schemeId) => {
    if (!schemeId) return;
    setHistoryLoading(true);
    try {
      const data = await fetchSchemeVersions(schemeId);
      if (data?.versions) {
        setSchemeVersions(data.versions);
      }
    } catch (err) {
      console.error('Failed to load scheme versions:', err);
      setSchemeVersions([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Section F: Working Manual Controls
  const handleDiscoverSources = async () => {
    setIsActionRunning(true);
    setActionNotification({ type: 'info', message: language === 'hi' ? 'स्रोत खोज एजेंट सक्रिय हो रहा है...' : 'Running Source Discovery Agent across seed portals...' });
    try {
      const res = await triggerAgentDiscover();
      if (!res.success) {
        throw new Error((res.source_errors || []).map((item) => `${item.url}: ${item.error}`).join('; ') || 'The myScheme source page could not be read.');
      }
      setActionNotification({
        type: 'success',
        message: language === 'hi'
          ? `स्रोत खोज पूर्ण! ${res.count || 0} स्रोत पंजीकृत हैं।${res.source_errors?.length ? ` ${res.source_errors.length} स्रोतों में त्रुटि हुई।` : ''}`
          : `Source discovery complete. ${res.count || 0} sources registered.${res.source_errors?.length ? ` ${res.source_errors.length} source(s) failed: ${res.source_errors.map((item) => `${item.url}: ${item.error}`).join('; ')}` : ''}`
      });
      await loadAllData();
    } catch (err) {
      setActionNotification({ type: 'error', message: `Discovery failed: ${err.message}` });
    } finally {
      setIsActionRunning(false);
    }
  };

  const handleRunCrawler = async () => {
    setIsActionRunning(true);
    setActionNotification({ type: 'info', message: language === 'hi' ? 'क्रॉलिंग एजेंट पेजों व सर्कुलरों का विश्लेषण कर रहा है...' : 'Crawling Agent fetching approved government pages & circulars...' });
    try {
      const res = await triggerAgentCrawl(null, 10);
      setActionNotification({
        type: 'success',
        message: language === 'hi'
          ? `क्रॉलिंग पूर्ण! ${res.count || 0} स्रोत सफलतापूर्वक प्रोसेस किए गए।`
          : `Crawl complete! Processed ${res.count || 0} sources.`
      });
      await loadAllData();
    } catch (err) {
      setActionNotification({ type: 'error', message: `Crawling failed: ${err.message}` });
    } finally {
      setIsActionRunning(false);
    }
  };

  const handleRunMonitoring = async () => {
    setIsActionRunning(true);
    setActionNotification({ type: 'info', message: language === 'hi' ? 'पूर्ण निगरानी चक्र चल रहा है (क्रॉल -> हैश -> निष्कर्षण -> सत्यापन)...' : 'Running full monitoring cycle (Crawl -> Hash -> Extract -> Validate)...' });
    try {
      const res = await triggerAgentMonitor(null, 10);
      setActionNotification({
        type: 'success',
        message: language === 'hi'
          ? `निगरानी चक्र पूर्ण! ${res.summary || 'कार्य संपन्न।'}`
          : `Monitoring cycle complete! ${res.summary || 'Finished successfully.'}`
      });
      await loadAllData();
    } catch (err) {
      setActionNotification({ type: 'error', message: `Monitoring run failed: ${err.message}` });
    } finally {
      setIsActionRunning(false);
    }
  };

  // Section D: Change Review Actions
  const handleApproveUpdate = async (updateId) => {
    try {
      await approveAgentUpdate(updateId, 'Approved following official government notification verification.');
      setActionNotification({
        type: 'success',
        message: language === 'hi'
          ? `अपडेट स्वीकृत! योजना कैटलॉग अपडेट हो चुका है एवं नया संस्करण दर्ज हुआ।`
          : `Update approved! Changes successfully published to active scheme catalog with new version.`
      });
      await loadAllData();
      if (selectedSchemeId) {
        loadSchemeVersions(selectedSchemeId);
      }
    } catch (err) {
      setActionNotification({ type: 'error', message: `Approval failed: ${err.message}` });
    }
  };

  const handleRejectUpdate = async () => {
    if (!rejectingUpdateId || !rejectReason.trim()) return;
    try {
      await rejectAgentUpdate(rejectingUpdateId, rejectReason.trim());
      setActionNotification({
        type: 'info',
        message: language === 'hi' ? 'अपडेट अस्वीकृत कर दिया गया है।' : 'Proposed update was rejected.'
      });
      setRejectingUpdateId(null);
      setRejectReason('');
      await loadAllData();
    } catch (err) {
      setActionNotification({ type: 'error', message: `Rejection failed: ${err.message}` });
    }
  };

  const filteredSources = sources.filter((s) => {
    const matchesFilter = sourceFilter === 'all' || s.status === sourceFilter;
    const matchesSearch = !searchSourceText || s.url.toLowerCase().includes(searchSourceText.toLowerCase()) || s.domain.toLowerCase().includes(searchSourceText.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const filteredUpdates = updates.filter((u) => {
    if (!updateFilter) return true;
    return u.review_status === updateFilter;
  });

  if (!authChecked) return <div className="p-8 text-center text-slate-600">{language === 'hi' ? 'प्रशासक सत्र जाँचा जा रहा है…' : 'Checking administrator session…'}</div>;
  if (!adminUser) return (
    <section className="max-w-md mx-auto my-12 w-full rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
      <button onClick={() => setCurrentScreen('S0')} className="mb-5 text-sm text-slate-500 hover:text-slate-900">← {language === 'hi' ? 'वापस' : 'Back'}</button>
      <h1 className="mb-2 text-2xl font-bold text-slate-900">{language === 'hi' ? 'प्रशासक लॉगिन' : 'Administrator sign in'}</h1>
      <p className="mb-6 text-sm text-slate-600">{language === 'hi' ? 'इस निगरानी पोर्टल तक केवल अधिकृत प्रशासक पहुँच सकते हैं।' : 'Only authorized administrators can access monitoring and scheme review.'}</p>
      <form onSubmit={handleAdminLogin} className="space-y-4">
        <label className="block text-sm font-medium">{language === 'hi' ? 'उपयोगकर्ता नाम' : 'Username'}
          <input autoComplete="username" required value={loginUsername} onChange={(e) => setLoginUsername(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
        </label>
        <label className="block text-sm font-medium">{language === 'hi' ? 'पासवर्ड' : 'Password'}
          <input autoComplete="current-password" type="password" required value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
        </label>
        {authError && <p role="alert" className="rounded-lg bg-rose-50 p-3 text-sm text-rose-800">{authError}</p>}
        <button disabled={authBusy} className="w-full rounded-lg bg-teal-700 px-4 py-2.5 font-semibold text-white disabled:opacity-60">{authBusy ? (language === 'hi' ? 'जाँच जारी है…' : 'Signing in…') : (language === 'hi' ? 'सुरक्षित लॉगिन' : 'Sign in securely')}</button>
      </form>
    </section>
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 pb-16">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-4 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrentScreen('S0')}
              className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition"
              title={language === 'hi' ? 'वापस जाएं' : 'Back to Home'}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  <ShieldCheck className="w-3 h-3 mr-1" />
                  {language === 'hi' ? 'स्वायत्त बहु-एजेंट प्रणाली' : 'Autonomous Multi-Agent System'}
                </span>
                <span className="text-xs text-slate-400">• YojnaSarthi v2.0</span>
              </div>
              <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
                {language === 'hi' ? 'योजना इंटेलिजेंस एवं बहु-एजेंट निगरानी डैशबोर्ड' : 'Scheme Intelligence & Agent Monitoring'}
              </h1>
            </div>
          </div>

          {/* Section F: Header Quick Controls */}
          <div className="flex items-center flex-wrap gap-2">
            <button
              onClick={handleDiscoverSources}
              disabled={isActionRunning}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition disabled:opacity-50"
            >
              <Globe className="w-3.5 h-3.5" />
              {language === 'hi' ? 'स्रोत खोजें' : 'Discover Sources'}
            </button>
            <button
              onClick={handleRunCrawler}
              disabled={isActionRunning}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition disabled:opacity-50"
            >
              <FileText className="w-3.5 h-3.5" />
              {language === 'hi' ? 'क्रॉल चलाएं' : 'Run Crawler'}
            </button>
            <button
              onClick={handleRunMonitoring}
              disabled={isActionRunning}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 text-white hover:bg-emerald-700 shadow-xs transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {language === 'hi' ? 'पूर्ण निगरानी चलाएं' : 'Run Monitoring'}
            </button>
            <button
              onClick={loadAllData}
              disabled={isLoading || isActionRunning}
              className="p-2 hover:bg-slate-100 text-slate-600 rounded-lg transition"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-emerald-600' : ''}`} />
            </button>
            <button onClick={handleAdminLogout} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100">{language === 'hi' ? 'लॉग आउट' : `Sign out (${adminUser})`}</button>
          </div>
        </div>
      </header>

      {/* Notification Banner */}
      {actionNotification && (
        <div className="max-w-7xl mx-auto px-6 pt-4">
          <div
            className={`p-3 rounded-lg border text-sm flex items-center justify-between shadow-xs ${
              actionNotification.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : actionNotification.type === 'error'
                ? 'bg-rose-50 text-rose-800 border-rose-200'
                : 'bg-blue-50 text-blue-800 border-blue-200'
            }`}
          >
            <div className="flex items-center gap-2">
              {actionNotification.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />}
              {actionNotification.type === 'error' && <XCircle className="w-4 h-4 text-rose-600 shrink-0" />}
              {actionNotification.type === 'info' && <RefreshCw className="w-4 h-4 text-blue-600 animate-spin shrink-0" />}
              <span>{actionNotification.message}</span>
            </div>
            <button
              onClick={() => setActionNotification(null)}
              className="text-xs opacity-70 hover:opacity-100 underline ml-3"
            >
              {language === 'hi' ? 'बंद करें' : 'Dismiss'}
            </button>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200 space-x-2 overflow-x-auto pb-px">
          {[
            { id: 'overview', labelEn: 'Overview & Status', labelHi: 'अवलोकन व सारांश', icon: Activity },
            { id: 'agents', labelEn: 'Agent Execution Panel (9)', labelHi: '9 एजेंट निष्पादन पैनल', icon: Cpu },
            { id: 'sources', labelEn: `Source Explorer (${sources.length})`, labelHi: `स्रोत एक्सप्लोरर (${sources.length})`, icon: Globe },
            { id: 'updates', labelEn: `Change Review Gate (${updates.filter(u => u.review_status === 'PENDING').length} Pending)`, labelHi: `नीति समीक्षा द्वार (${updates.filter(u => u.review_status === 'PENDING').length} लंबित)`, icon: ShieldCheck },
            { id: 'history', labelEn: 'Version History', labelHi: 'संस्करण इतिहास', icon: History },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition whitespace-nowrap ${
                  isActive
                    ? 'border-emerald-600 text-emerald-700 bg-emerald-50/50'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-600' : 'text-slate-400'}`} />
                <span>{language === 'hi' ? tab.labelHi : tab.labelEn}</span>
              </button>
            );
          })}
        </div>

        {/* =========================================================================
            SECTION A: OVERVIEW
        ========================================================================== */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Metric Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-xs font-medium text-slate-500">
                  {language === 'hi' ? 'कुल खोजे गए स्रोत' : 'Total Sources'}
                </span>
                <div className="text-2xl font-bold text-slate-900 mt-1">{overview.total_discovered_sources}</div>
                <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                  <Globe className="w-3 h-3 text-indigo-500" /> myScheme reference pages
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-xs font-medium text-slate-500">
                  {language === 'hi' ? 'सक्रिय मॉनिटर' : 'Monitored Sources'}
                </span>
                <div className="text-2xl font-bold text-emerald-600 mt-1">{overview.successfully_monitored_sources}</div>
                <div className="text-[11px] text-emerald-600/80 mt-1 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Status: Crawled & Active
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-xs font-medium text-slate-500">
                  {language === 'hi' ? 'खोजे गए योजना नियम' : 'Discovered Schemes'}
                </span>
                <div className="text-2xl font-bold text-blue-600 mt-1">{overview.schemes_discovered}</div>
                <div className="text-[11px] text-blue-600/80 mt-1 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> Structured Extractions
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-amber-200 bg-amber-50/20 shadow-2xs">
                <span className="text-xs font-medium text-amber-800">
                  {language === 'hi' ? 'समीक्षा हेतु लंबित' : 'Pending Updates'}
                </span>
                <div className="text-2xl font-bold text-amber-700 mt-1">{overview.pending_updates}</div>
                <div className="text-[11px] text-amber-700 mt-1 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Awaiting Human Approval
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-xs font-medium text-slate-500">
                  {language === 'hi' ? 'स्वीकृत व प्रकाशित' : 'Approved Updates'}
                </span>
                <div className="text-2xl font-bold text-emerald-700 mt-1">{overview.approved_updates}</div>
                <div className="text-[11px] text-emerald-600 mt-1 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> In Live Scheme Catalog
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-xs font-medium text-slate-500">
                  {language === 'hi' ? 'विफल एजेंट रन' : 'Failed Agent Runs'}
                </span>
                <div className="text-2xl font-bold text-rose-600 mt-1">{overview.failed_agent_runs}</div>
                <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 text-rose-500" /> Auto-isolated & Logged
                </div>
              </div>
            </div>

            {/* Architecture Highlights & Execution Pipeline */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-slate-900">
                    {language === 'hi' ? 'स्वायत्त बहु-एजेंट पाइपलाइन कार्यप्रणाली' : 'Autonomous Multi-Agent Intelligence Pipeline'}
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {language === 'hi'
                      ? '9 विशिष्ट एजेंट क्रमिक रूप से सार्वजनिक स्रोतों से नियम निकालते हैं एवं साक्ष्य की पुष्टि के बाद ही मानव समीक्षा हेतु प्रस्तुत करते हैं।'
                      : 'The agent pipeline runs only when an administrator starts a manual action. Background page scraping is disabled; citizen scheme data comes from the local curated catalogue.'}
                  </p>
                </div>
                <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-700">
                  Deterministic Rule Engine Intact
                </span>
              </div>

              {/* Pipeline Flow Stepper */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2">
                {[
                  { step: '1', title: 'Curated Scheme Pages', desc: 'myScheme page details are stored in the local catalogue' },
                  { step: '2', title: 'SHA-256 Hash Diff', desc: 'Detects semantic modifications vs previous snapshots' },
                  { step: '3', title: 'Extraction & Grounding', desc: 'Eligibility, benefits & exact evidence quotes extracted' },
                  { step: '4', title: 'Classification & Gate', desc: 'Changes routed to Human Policy Review Gate (PENDING)' },
                  { step: '5', title: 'Publishing & Versioning', desc: 'Approved updates versioned; Rule Engine reflects instantly' },
                ].map((s, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1 relative">
                    <div className="flex items-center justify-between">
                      <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-[10px]">
                        {s.step}
                      </span>
                      {idx < 4 && <ChevronRight className="w-3.5 h-3.5 text-slate-400 hidden md:block absolute -right-2 top-4 z-10 bg-white rounded-full border border-slate-200" />}
                    </div>
                    <div className="font-semibold text-slate-800">{s.title}</div>
                    <div className="text-[11px] text-slate-500 leading-relaxed">{s.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Agent Runs Audit Trail */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-3">
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <History className="w-4 h-4 text-slate-500" />
                {language === 'hi' ? 'हालिया एजेंट रन एवं ऑडिट ट्रेल' : 'Recent Agent Execution Runs'}
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 bg-slate-50/50">
                      <th className="py-2.5 px-3">Run ID</th>
                      <th className="py-2.5 px-3">Agent</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Summary / Outcome</th>
                      <th className="py-2.5 px-3">Started At</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {agentRuns.slice(0, 8).map((run) => (
                      <tr key={run.id} className="hover:bg-slate-50/60">
                        <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600">{run.id}</td>
                        <td className="py-2.5 px-3 font-medium text-slate-800">
                          {AGENT_METADATA[run.agent_name]?.titleEn || run.agent_name}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                              run.status === 'COMPLETED'
                                ? 'bg-emerald-100 text-emerald-800'
                                : run.status === 'FAILED'
                                ? 'bg-rose-100 text-rose-800'
                                : run.status === 'RUNNING'
                                ? 'bg-blue-100 text-blue-800 animate-pulse'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {run.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-600 max-w-md truncate">
                          {run.output_summary || run.input_summary || run.error_message || 'Completed'}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                          {run.started_at ? new Date(run.started_at).toLocaleString() : '—'}
                        </td>
                      </tr>
                    ))}
                    {agentRuns.length === 0 && (
                      <tr>
                        <td colSpan="5" className="py-6 text-center text-slate-400">
                          {language === 'hi' ? 'कोई रन रिकॉर्ड नहीं मिला। ऊपर दिए बटन से रन प्रारंभ करें।' : 'No agent runs recorded yet. Click Run Monitoring above to trigger a cycle.'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            SECTION B: AGENT EXECUTION PANEL
        ========================================================================== */}
        {activeTab === 'agents' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-slate-900">
                  {language === 'hi' ? 'सभी 9 विशेषज्ञ एजेंटों की लाइव स्थिति' : 'Live Status of 9 Specialized Agents'}
                </h2>
                <p className="text-xs text-slate-500">
                  {language === 'hi'
                    ? 'प्रत्येक एजेंट अपने निर्दिष्ट कार्य क्षेत्र में स्वायत्त एवं सुरक्षित रूप से कार्य करता है।'
                    : 'Each agent is strictly scoped and decoupled from the deterministic eligibility decision engine.'}
                </p>
              </div>
              <button
                onClick={loadAllData}
                className="text-xs text-emerald-700 hover:text-emerald-800 font-medium flex items-center gap-1"
              >
                <RefreshCw className="w-3.5 h-3.5" /> {language === 'hi' ? 'ताज़ा करें' : 'Refresh Agents'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.keys(AGENT_METADATA).map((agentKey) => {
                const meta = AGENT_METADATA[agentKey];
                const liveStatus = agentsStatus[agentKey] || { status: 'IDLE', last_run: null, output_summary: 'Ready to execute' };
                const Icon = meta.icon;
                const status = liveStatus.status;

                return (
                  <div key={agentKey} className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
                          <Icon className="w-4 h-4" />
                        </div>
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                            status === 'COMPLETED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : status === 'RUNNING'
                              ? 'bg-blue-100 text-blue-800 animate-pulse'
                              : status === 'FAILED'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {status}
                        </span>
                      </div>

                      <h3 className="font-semibold text-sm text-slate-900">
                        {language === 'hi' ? meta.titleHi : meta.titleEn}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                        {language === 'hi' ? meta.descHi : meta.descEn}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
                      <div className="flex items-center justify-between">
                        <span>{language === 'hi' ? 'अंतिम रन:' : 'Last run:'}</span>
                        <span className="font-medium text-slate-700">
                          {liveStatus.last_run ? new Date(liveStatus.last_run).toLocaleTimeString() : 'Never / Initialized'}
                        </span>
                      </div>
                      <div className="truncate text-slate-600">
                        {liveStatus.output_summary || liveStatus.error_message || 'Awaiting trigger'}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* =========================================================================
            SECTION C: SOURCE EXPLORER
        ========================================================================== */}
        {activeTab === 'sources' && (
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-slate-900">
                  {language === 'hi' ? 'खोजे गए एवं ट्रैक किए गए सरकारी स्रोत' : 'Discovered Government Sources'}
                </h2>
                <p className="text-xs text-slate-500">
                  {language === 'hi'
                    ? 'myScheme के योजना पृष्ठ स्थानीय कैटलॉग में संदर्भित हैं; पृष्ठों की स्वचालित स्क्रैपिंग बंद है।'
                    : 'Discovered official government web pages, datasets, and circulars with verified domain boundaries.'}
                </p>
              </div>

              {/* Filters & Search */}
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder={language === 'hi' ? 'URL या डोमेन खोजें...' : 'Filter URL or domain...'}
                    value={searchSourceText}
                    onChange={(e) => setSearchSourceText(e.target.value)}
                    className="pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500 w-48 md:w-64"
                  />
                </div>

                <select
                  value={sourceFilter}
                  onChange={(e) => setSourceFilter(e.target.value)}
                  className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="all">{language === 'hi' ? 'सभी स्थितियां' : 'All Status'}</option>
                  <option value="crawled">crawled</option>
                  <option value="discovered">discovered</option>
                  <option value="failed">failed</option>
                </select>
              </div>
            </div>

            {/* Sources Table */}
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 bg-slate-50/50">
                      <th className="py-2.5 px-3">Domain</th>
                      <th className="py-2.5 px-3">Source URL</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3">Discovered From</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Last Checked</th>
                      <th className="py-2.5 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredSources.map((src) => (
                      <tr key={src.id} className="hover:bg-slate-50/60">
                        <td className="py-2.5 px-3 font-semibold text-slate-800">{src.domain}</td>
                        <td className="py-2.5 px-3 max-w-sm truncate text-slate-600 font-mono text-[11px]">
                          {src.url}
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700">
                            {src.source_type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 text-[11px] max-w-xs truncate">
                          {src.discovered_from || 'Direct Seed'}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                              src.status === 'crawled'
                                ? 'bg-emerald-100 text-emerald-800'
                                : src.status === 'failed'
                                ? 'bg-rose-100 text-rose-800'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {src.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                          {src.last_checked_at ? new Date(src.last_checked_at).toLocaleDateString() : 'Pending'}
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <a
                            href={src.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-emerald-600 hover:text-emerald-700 font-medium"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                            {language === 'hi' ? 'देखें' : 'Visit'}
                          </a>
                        </td>
                      </tr>
                    ))}
                    {filteredSources.length === 0 && (
                      <tr>
                        <td colSpan="7" className="py-8 text-center text-slate-400">
                          {language === 'hi' ? 'कोई स्रोत नहीं मिला।' : 'No sources found matching filter.'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            SECTION D: CHANGE REVIEW PANEL
        ========================================================================== */}
        {activeTab === 'updates' && (
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-slate-900">
                  {language === 'hi' ? 'नीति परिवर्तन समीक्षा एवं अनुमोदन द्वार' : 'Policy Change Review Gate'}
                </h2>
                <p className="text-xs text-slate-500">
                  {language === 'hi'
                    ? 'नागरिक पात्रता अथवा लाभ को प्रभावित करने वाले प्रत्येक परिवर्तन पर प्रशासनिक स्वीकृति आवश्यक है।'
                    : 'Human approval required for any change affecting eligibility criteria, benefits, or documents.'}
                </p>
              </div>

              {/* Status Filter */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg text-xs">
                {['PENDING', 'APPROVED', 'REJECTED'].map((st) => (
                  <button
                    key={st}
                    onClick={() => setUpdateFilter(st)}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      updateFilter === st
                        ? 'bg-white text-slate-800 shadow-2xs'
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    {st} ({updates.filter((u) => u.review_status === st).length})
                  </button>
                ))}
              </div>
            </div>

            {/* Updates List */}
            <div className="space-y-3">
              {filteredUpdates.map((upd) => (
                <div
                  key={upd.id}
                  className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-3 transition hover:border-slate-300"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-slate-900 text-sm">{upd.scheme_id}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        {upd.change_type}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          upd.review_status === 'APPROVED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : upd.review_status === 'REJECTED'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        Status: {upd.review_status}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <span>Confidence: {Math.round((upd.confidence || 0.85) * 100)}%</span>
                      <span>•</span>
                      <span>{upd.created_at ? new Date(upd.created_at).toLocaleString() : 'Recent'}</span>
                    </div>
                  </div>

                  {/* Old vs Proposed Values */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                      <span className="font-semibold text-slate-500 uppercase text-[10px]">
                        {language === 'hi' ? 'मौजूदा नियम / मान' : 'Current Value in Catalog'}
                      </span>
                      <div className="text-slate-700 font-mono text-[11px] whitespace-pre-wrap">
                        {upd.old_value || 'None (New Initiative)'}
                      </div>
                    </div>

                    <div className="p-3 bg-emerald-50/50 border border-emerald-200 rounded-lg space-y-1">
                      <span className="font-semibold text-emerald-800 uppercase text-[10px]">
                        {language === 'hi' ? 'प्रस्तावित नया मान' : 'Proposed New Value'}
                      </span>
                      <div className="text-emerald-950 font-mono text-[11px] whitespace-pre-wrap">
                        {upd.proposed_value}
                      </div>
                    </div>
                  </div>

                  {/* Supporting Source Evidence */}
                  {upd.evidence && (
                    <div className="p-3 bg-amber-50/40 border border-amber-200/80 rounded-lg text-xs space-y-1">
                      <span className="font-semibold text-amber-900 flex items-center gap-1 text-[11px]">
                        <FileCheck className="w-3.5 h-3.5 text-amber-700" />
                        {language === 'hi' ? 'सत्यापित साक्ष्य उद्धरण' : 'Grounded Evidence Citation from Official Source'}
                      </span>
                      <div className="text-amber-950/90 italic font-serif text-[11px]">
                        "{typeof upd.evidence === 'object' ? JSON.stringify(upd.evidence, null, 1) : upd.evidence}"
                      </div>
                      <div className="pt-1 flex items-center gap-1 text-[11px] text-slate-500">
                        <span>Source:</span>
                        <a
                          href={upd.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-emerald-700 hover:underline truncate max-w-md inline-flex items-center gap-1"
                        >
                          {upd.source_url} <ExternalLink className="w-3 h-3 inline" />
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons for Pending Updates */}
                  {upd.review_status === 'PENDING' && (
                    <div className="flex items-center justify-end gap-2 pt-2">
                      <button
                        onClick={() => {
                          setRejectingUpdateId(upd.id);
                          setRejectReason('');
                        }}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition"
                      >
                        <X className="w-3.5 h-3.5" />
                        {language === 'hi' ? 'अस्वीकार करें' : 'Reject'}
                      </button>
                      <button
                        onClick={() => handleApproveUpdate(upd.id)}
                        className="inline-flex items-center gap-1 px-4 py-1.5 rounded-lg text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 shadow-xs transition"
                      >
                        <Check className="w-3.5 h-3.5" />
                        {language === 'hi' ? 'स्वीकृत करें और प्रकाशित करें' : 'Approve & Publish'}
                      </button>
                    </div>
                  )}
                </div>
              ))}

              {filteredUpdates.length === 0 && (
                <div className="bg-white p-12 text-center rounded-xl border border-slate-200 text-slate-400">
                  <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500 mb-2" />
                  <p className="text-sm font-medium text-slate-700">
                    {language === 'hi' ? 'कोई लंबित अपडेट नहीं है।' : 'No updates found in this status category.'}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    {language === 'hi'
                      ? 'नए अपडेट खोजने के लिए "पूर्ण निगरानी चलाएं" पर क्लिक करें।'
                      : 'Click "Run Monitoring" above to check government portals for new changes.'}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* =========================================================================
            SECTION E: VERSION HISTORY
        ========================================================================== */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-slate-900">
                  {language === 'hi' ? 'योजना संस्करण इतिहास एवं ऑडिट ट्रेल' : 'Scheme Version History & Audit Trail'}
                </h2>
                <p className="text-xs text-slate-500">
                  {language === 'hi'
                    ? 'प्रत्येक स्वीकृत नीति परिवर्तन के साथ योजना का अपरिवर्तनीय नया संस्करण सुरक्षित रखा जाता है।'
                    : 'Every approved update creates an immutable version record ensuring transparent traceability.'}
                </p>
              </div>

              {/* Scheme Picker */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">{language === 'hi' ? 'योजना चुनें:' : 'Select Scheme:'}</span>
                <select
                  value={selectedSchemeId}
                  onChange={(e) => {
                    setSelectedSchemeId(e.target.value);
                    loadSchemeVersions(e.target.value);
                  }}
                  className="text-xs bg-white border border-slate-200 rounded-lg px-3 py-1.5 font-medium text-slate-700 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  {schemeCatalog.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name_en} ({s.id})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Version Timeline */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
              {historyLoading ? (
                <div className="py-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-600" />
                  Loading version history...
                </div>
              ) : schemeVersions.length > 0 ? (
                <div className="relative border-l-2 border-emerald-200 ml-4 pl-6 space-y-6">
                  {schemeVersions.map((ver, idx) => (
                    <div key={ver.id || idx} className="relative space-y-2">
                      <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-emerald-600 border-2 border-white ring-2 ring-emerald-100" />
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-slate-900 text-sm">
                          Version {ver.version_number}
                        </span>
                        <span className="px-2 py-0.5 text-[10px] font-semibold rounded-full bg-emerald-100 text-emerald-800">
                          {ver.approval_status || 'APPROVED'}
                        </span>
                        <span className="text-xs text-slate-400">
                          {ver.created_at ? new Date(ver.created_at).toLocaleString() : 'Historical baseline'}
                        </span>
                      </div>

                      {ver.source_url && (
                        <div className="text-xs text-slate-500">
                          Source circular:{' '}
                          <a
                            href={ver.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-700 hover:underline"
                          >
                            {ver.source_url}
                          </a>
                        </div>
                      )}

                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-700 max-h-48 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-[11px]">
                          {JSON.stringify(ver.scheme_data, null, 2)}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">
                  {language === 'hi'
                    ? 'इस योजना के लिए कोई अतिरिक्त संस्करण दर्ज नहीं है। वर्तमान में मूल संस्करण सक्रिय है।'
                    : 'No additional versions recorded for this scheme yet. Baseline v1 is active.'}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Reject Modal */}
      {rejectingUpdateId && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-5 space-y-4 shadow-xl border border-slate-200">
            <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              {language === 'hi' ? 'परिवर्तन अस्वीकृति का कारण' : 'Reason for Rejecting Update'}
            </h3>
            <p className="text-xs text-slate-500">
              {language === 'hi'
                ? 'कृपया ऑडिट रिकॉर्ड हेतु अस्वीकृति का आधिकारिक कारण दर्ज करें।'
                : 'Provide mandatory audit rationale for rejecting this proposed policy change.'}
            </p>
            <textarea
              rows={3}
              placeholder={language === 'hi' ? 'जैसे: विभागीय परिपत्र से विसंगति पाई गई...' : 'e.g. Discrepancy with official departmental gazette notification...'}
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full text-xs p-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-rose-500"
            />
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setRejectingUpdateId(null)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                {language === 'hi' ? 'रद्द करें' : 'Cancel'}
              </button>
              <button
                onClick={handleRejectUpdate}
                disabled={!rejectReason.trim()}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-lg disabled:opacity-50"
              >
                {language === 'hi' ? 'अस्वीकार करें' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
