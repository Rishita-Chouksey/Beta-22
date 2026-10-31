import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchDocumentList, fetchDocumentDetails } from '../services/api';
import {
  FileText,
  Search,
  ExternalLink,
  ArrowLeft,
  ShieldCheck,
  CheckCircle2,
  Building2,
  ListChecks,
  FileCheck2,
  AlertCircle,
  HelpCircle,
  MapPin,
  Sparkles,
  Printer,
  ChevronRight,
  Info
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S8_DocumentGuideScreen() {
  const { language, t } = useLanguage();
  const {
    currentScreen,
    setCurrentScreen,
    selectedDocId,
    setSelectedDocId,
    docGuideReturnScreen,
    setDocGuideReturnScreen,
    activeSchemeModal,
    setActiveSchemeModal
  } = useSession();

  const [documents, setDocuments] = useState([]);
  const [activeDoc, setActiveDoc] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch documents list on mount
  useEffect(() => {
    setIsLoading(true);
    fetchDocumentList()
      .then((data) => {
        setDocuments(data);
        setError(null);
      })
      .catch((err) => {
        console.error('Error fetching documents list:', err);
        setError('Could not load document catalog.');
      })
      .finally(() => setIsLoading(false));
  }, []);

  // Fetch active document details if selectedDocId changes
  useEffect(() => {
    if (selectedDocId) {
      setIsLoading(true);
      fetchDocumentDetails(selectedDocId)
        .then((doc) => {
          setActiveDoc(doc);
          setError(null);
        })
        .catch((err) => {
          console.error('Error fetching document details:', err);
          setError('Document details could not be retrieved.');
        })
        .finally(() => setIsLoading(false));
    } else {
      setActiveDoc(null);
    }
  }, [selectedDocId]);

  const handleReturn = () => {
    if (docGuideReturnScreen === 'S5' && activeSchemeModal) {
      // Re-open scheme details modal
      setCurrentScreen('S4');
    } else if (docGuideReturnScreen) {
      setCurrentScreen(docGuideReturnScreen);
    } else {
      setCurrentScreen('S0');
    }
    setDocGuideReturnScreen(null);
  };

  const categories = [
    { id: 'all', label_en: 'All Documents', label_hi: 'सभी दस्तावेज़' },
    { id: 'Identity', label_en: 'Identity', label_hi: 'पहचान प्रमाण' },
    { id: 'Revenue', label_en: 'Revenue & Income', label_hi: 'आय एवं राजस्व' },
    { id: 'Residence', label_en: 'Residence / Domicile', label_hi: 'मूल निवास' },
    { id: 'Social Security', label_en: 'Social Security', label_hi: 'सामाजिक सुरक्षा' },
    { id: 'Land', label_en: 'Land Records', label_hi: 'भूमि अभिलेख' },
    { id: 'Education', label_en: 'Education', label_hi: 'शिक्षा प्रमाण' }
  ];

  const filteredDocs = documents.filter((doc) => {
    const matchesCat = selectedCategory === 'all' || doc.category.toLowerCase() === selectedCategory.toLowerCase();
    const q = searchQuery.toLowerCase().trim();
    const matchesQuery =
      !q ||
      doc.name_en.toLowerCase().includes(q) ||
      doc.name_hi.toLowerCase().includes(q) ||
      doc.short_explanation_en.toLowerCase().includes(q) ||
      doc.short_explanation_hi.toLowerCase().includes(q);
    return matchesCat && matchesQuery;
  });

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Top Navigation & Context Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          {docGuideReturnScreen ? (
            <button
              onClick={handleReturn}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-blue-50 text-blue-800 hover:bg-blue-100 font-semibold text-xs border border-blue-200 transition-all shadow-2xs"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>
                {docGuideReturnScreen === 'S5'
                  ? (language === 'hi' ? 'योजना विवरण पर लौटें' : 'Return to Scheme')
                  : docGuideReturnScreen === 'S6'
                  ? (language === 'hi' ? 'दस्तावेज़ चेकलिस्ट पर लौटें' : 'Return to Checklist')
                  : (language === 'hi' ? 'वापस जाएं' : 'Go Back')}
              </span>
            </button>
          ) : (
            <button
              onClick={() => setCurrentScreen('S0')}
              className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{language === 'hi' ? 'होम पर जाएं' : 'Home'}</span>
            </button>
          )}

          <div className="h-4 w-px bg-slate-300 hidden sm:block"></div>

          <div className="flex items-center gap-1 text-xs text-slate-600">
            <span
              onClick={() => setSelectedDocId(null)}
              className={`cursor-pointer hover:text-blue-700 ${!selectedDocId ? 'font-bold text-slate-900' : ''}`}
            >
              {language === 'hi' ? 'दस्तावेज़ मार्गदर्शिका (Document Guide)' : 'Document Guide'}
            </span>
            {activeDoc && (
              <>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                <span className="font-bold text-slate-900 line-clamp-1">
                  {language === 'hi' ? activeDoc.name_hi : activeDoc.name_en}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Global badge */}
        <div className="flex items-center gap-2 text-xs text-slate-500 self-start sm:self-auto">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>
            {language === 'hi'
              ? 'सत्यापित आधिकारिक पोर्टल एवं प्रक्रियाएं'
              : 'Verified Government Portals & Procedures'}
          </span>
        </div>
      </div>

      {/* VIEW A: Single Document Detail View */}
      {activeDoc ? (
        <div className="space-y-8 animate-fade-in">
          {/* Header Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 text-[11px] font-bold uppercase tracking-wider rounded-full bg-blue-100 text-blue-800">
                    {activeDoc.category}
                  </span>
                  <span
                    className={`px-3 py-1 text-[11px] font-bold rounded-full border ${
                      activeDoc.is_online_available
                        ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                        : 'bg-amber-50 text-amber-900 border-amber-200'
                    }`}
                  >
                    {activeDoc.is_online_available
                      ? (language === 'hi' ? 'ऑनलाइन आवेदन उपलब्ध' : 'Online Application Available')
                      : (language === 'hi' ? 'तहसील / केंद्र पर व्यक्तिगत उपस्थिति' : 'Offline / In-Person Visit')}
                  </span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  {language === 'hi' ? activeDoc.name_hi : activeDoc.name_en}
                </h1>
                <p className="text-sm text-slate-600 leading-relaxed max-w-3xl">
                  {language === 'hi' ? activeDoc.short_explanation_hi : activeDoc.short_explanation_en}
                </p>
              </div>

              {/* Audio Read-Aloud & Actions */}
              <div className="flex items-center gap-3">
                <AudioSpeaker
                  text={`${language === 'hi' ? activeDoc.name_hi : activeDoc.name_en}। ${
                    language === 'hi' ? activeDoc.short_explanation_hi : activeDoc.short_explanation_en
                  }`}
                  className="w-10 h-10 shadow-sm"
                />
                {activeDoc.apply_url && (
                  <a
                    href={activeDoc.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs sm:text-sm rounded-xl shadow-md hover:shadow-lg transition-all"
                  >
                    <span>{language === 'hi' ? 'आवेदन पोर्टल पर जाएं' : 'Apply on Official Portal'}</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>

            {/* Offline vs Online note callout */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-700 flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-900 block">
                  {language === 'hi' ? 'आवेदन माध्यम एवं जारीकर्ता प्राधिकरण:' : 'Application Mode & Issuing Office:'}
                </span>
                <span>
                  {language === 'hi'
                    ? `${activeDoc.application_mode_note_hi} (${activeDoc.issuing_authority_note_hi})`
                    : `${activeDoc.application_mode_note_en} (${activeDoc.issuing_authority_note_en})`}
                </span>
              </div>
            </div>
          </div>

          {/* 2-Column Content Grid: Left Details, Right Sample Document */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Column: Explanations, Criteria & Steps */}
            <div className="lg:col-span-7 space-y-6">
              {/* 1. Why schemes ask for this */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-3">
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 text-blue-900">
                  <HelpCircle className="w-4 h-4 text-blue-700" />
                  <span>{language === 'hi' ? 'सरकारी योजनाएं यह दस्तावेज़ क्यों मांगती हैं?' : 'Why Do Government Schemes Require This?'}</span>
                </h2>
                <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                  {language === 'hi' ? activeDoc.why_schemes_ask_hi : activeDoc.why_schemes_ask_en}
                </p>
              </div>

              {/* 2. Who issues this */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-3">
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 text-indigo-900">
                  <Building2 className="w-4 h-4 text-indigo-700" />
                  <span>{language === 'hi' ? 'यह दस्तावेज़ कौन जारी करता है?' : 'Who Issues This Document?'}</span>
                </h2>
                <p className="text-xs sm:text-sm font-semibold text-slate-900">
                  {language === 'hi' ? activeDoc.issuer_hi : activeDoc.issuer_en}
                </p>
              </div>

              {/* 3. What information it contains */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-3">
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 text-slate-800">
                  <FileText className="w-4 h-4 text-slate-600" />
                  <span>{language === 'hi' ? 'इस दस्तावेज़ में क्या जानकारी होती है?' : 'What Information Does It Contain?'}</span>
                </h2>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-700">
                  {(language === 'hi' ? activeDoc.contents_hi : activeDoc.contents_en).map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 4. Requirements to obtain it */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-3">
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 text-amber-900">
                  <ListChecks className="w-4 h-4 text-amber-700" />
                  <span>{language === 'hi' ? 'इसे बनवाने हेतु आवश्यक दस्तावेज़ एवं जानकारी:' : 'Documents Needed to Apply For It:'}</span>
                </h2>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-700">
                  {(language === 'hi' ? activeDoc.required_for_application_hi : activeDoc.required_for_application_en).map((reqItem, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-600 flex-shrink-0 mt-2"></span>
                      <span>{reqItem}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 5. Step-by-Step Instructions */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 text-blue-900">
                  <FileCheck2 className="w-4 h-4 text-blue-700" />
                  <span>{language === 'hi' ? 'आवेदन करने के सरल चरण (Step-by-Step Instructions):' : 'Step-by-Step Application Instructions:'}</span>
                </h2>
                <div className="space-y-3">
                  {(language === 'hi' ? activeDoc.application_steps_hi : activeDoc.application_steps_en).map((step, idx) => (
                    <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs sm:text-sm text-slate-800 leading-relaxed">
                      {step}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Synthetic Illustrative Sample Preview */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-white border-2 border-slate-300 rounded-2xl shadow-md p-6 space-y-4 relative overflow-hidden">
                {/* Illustrative Watermark Ribbon */}
                <div className="bg-amber-500/10 border-b border-amber-300 text-amber-900 text-[10px] font-black tracking-widest uppercase p-2 -mx-6 -mt-6 text-center select-none">
                  ⚠️ {activeDoc.sample_preview.watermark_text}
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                      {language === 'hi' ? 'काल्पनिक प्रारूप (Synthetic Preview)' : 'Synthetic Document Preview'}
                    </span>
                    <h3 className="font-extrabold text-slate-900 text-base">
                      {language === 'hi' ? activeDoc.name_hi : activeDoc.name_en}
                    </h3>
                  </div>
                  <span className="text-2xl">🏛️</span>
                </div>

                {/* Synthetic Certificate Layout Mockup */}
                <div className="border border-slate-200 rounded-xl p-5 bg-gradient-to-b from-amber-50/20 via-white to-blue-50/10 space-y-3 font-mono text-xs relative">
                  {/* Diagonal background watermark */}
                  <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none select-none rotate-[-25deg]">
                    <span className="text-2xl font-black text-slate-900 tracking-wider text-center">
                      ILLUSTRATIVE SAMPLE<br />NOT OFFICIAL
                    </span>
                  </div>

                  <div className="text-center pb-2 border-b border-slate-200">
                    <p className="font-bold text-[11px] text-slate-800">
                      {activeDoc.sample_preview.issuing_authority}
                    </p>
                    <p className="text-[10px] text-slate-500">
                      {language === 'hi' ? 'आधिकारिक नागरिक प्रमाण पत्र प्रारूप' : 'Official Citizen Certificate Layout'}
                    </p>
                  </div>

                  <div className="space-y-2 py-2">
                    <div className="flex justify-between items-center text-[11px] bg-slate-100/70 p-2 rounded">
                      <span className="text-slate-500">Document No:</span>
                      <span className="font-bold text-slate-900">{activeDoc.sample_preview.document_number}</span>
                    </div>

                    <div className="flex justify-between items-center text-[11px] bg-slate-100/70 p-2 rounded">
                      <span className="text-slate-500">Holder Name:</span>
                      <span className="font-bold text-blue-900">{activeDoc.sample_preview.holder_name}</span>
                    </div>

                    {Object.entries(activeDoc.sample_preview.key_fields).map(([k, v], i) => (
                      <div key={i} className="flex justify-between items-start text-[11px] border-b border-slate-100 pb-1">
                        <span className="text-slate-500">{k}:</span>
                        <span className="font-semibold text-slate-800 text-right max-w-[60%]">{v}</span>
                      </div>
                    ))}
                  </div>

                  {/* QR Code and Seal Placeholder */}
                  <div className="pt-3 border-t border-slate-200 flex items-center justify-between text-[10px] text-slate-500">
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 border border-slate-300 rounded bg-slate-100 flex items-center justify-center font-bold text-slate-400">
                        QR
                      </div>
                      <span className="leading-tight">Digital Verification<br />Barcode Area</span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-slate-700 block">Digitally Signed</span>
                      <span className="text-[9px]">Competent Authority</span>
                    </div>
                  </div>
                </div>

                {/* Prominent Legal Disclaimer */}
                <div className="text-[11px] text-slate-500 bg-slate-50 p-3 rounded-xl border border-slate-200 leading-relaxed space-y-1">
                  <p className="font-semibold text-slate-700">
                    {language === 'hi' ? '⚠️ कानूनी अस्वीकरण (Disclaimer):' : '⚠️ Important Notice:'}
                  </p>
                  <p>
                    {language === 'hi' ? activeDoc.sample_preview.disclaimer_hi : activeDoc.sample_preview.disclaimer_en}
                  </p>
                  <p className="text-[10px] text-slate-400">
                    {language === 'hi'
                      ? 'यह नमूना केवल लेआउट और फ़ील्ड्स को समझाने हेतु बनाया गया है। इसमें किसी भी वास्तविक नागरिक का डेटा सम्मिलित नहीं है।'
                      : 'This sample illustrates standard layouts only and does not contain any real citizen data or valid security marks.'}
                  </p>
                </div>

                {/* Apply button & Return CTA */}
                <div className="pt-2 space-y-3">
                  {activeDoc.apply_url && (
                    <a
                      href={activeDoc.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-700 hover:bg-blue-800 text-white font-bold text-sm rounded-xl shadow-md hover:shadow-lg transition-all"
                    >
                      <span>{language === 'hi' ? 'दस्तावेज़ हेतु आवेदन करें' : 'Apply for this Document'}</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}

                  <button
                    onClick={() => setSelectedDocId(null)}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 font-semibold text-xs text-slate-700 transition-all"
                  >
                    <span>{language === 'hi' ? '← सभी दस्तावेज़ देखें' : '← View All Documents in Guide'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* VIEW B: Document Catalogue Grid */
        <div className="space-y-8 animate-fade-in">
          {/* Header & Hero */}
          <div className="bg-gradient-to-b from-white to-blue-50/40 border border-slate-200 rounded-2xl p-6 sm:p-10 shadow-xs space-y-4">
            <div className="max-w-3xl space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-900 text-xs font-bold uppercase tracking-wider">
                <span>📚 {language === 'hi' ? 'नागरिक दस्तावेज़ मार्गदर्शिका' : 'Citizen Document Guide'}</span>
              </div>
              <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                {language === 'hi'
                  ? 'सरकारी योजनाओं हेतु आवश्यक दस्तावेज़ एवं आवेदन प्रक्रिया'
                  : 'Common Government Documents & Procurement Guide'}
              </h1>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                {language === 'hi'
                  ? 'आय प्रमाण पत्र, मूल निवास, जाति प्रमाण पत्र, समग्र आईडी एवं आधार कार्ड के बारे में जानें, उनके काल्पनिक नमूने देखें, और आधिकारिक पोर्टल से सीधे आवेदन करें।'
                  : 'Understand what certificates are required, view illustrative synthetic samples, know where to apply, and get direct links to official government application portals.'}
              </p>
            </div>

            {/* Search Input Bar */}
            <div className="pt-4 max-w-xl">
              <div className="relative">
                <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={
                    language === 'hi'
                      ? 'दस्तावेज़ का नाम खोजें (जैसे: आय, निवास, आधार, समग्र)...'
                      : 'Search document name (e.g. Income, Domicile, Aadhaar, Land)...'
                  }
                  className="w-full pl-11 pr-4 py-3 bg-white border border-slate-300 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all shadow-xs"
                />
              </div>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                  selectedCategory === cat.id
                    ? 'bg-blue-700 text-white shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                {language === 'hi' ? cat.label_hi : cat.label_en}
              </button>
            ))}
          </div>

          {/* Documents Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredDocs.map((doc) => (
              <div
                key={doc.id}
                onClick={() => setSelectedDocId(doc.id)}
                className="bg-white border border-slate-200 hover:border-blue-400 hover:shadow-md rounded-2xl p-6 flex flex-col justify-between transition-all cursor-pointer group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700">
                      {doc.category}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        doc.is_online_available
                          ? 'bg-emerald-50 text-emerald-700'
                          : 'bg-amber-50 text-amber-800'
                      }`}
                    >
                      {doc.is_online_available
                        ? (language === 'hi' ? 'ऑनलाइन' : 'Online')
                        : (language === 'hi' ? 'ऑफलाइन / केंद्र' : 'In-Person')}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-slate-900 text-base group-hover:text-blue-700 transition-colors">
                      {language === 'hi' ? doc.name_hi : doc.name_en}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                      {language === 'hi' ? doc.short_explanation_hi : doc.short_explanation_en}
                    </p>
                  </div>

                  <div className="text-[11px] text-slate-500 pt-1">
                    <span className="font-semibold text-slate-700">
                      {language === 'hi' ? 'जारीकर्ता: ' : 'Issued by: '}
                    </span>
                    <span>{language === 'hi' ? doc.issuer_hi : doc.issuer_en}</span>
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-blue-700">
                  <span className="flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    <span>{language === 'hi' ? 'मार्गदर्शिका एवं नमूना देखें' : 'View Guide & Sample'}</span>
                    <ChevronRight className="w-4 h-4" />
                  </span>
                  <span className="text-base">📄</span>
                </div>
              </div>
            ))}
          </div>

          {filteredDocs.length === 0 && (
            <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 space-y-2">
              <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
              <p className="font-bold text-slate-800">
                {language === 'hi' ? 'कोई दस्तावेज़ नहीं मिला' : 'No documents matched your search'}
              </p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                }}
                className="text-xs text-blue-700 font-semibold hover:underline"
              >
                {language === 'hi' ? 'सभी फ़िल्टर साफ़ करें' : 'Clear all filters'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
