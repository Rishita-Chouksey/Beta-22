import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  Globe,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ExternalLink,
  History,
  Lock,
  Unlock,
  Eye,
  FileText,
  RotateCcw,
  Sparkles,
  Search,
  Filter,
  ArrowLeft,
  ChevronRight,
  Database,
  Building2
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import {
  fetchMonitoringSummary,
  fetchMonitoringSources,
  fetchMonitoringChanges,
  fetchPendingUpdates,
  fetchSchemeVersionHistory,
  triggerMonitoringRun,
  approveSchemeUpdate,
  rejectSchemeUpdate,
  rollbackSchemeVersion
} from '../services/api';

export default function S9_AdminMonitoringScreen() {
  const { language } = useLanguage();
  const { setCurrentScreen } = useSession();

  // Admin auth state (Held strictly in memory)
  const [adminKey, setAdminKey] = useState('');
  const [keyInput, setKeyInput] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');

  // Dashboard state
  const [activeTab, setActiveTab] = useState('updates'); // 'updates', 'sources', 'activity', 'history'
  const [summary, setSummary] = useState(null);
  const [sources, setSources] = useState([]);
  const [updates, setUpdates] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [includeDemo, setIncludeDemo] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isTriggeringRun, setIsTriggeringRun] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  // Modal states for Approval / Rejection
  const [selectedUpdate, setSelectedUpdate] = useState(null);
  const [modalMode, setModalMode] = useState(null); // 'approve', 'reject', 'inspect'
  const [reviewerName, setReviewerName] = useState('Verification Officer');
  const [decisionReason, setDecisionReason] = useState('');
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);

  // Version History state
  const [selectedSchemeId, setSelectedSchemeId] = useState('ladli_behna_mp');
  const [versionHistory, setVersionHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Auto-login if default dev key is accepted
  const handleAuthenticate = async (e) => {
    e?.preventDefault();
    if (!keyInput.trim()) {
      setAuthError(language === 'hi' ? 'कृपया एडमिन कुंजी दर्ज करें।' : 'Please enter Admin API Key.');
      return;
    }
    setIsLoading(true);
    setAuthError('');
    try {
      const sum = await fetchMonitoringSummary(keyInput.trim());
      setAdminKey(keyInput.trim());
      setSummary(sum);
      setIsAuthenticated(true);
      loadAllDashboardData(keyInput.trim());
    } catch (err) {
      setAuthError(
        language === 'hi'
          ? 'अमान्य एडमिन कुंजी अथवा बैकएंड से कनेक्शन विफल।'
          : 'Invalid Admin Key or access denied. Check backend .env ADMIN_API_KEY.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const loadAllDashboardData = async (key) => {
    setIsLoading(true);
    try {
      const [sumData, sourcesData, updatesData, logsData] = await Promise.all([
        fetchMonitoringSummary(key),
        fetchMonitoringSources(key),
        fetchPendingUpdates(key, includeDemo),
        fetchMonitoringChanges(key, 50),
      ]);
      setSummary(sumData);
      setSources(sourcesData);
      setUpdates(updatesData);
      setActivityLogs(logsData);
    } catch (err) {
      console.error('Failed to load monitoring data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleManualRun = async (sourceId = null) => {
    setIsTriggeringRun(true);
    setActionMessage(null);
    try {
      const res = await triggerMonitoringRun(adminKey, sourceId);
      setActionMessage({
        type: 'success',
        text: res.message || 'Polite monitoring cycle completed successfully.',
      });
      await loadAllDashboardData(adminKey);
    } catch (err) {
      setActionMessage({
        type: 'error',
        text: `Monitoring run error: ${err.message}`,
      });
    } finally {
      setIsTriggeringRun(false);
    }
  };

  const handleOpenDecisionModal = (upd, mode) => {
    setSelectedUpdate(upd);
    setModalMode(mode);
    setDecisionReason(
      mode === 'approve'
        ? 'Verified against official notification. Scheme guidelines confirmed.'
        : 'Discrepancy detected with gazetted departmental rules.'
    );
  };

  const handleConfirmDecision = async () => {
    if (!selectedUpdate || !decisionReason.trim()) return;
    setIsSubmittingDecision(true);
    try {
      if (modalMode === 'approve') {
        const res = await approveSchemeUpdate(
          adminKey,
          selectedUpdate.update_id,
          reviewerName,
          decisionReason
        );
        setActionMessage({ type: 'success', text: res.message });
      } else if (modalMode === 'reject') {
        const res = await rejectSchemeUpdate(
          adminKey,
          selectedUpdate.update_id,
          reviewerName,
          decisionReason
        );
        setActionMessage({ type: 'success', text: res.message });
      }
      setModalMode(null);
      setSelectedUpdate(null);
      await loadAllDashboardData(adminKey);
    } catch (err) {
      setActionMessage({ type: 'error', text: `Action failed: ${err.message}` });
    } finally {
      setIsSubmittingDecision(false);
    }
  };

  const handleLoadVersionHistory = async (schemeId) => {
    setSelectedSchemeId(schemeId);
    setHistoryLoading(true);
    try {
      const res = await fetchSchemeVersionHistory(adminKey, schemeId);
      setVersionHistory(res.versions || []);
    } catch (err) {
      console.error('Failed to load version history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleRollback = async (versionId) => {
    if (!window.confirm('Are you sure you want to restore this historical version as active in the scheme catalogue?')) return;
    try {
      const res = await rollbackSchemeVersion(adminKey, selectedSchemeId, versionId, reviewerName);
      setActionMessage({ type: 'success', text: res.message });
      await handleLoadVersionHistory(selectedSchemeId);
      await loadAllDashboardData(adminKey);
    } catch (err) {
      setActionMessage({ type: 'error', text: `Rollback failed: ${err.message}` });
    }
  };

  useEffect(() => {
    if (activeTab === 'history' && isAuthenticated) {
      handleLoadVersionHistory(selectedSchemeId);
    }
  }, [activeTab, selectedSchemeId, isAuthenticated]);

  // If not authenticated, render Login Screen
  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl border border-slate-200 shadow-xl text-center">
        <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-slate-900 text-teal-400 flex items-center justify-center shadow-lg">
          <Lock className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          {language === 'hi' ? 'योजनासारथी — प्रशासनिक निगरानी डैशबोर्ड' : 'YojnaSarthi — Scheme Intelligence Monitor'}
        </h2>
        <p className="text-xs text-slate-500 mt-2 mb-6">
          {language === 'hi'
            ? 'केवल अधिकृत अधिकारियों के लिए। बैकएंड .env में कॉन्फ़िगर की गई कुंजी दर्ज करें।'
            : 'Restricted administrative portal. Enter the ADMIN_API_KEY configured in backend environment.'}
        </p>

        <form onSubmit={handleAuthenticate} className="space-y-4">
          <div className="text-left">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {language === 'hi' ? 'प्रशासनिक गुप्त कुंजी (Admin Key)' : 'Administrative Access Key'}
            </label>
            <input
              type="password"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              placeholder="yojnasarthi-admin-secret-2026"
              className="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-teal-600 focus:border-teal-600 outline-none"
            />
          </div>

          {authError && (
            <div className="p-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-xl text-left flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{authError}</span>
            </div>
          )}

          <div className="pt-2 flex items-center gap-3">
            <button
              type="button"
              onClick={() => setCurrentScreen('S0')}
              className="w-1/2 py-2.5 border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold rounded-xl transition"
            >
              {language === 'hi' ? 'वापस जाएं' : 'Return to Home'}
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="w-1/2 py-2.5 bg-slate-900 hover:bg-slate-800 text-teal-400 text-xs font-semibold rounded-xl shadow-md transition flex items-center justify-center gap-2"
            >
              {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Unlock className="w-4 h-4" />}
              <span>{language === 'hi' ? 'प्रवेश करें' : 'Unlock Dashboard'}</span>
            </button>
          </div>
        </form>
      </div>
    );
  }

  // Dashboard Interface
  return (
    <div className="space-y-6">
      {/* Top Header & Breadcrumbs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 mb-1">
            <button onClick={() => setCurrentScreen('S0')} className="hover:text-teal-700 flex items-center gap-1">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{language === 'hi' ? 'मुख्य पृष्ठ' : 'Public Portal'}</span>
            </button>
            <span>/</span>
            <span className="text-teal-800">
              {language === 'hi' ? 'प्रशासनिक योजना निगरानी' : 'Scheme Intelligence & Monitoring'}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Building2 className="w-6 h-6 text-teal-700" />
            <span>Scheme Intelligence Monitor</span>
            <span className="text-xs px-2.5 py-1 bg-teal-100 text-teal-800 rounded-full font-semibold border border-teal-200">
              Admin Access Active
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Automated official government source monitoring, change detection, and human-in-the-loop rule approval.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <label className="flex items-center gap-2 text-xs font-medium text-slate-600 bg-white border border-slate-200 px-3 py-2 rounded-xl cursor-pointer">
            <input
              type="checkbox"
              checked={includeDemo}
              onChange={(e) => {
                setIncludeDemo(e.target.checked);
                loadAllDashboardData(adminKey);
              }}
              className="rounded text-teal-600"
            />
            <span>Show Demo Data</span>
          </label>

          <button
            onClick={() => handleManualRun()}
            disabled={isTriggeringRun}
            className="flex items-center gap-1.5 px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white rounded-xl text-xs font-semibold shadow-sm transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isTriggeringRun ? 'animate-spin' : ''}`} />
            <span>{isTriggeringRun ? 'Checking Official Portals...' : 'Run Monitoring Now'}</span>
          </button>

          <button
            onClick={() => setIsAuthenticated(false)}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition"
          >
            <Lock className="w-3.5 h-3.5" />
            <span>Lock Session</span>
          </button>
        </div>
      </div>

      {/* Global Notifications */}
      {actionMessage && (
        <div
          className={`p-3.5 rounded-xl border text-xs flex items-center justify-between ${
            actionMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : 'bg-rose-50 border-rose-200 text-rose-900'
          }`}
        >
          <div className="flex items-center gap-2">
            {actionMessage.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-600" />
            )}
            <span>{actionMessage.text}</span>
          </div>
          <button onClick={() => setActionMessage(null)} className="text-slate-400 hover:text-slate-600">
            ×
          </button>
        </div>
      )}

      {/* Metric Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Monitored Schemes</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{summary.total_schemes_monitored}</div>
            <div className="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
              <Database className="w-3 h-3" /> Core Catalogue
            </div>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Monitored Sources</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{summary.total_sources_monitored}</div>
            <div className="text-[10px] text-emerald-600 mt-1 flex items-center gap-1">
              <Globe className="w-3 h-3" /> Central & MP Portals
            </div>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Changes Detected</div>
            <div className="text-2xl font-bold text-amber-600 mt-1">{summary.changes_detected_count}</div>
            <div className="text-[10px] text-slate-400 mt-1">Fingerprint updates</div>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-amber-200 bg-amber-50/50 shadow-xs">
            <div className="text-[11px] font-semibold text-amber-800 uppercase tracking-wider">Awaiting Review</div>
            <div className="text-2xl font-bold text-amber-700 mt-1">{summary.updates_awaiting_review}</div>
            <div className="text-[10px] text-amber-700 mt-1 font-medium">Pending Human Approval</div>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Verified Rules</div>
            <div className="text-2xl font-bold text-emerald-700 mt-1">{summary.verified_schemes_count}</div>
            <div className="text-[10px] text-emerald-700 mt-1 font-medium">Active in Evaluator</div>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Unavailable Sources</div>
            <div className="text-2xl font-bold text-rose-600 mt-1">{summary.outdated_or_unavailable_sources}</div>
            <div className="text-[10px] text-slate-400 mt-1">Timeouts / Degraded</div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 space-x-2 sm:space-x-4 overflow-x-auto text-xs font-semibold">
        <button
          onClick={() => setActiveTab('updates')}
          className={`pb-3 px-2 border-b-2 transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'updates'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span>Pending Updates</span>
          {summary && summary.updates_awaiting_review > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-amber-100 text-amber-800 font-bold">
              {summary.updates_awaiting_review}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('sources')}
          className={`pb-3 px-2 border-b-2 transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'sources'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Globe className="w-4 h-4" />
          <span>Official Sources Health ({sources.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('activity')}
          className={`pb-3 px-2 border-b-2 transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'activity'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Activity className="w-4 h-4" />
          <span>Activity Audit Trail</span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`pb-3 px-2 border-b-2 transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'history'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <History className="w-4 h-4" />
          <span>Version History & Rollback</span>
        </button>
      </div>

      {/* TAB 1: PENDING UPDATES */}
      {activeTab === 'updates' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing changes detected from official portals. AI assists analysis; human verification is mandatory.
            </span>
            <span>Total: {updates.length}</span>
          </div>

          {updates.length === 0 ? (
            <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-slate-800">All Schemes Up to Date</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                No pending changes detected from official government portals awaiting human verification.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {updates.map((upd) => (
                <div
                  key={upd.update_id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-base text-slate-900">{upd.scheme_name_en}</span>
                        {upd.is_demo ? (
                          <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-indigo-100 text-indigo-700 border border-indigo-200">
                            DEMO / SYNTHETIC DATA
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200">
                            LIVE OFFICIAL CHANGE
                          </span>
                        )}
                        <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-200 uppercase">
                          {upd.change_type}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 mt-1 flex items-center gap-3">
                        <span>Source: {upd.source_id}</span>
                        <span>•</span>
                        <span>Detected: {upd.detected_at}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <a
                        href={upd.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-3 py-1.5 border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-xl text-xs font-semibold transition"
                      >
                        <ExternalLink className="w-3.5 h-3.5 text-teal-700" />
                        <span>Official Portal</span>
                      </a>
                    </div>
                  </div>

                  {/* Side-by-side snippet comparison */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 my-4 text-xs">
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                      <div className="font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-slate-500" />
                        <span>Previous Verified Portal Text</span>
                      </div>
                      <p className="text-slate-600 whitespace-pre-wrap leading-relaxed">
                        {upd.old_content_snippet || 'No previous snippet captured.'}
                      </p>
                    </div>

                    <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-xl">
                      <div className="font-semibold text-amber-900 mb-1 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                        <span>New Detected Portal Text</span>
                      </div>
                      <p className="text-amber-900 whitespace-pre-wrap leading-relaxed">
                        {upd.new_content_snippet || 'No new snippet captured.'}
                      </p>
                    </div>
                  </div>

                  {/* AI-assisted analysis box */}
                  <div className="p-3.5 bg-gradient-to-r from-teal-50/70 to-blue-50/70 border border-teal-200 rounded-xl text-xs mb-4">
                    <div className="flex items-center gap-1.5 font-bold text-teal-900 mb-1">
                      <Sparkles className="w-4 h-4 text-teal-600" />
                      <span>AI Policy Diff Analysis (Grounded in Verified Excerpts)</span>
                    </div>
                    <div className="text-slate-700 whitespace-pre-wrap leading-relaxed pl-5 border-l-2 border-teal-400">
                      {upd.ai_analysis_summary}
                    </div>
                    <p className="text-[10px] text-slate-500 mt-2 pl-5">
                      ⚠️ Note: AI analysis is for reviewer guidance only. Only human review decisions can alter executable rules.
                    </p>
                  </div>

                  {/* Review Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                    <div className="text-xs text-slate-500">
                      Status: <span className="font-semibold text-slate-800">{upd.status}</span>
                      {upd.decision_by && (
                        <span>
                          {' '}
                          (By {upd.decision_by} on {upd.decision_at})
                        </span>
                      )}
                    </div>

                    {upd.status === 'PENDING' ? (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleOpenDecisionModal(upd, 'reject')}
                          className="px-3.5 py-1.5 border border-rose-200 text-rose-700 hover:bg-rose-50 rounded-xl text-xs font-semibold transition"
                        >
                          Reject Update
                        </button>
                        <button
                          onClick={() => handleOpenDecisionModal(upd, 'approve')}
                          className="px-4 py-1.5 bg-teal-700 hover:bg-teal-800 text-white rounded-xl text-xs font-semibold shadow-xs transition"
                        >
                          Approve & Publish
                        </button>
                      </div>
                    ) : (
                      <span
                        className={`text-xs font-semibold px-3 py-1 rounded-full ${
                          upd.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {upd.status}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: OFFICIAL SOURCES HEALTH */}
      {activeTab === 'sources' && (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Monitored Government Portals Registry
            </span>
            <span className="text-xs text-slate-500">{sources.length} Total Sources</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <th className="p-3 pl-4">Portal / Source Name</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Frequency</th>
                  <th className="p-3">Health Status</th>
                  <th className="p-3">Robots.txt</th>
                  <th className="p-3">Last Check</th>
                  <th className="p-3 pr-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {sources.map((src) => (
                  <tr key={src.source_id} className="hover:bg-slate-50/80 transition">
                    <td className="p-3 pl-4">
                      <div className="font-bold text-slate-900">{src.name}</div>
                      <a
                        href={src.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-teal-700 hover:underline flex items-center gap-1 mt-0.5"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>{src.official_url}</span>
                      </a>
                    </td>
                    <td className="p-3">
                      <span className="capitalize px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium text-[11px]">
                        {src.category.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-[11px]">{src.source_type}</td>
                    <td className="p-3 capitalize">{src.monitoring_frequency}</td>
                    <td className="p-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold text-[11px] ${
                          src.accessibility_status === 'healthy'
                            ? 'bg-emerald-100 text-emerald-800'
                            : src.accessibility_status === 'degraded'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {src.accessibility_status === 'healthy' ? (
                          <CheckCircle2 className="w-3 h-3" />
                        ) : (
                          <AlertTriangle className="w-3 h-3" />
                        )}
                        <span className="capitalize">{src.accessibility_status}</span>
                      </span>
                      {src.error_details && (
                        <div className="text-[10px] text-rose-600 mt-1 max-w-xs truncate" title={src.error_details}>
                          {src.error_details}
                        </div>
                      )}
                    </td>
                    <td className="p-3">
                      {src.automated_monitoring_permitted ? (
                        <span className="text-emerald-700 font-semibold">Allowed</span>
                      ) : (
                        <span className="text-rose-700 font-semibold">Disallowed</span>
                      )}
                    </td>
                    <td className="p-3 text-slate-500">{src.last_successful_check || 'Pending first run'}</td>
                    <td className="p-3 pr-4">
                      <button
                        onClick={() => handleManualRun(src.source_id)}
                        disabled={isTriggeringRun}
                        className="px-2.5 py-1 text-[11px] font-semibold border border-slate-200 text-slate-700 hover:bg-slate-100 rounded-lg transition"
                      >
                        Check
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: ACTIVITY LOGS */}
      {activeTab === 'activity' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Monitoring Activity Audit Trail
            </h3>
            <span className="text-xs text-slate-500">Last 50 Events</span>
          </div>

          <div className="divide-y divide-slate-100">
            {activityLogs.map((log) => (
              <div key={log.id} className="py-2.5 flex items-start justify-between gap-4 text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.status === 'SUCCESS'
                          ? 'bg-emerald-100 text-emerald-800'
                          : log.status === 'CHANGE_DETECTED'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {log.status}
                    </span>
                    <span className="font-semibold text-slate-800">{log.source_id}</span>
                    {log.is_demo && (
                      <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">DEMO</span>
                    )}
                  </div>
                  <p className="text-slate-600 mt-1">{log.details}</p>
                </div>
                <span className="text-[11px] text-slate-400 whitespace-nowrap">{log.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: VERSION HISTORY & ROLLBACK */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Scheme Version History & Rollback
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Inspect historical approved versions and restore previous rules if required.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-slate-700">Select Scheme:</label>
              <select
                value={selectedSchemeId}
                onChange={(e) => handleLoadVersionHistory(e.target.value)}
                className="px-3 py-1.5 text-xs border border-slate-300 rounded-xl bg-white outline-none"
              >
                <option value="ladli_behna_mp">Mukhyamantri Ladli Behna Yojana (MP)</option>
                <option value="mmvy_scholarship">MMVY Scholarship (MP)</option>
                <option value="pm_kisan">PM-KISAN Samman Nidhi (Central)</option>
                <option value="pm_jay_ayushman">PM-JAY Ayushman Bharat (Central)</option>
                <option value="pm_awas_yojana_gramin">PMAY-Gramin (Central)</option>
                <option value="ignwps_widow_pension">IGNWPS Widow Pension (Central)</option>
              </select>
            </div>
          </div>

          {historyLoading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading version records...</div>
          ) : versionHistory.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No historical revisions archived yet for {selectedSchemeId}. Currently running on base verified catalogue.
            </div>
          ) : (
            <div className="space-y-3">
              {versionHistory.map((ver) => (
                <div
                  key={ver.version_id}
                  className="p-4 border border-slate-200 rounded-xl bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900">Version {ver.version_number}</span>
                      <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 font-semibold rounded-full text-[10px]">
                        {ver.review_status}
                      </span>
                    </div>
                    <p className="text-slate-600 mt-1">{ver.change_summary || 'Approved scheme rule snapshot.'}</p>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Approved by <span className="font-medium text-slate-700">{ver.approved_by || 'Officer'}</span> on{' '}
                      {ver.approved_at || ver.created_at}
                    </div>
                  </div>

                  <button
                    onClick={() => handleRollback(ver.version_id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-100 rounded-xl font-semibold transition"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Restore Version {ver.version_number}</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Decision Modal (Approve or Reject) */}
      {modalMode && selectedUpdate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
                {modalMode === 'approve' ? (
                  <>
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    <span>Approve & Publish Update</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-rose-600" />
                    <span>Reject Scheme Update</span>
                  </>
                )}
              </h3>
              <button onClick={() => setModalMode(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                ×
              </button>
            </div>

            <div className="text-xs text-slate-600 space-y-1">
              <div>
                <span className="font-semibold text-slate-800">Scheme:</span> {selectedUpdate.scheme_name_en}
              </div>
              <div>
                <span className="font-semibold text-slate-800">Update ID:</span> {selectedUpdate.update_id}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Authorizing Reviewer Name</label>
              <input
                type="text"
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Audit Rationale / Reason</label>
              <textarea
                rows={3}
                value={decisionReason}
                onChange={(e) => setDecisionReason(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-teal-600"
                placeholder="Specify the reason for this decision..."
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setModalMode(null)}
                className="px-4 py-2 border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold rounded-xl transition"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSubmittingDecision || !decisionReason.trim()}
                onClick={handleConfirmDecision}
                className={`px-4 py-2 text-xs font-semibold rounded-xl text-white shadow-xs transition flex items-center gap-1.5 ${
                  modalMode === 'approve'
                    ? 'bg-teal-700 hover:bg-teal-800'
                    : 'bg-rose-700 hover:bg-rose-800'
                }`}
              >
                {isSubmittingDecision ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : null}
                <span>{modalMode === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
