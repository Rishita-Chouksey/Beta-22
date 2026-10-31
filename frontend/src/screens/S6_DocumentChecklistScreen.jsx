import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchDocumentChecklist } from '../services/api';
import {
  ArrowLeft,
  Printer,
  CheckSquare,
  Square,
  ExternalLink,
  MapPin,
  FileCheck,
  ShieldCheck,
  Calendar,
  Sparkles,
  Info,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Eye,
  FileText
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

// Rich illustrative sample document configurations
const DOCUMENT_SAMPLES_CONFIG = {
  aadhaar: {
    sampleType: 'id_card',
    issuer_en: 'Unique Identification Authority of India (UIDAI)',
    issuer_hi: 'भारतीय विशिष्ट पहचान प्राधिकरण (UIDAI)',
    docNumberPlaceholder: 'XXXX XXXX 1234',
    watermark: 'GOVERNMENT OF INDIA',
    checkpoints_en: [
      '12-digit Aadhaar number clearly legible and matches biometric record.',
      'Exact Date of Birth (DOB) recorded (DD/MM/YYYY), not just birth year.',
      'Active mobile number linked with Aadhaar for OTP verification.',
      'Name spelling matches your bank account and school records exactly.'
    ],
    checkpoints_hi: [
      '12 अंकों का आधार क्रमांक स्पष्ट हो और बायोमेट्रिक रिकॉर्ड से मेल खाता हो।',
      'सटीक जन्म तिथि (DD/MM/YYYY) दर्ज हो, केवल जन्म वर्ष नहीं।',
      'ओटीपी सत्यापन के लिए आधार से सक्रिय मोबाइल नंबर जुड़ा होना चाहिए।',
      'नाम की स्पेलिंग बैंक खाते और अन्य दस्तावेजों से पूर्णतः मेल खानी चाहिए।'
    ]
  },
  income_cert: {
    sampleType: 'certificate',
    issuer_en: 'Revenue Department / Sub-Divisional Magistrate (SDM) / Tehsildar',
    issuer_hi: 'राजस्व विभाग / अनुविभागीय अधिकारी (SDM) / तहसीलदार',
    docNumberPlaceholder: 'MP/INC/2026/89421',
    watermark: 'OFFICIAL REVENUE SEAL',
    checkpoints_en: [
      'Total annual family income must be under the scheme ceiling (e.g., ₹6 Lakhs for MMVY).',
      'Valid Tehsildar / SDM digital signature with official QR code/barcode.',
      'Certificate must be within statutory validity period (typically 3 financial years).',
      'Family members and village/town address clearly stated.'
    ],
    checkpoints_hi: [
      'कुल वार्षिक पारिवारिक आय योजना सीमा (जैसे ₹6 लाख) के भीतर होनी चाहिए।',
      'तहसीलदार/एसडीएम के मान्य डिजिटल हस्ताक्षर एवं आधिकारिक बारकोड उपस्थित हो।',
      'प्रमाण पत्र वैधानिक वैधता अवधि (सामान्यतः 3 वित्तीय वर्ष) के भीतर होना चाहिए।',
      'परिवार के सदस्यों और गांव/शहर का सही पता दर्ज हो।'
    ]
  },
  income_cert_tehsildar: {
    sampleType: 'certificate',
    issuer_en: 'Tehsildar Office (Government of Maharashtra - Aaple Sarkar)',
    issuer_hi: 'तहसीलदार कार्यालय (महाराष्ट्र शासन - आपले सरकार)',
    docNumberPlaceholder: 'MH/REV/INC/44912',
    watermark: 'REVENUE DIVISION MH',
    checkpoints_en: [
      'Total annual family income must not exceed ₹21,000 for Sanjay Gandhi Niradhar.',
      'Talathi local spot enquiry report attached or endorsed by Tehsildar.',
      'Current financial year validity.'
    ],
    checkpoints_hi: [
      'संजय गांधी निराधार योजना हेतु कुल वार्षिक आय ₹21,000 से अधिक नहीं होनी चाहिए।',
      'तलाठी की स्थानीय जांच रिपोर्ट तहसीलदार द्वारा समर्थित होनी चाहिए।',
      'वर्तमान वित्तीय वर्ष की वैधता दर्ज हो।'
    ]
  },
  mp_domicile: {
    sampleType: 'certificate',
    issuer_en: 'MP Lok Seva Kendra / Sub-Divisional Magistrate (SDM)',
    issuer_hi: 'लोक सेवा प्रबंधन विभाग, मध्य प्रदेश शासन',
    docNumberPlaceholder: 'MP/DOM/2026/33102',
    watermark: 'MOOL NIWAS PRAMAN PATRA',
    checkpoints_en: [
      'Confirms permanent resident status in Madhya Pradesh.',
      'Issued by authorized Sub-Divisional Officer (Civil) or Tehsildar.',
      'Includes digital verification barcode verifiable on mpedistrict.gov.in.'
    ],
    checkpoints_hi: [
      'मध्य प्रदेश का स्थायी मूल निवासी होने की पुष्टि करता हो।',
      'अधिकृत अनुविभागीय अधिकारी (राजस्व) या तहसीलदार द्वारा जारी हो।',
      'mpedistrict.gov.in पर सत्यापन हेतु डिजिटल बारकोड उपस्थित हो।'
    ]
  },
  mh_domicile_15years: {
    sampleType: 'certificate',
    issuer_en: 'Revenue & Forest Department, Maharashtra (Aaple Sarkar)',
    issuer_hi: 'महसूल व वन विभाग, महाराष्ट्र शासन',
    docNumberPlaceholder: 'MH/DOM/15Y/77812',
    watermark: 'MAHARASHTRA RESIDENCE',
    checkpoints_en: [
      'Explicitly certifies continuous residence in Maharashtra for at least 15 years.',
      'Digital signature of Sub-Divisional Officer / Tehsildar.'
    ],
    checkpoints_hi: [
      'महाराष्ट्र में कम से कम 15 वर्षों के निरंतर निवास की स्पष्ट पुष्टि हो।',
      'तहसीलदार/उपविभागीय अधिकारी के डिजिटल हस्ताक्षर दर्ज हों।'
    ]
  },
  bank_passbook: {
    sampleType: 'passbook',
    issuer_en: 'Public Sector / Scheduled Commercial Bank / Post Office',
    issuer_hi: 'राष्ट्रीयकृत बैंक / क्षेत्रीय ग्रामीण बैंक / डाकघर बैंक',
    docNumberPlaceholder: 'A/C: 9182XXXX3401',
    watermark: 'DBT ACTIVE PASSBOOK',
    checkpoints_en: [
      'Single individual account in applicant\'s own name (not joint).',
      'NPCI Aadhaar Seeding / DBT mapping must be ACTIVE.',
      'Branch IFSC Code, MICR, and Account Number clearly printed.'
    ],
    checkpoints_hi: [
      'आवेदक के स्वयं के नाम पर एकल बैंक खाता (संयुक्त खाता न हो)।',
      'एनपीसीआई आधार सीडिंग / डीबीटी मैपिंग सक्रिय (Active) होनी चाहिए।',
      'शाखा का IFSC कोड और खाता संख्या स्पष्ट पठनीय हो।'
    ]
  },
  death_certificate_husband: {
    sampleType: 'certificate',
    issuer_en: 'Civil Registration System / Registrar of Births and Deaths',
    issuer_hi: 'जन्म एवं मृत्यु रजिस्ट्रार / नगर निगम / ग्राम पंचायत',
    docNumberPlaceholder: 'CRS/DTH/2025/11094',
    watermark: 'CIVIL REGISTRATION FORM 6',
    checkpoints_en: [
      'Official Form 6 Death Certificate issued under Registration of Births & Deaths Act.',
      'Husband\'s full name matching marriage records and Aadhaar.',
      'Date of death and place of registration with official seal.'
    ],
    checkpoints_hi: [
      'जन्म-मृत्यु पंजीकरण अधिनियम के तहत जारी आधिकारिक प्रपत्र-6 मृत्यु प्रमाण पत्र।',
      'पति का नाम विवाह और आधार रिकॉर्ड से पूर्णतः मेल खाता हो।',
      'मृत्यु की तिथि और पंजीकरण स्थान आधिकारिक मुहर सहित दर्ज हो।'
    ]
  },
  marksheet_12th: {
    sampleType: 'marksheet',
    issuer_en: 'Board of Secondary Education (MPBSE / CBSE / ICSE)',
    issuer_hi: 'माध्यमिक शिक्षा मंडल (एमपी बोर्ड / सीबीएसई)',
    docNumberPlaceholder: 'ROLL: 26189042',
    watermark: 'HIGHER SECONDARY MARKSHEET',
    checkpoints_en: [
      'Total percentage meets merit cutoff (>=70% MP Board or >=85% CBSE).',
      'Passing year corresponds to direct higher education undergraduate admission.',
      'Candidate name and parents\' names match Aadhaar card.'
    ],
    checkpoints_hi: [
      'कुल प्रतिशत पात्रता कटऑफ (एमपी बोर्ड 70%+, सीबीएसई 85%+) को पूरा करता हो।',
      'उत्तीर्ण वर्ष उच्च शिक्षा में सीधे प्रवेश से संबंधित हो।',
      'छात्र एवं माता-पिता का नाम आधार कार्ड से मेल खाता हो।'
    ]
  },
  samagra_id: {
    sampleType: 'id_card',
    issuer_en: 'Samagra Samajik Suraksha Mission (MP Government)',
    issuer_hi: 'समग्र सामाजिक सुरक्षा मिशन, मध्य प्रदेश शासन',
    docNumberPlaceholder: 'Family ID: 81094321 • Member ID: 198452310',
    watermark: 'SAMAGRA e-KYC VERIFIED',
    checkpoints_en: [
      '9-digit Member ID and 8-digit Family ID matching household register.',
      'Aadhaar e-KYC status must be "Completed / पूर्ण".',
      'Linked with bank account for Ladli Behna and MP social aid.'
    ],
    checkpoints_hi: [
      '9 अंकों की सदस्य आईडी और 8 अंकों की परिवार आईडी सही हो।',
      'समग्र पोर्टल पर आधार ई-केवाईसी स्थिति "पूर्ण (Yes)" होनी चाहिए।',
      'लाड़ली बहना और राज्य सहायता के लिए बैंक खाते से लिंक हो।'
    ]
  },
  land_record: {
    sampleType: 'land_record',
    issuer_en: 'State Revenue / Bhulekh Department (Patwari / Tehsildar)',
    issuer_hi: 'राजस्व विभाग / भूलेख (पटवारी / तहसीलदार)',
    docNumberPlaceholder: 'Khasra No: 142/1 • Khatauni: 88',
    watermark: 'BHULEKH REVENUE EXTRACT',
    checkpoints_en: [
      'Cultivable agricultural land title in applicant\'s name.',
      'Landholding up to 2.0 hectares for smallholder farmer PM-KISAN entitlement.',
      'Certified copy or digitally signed extract from state Bhulekh portal.'
    ],
    checkpoints_hi: [
      'आवेदक के नाम पर कृषि योग्य भूमि का स्वामित्व दर्ज हो।',
      'लघु एवं सीमांत किसान श्रेणी (2.0 हेक्टेयर तक) का सत्यापन।',
      'राज्य भूलेख पोर्टल से डिजिटल सत्यापित प्रति अथवा पटवारी प्रमाणित नकल।'
    ]
  },
  job_card_mgnrega: {
    sampleType: 'id_card',
    issuer_en: 'Ministry of Rural Development / Gram Panchayat',
    issuer_hi: 'ग्रामीण विकास मंत्रालय / ग्राम पंचायत कार्यालय',
    docNumberPlaceholder: 'MP-04-002-019/3321',
    watermark: 'MGNREGA JOB CARD',
    checkpoints_en: [
      'Active Job Card number registered in local Gram Panchayat.',
      'Household members registered for unskilled wage labor credit under PMAY-G.'
    ],
    checkpoints_hi: [
      'स्थानीय ग्राम पंचायत में पंजीकृत सक्रिय जॉब कार्ड क्रमांक।',
      'पीएम आवास योजना के तहत अकुशल मजदूरी भुगतान हेतु परिवार के सदस्यों का नाम दर्ज हो।'
    ]
  },
  bpl_ration_card: {
    sampleType: 'id_card',
    issuer_en: 'Department of Food, Civil Supplies and Consumer Protection',
    issuer_hi: 'खाद्य, नागरिक आपूर्ति एवं उपभोक्ता संरक्षण विभाग',
    docNumberPlaceholder: 'RATION NO: 2319084421',
    watermark: 'BPL / ANTYODAYA CARD',
    checkpoints_en: [
      'BPL / Antyodaya category clearly indicated on card cover and database.',
      'Family survey number and listed members match application details.'
    ],
    checkpoints_hi: [
      'कार्ड और डेटाबेस में बीपीएल या अंत्योदय श्रेणी स्पष्ट रूप से दर्ज हो।',
      'परिवार सर्वे क्रमांक और सदस्यों के नाम आवेदन से मेल खाते हों।'
    ]
  },
  ration_card: {
    sampleType: 'id_card',
    issuer_en: 'State Food & Civil Supplies Department (NFSA)',
    issuer_hi: 'खाद्य एवं नागरिक आपूर्ति विभाग (राष्ट्रीय खाद्य सुरक्षा)',
    docNumberPlaceholder: 'NFSA / PHH / 10928421',
    watermark: 'NFSA RATION CARD',
    checkpoints_en: [
      'Priority Household (PHH) or Antyodaya Anna Yojana (AAY) category.',
      'Beneficiary name included in verified family roster.'
    ],
    checkpoints_hi: [
      'प्राथमिकता परिवार (PHH) या अंत्योदय श्रेणी का कार्ड।',
      'पारिवारिक सूची में लाभार्थी का नाम शामिल हो।'
    ]
  },
  admission_fee_receipt: {
    sampleType: 'certificate',
    issuer_en: 'Admitted University / Professional Degree College',
    issuer_hi: 'प्रवेशित विश्वविद्यालय / डिग्री कॉलेज प्रशासन',
    docNumberPlaceholder: 'ALLOTMENT / ADM / 2026 / 552',
    watermark: 'COLLEGE ADMISSION RECEIPT',
    checkpoints_en: [
      'Official admission allotment letter through counseling or direct merit.',
      'Tuition fee structure breakdown on official college letterhead.'
    ],
    checkpoints_hi: [
      'काउंसलिंग या मेरिट के माध्यम से जारी कॉलेज आवंटन पत्र।',
      'कॉलेज लेटरहेड पर शिक्षण शुल्क संरचना का विवरण।'
    ]
  }
};

export default function S6_DocumentChecklistScreen() {
  const { language, t } = useLanguage();
  const { evaluationResults, setCurrentScreen, checklistData, setChecklistData } = useSession();

  const [readyDocs, setReadyDocs] = useState({});
  const [expandedPreview, setExpandedPreview] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  const eligibleIds = (evaluationResults?.eligible || []).map((s) => s.scheme_id);
  const targetSchemeIds = eligibleIds.length > 0 ? eligibleIds : (evaluationResults?.not_sure || []).map((s) => s.scheme_id);

  useEffect(() => {
    if (targetSchemeIds.length > 0) {
      setIsLoading(true);
      fetchDocumentChecklist(targetSchemeIds)
        .then((data) => {
          setChecklistData(data);
        })
        .catch((err) => console.error('Checklist fetch error:', err))
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const toggleReady = (docId) => {
    setReadyDocs((prev) => ({
      ...prev,
      [docId]: !prev[docId],
    }));
  };

  const togglePreview = (docId) => {
    setExpandedPreview((prev) => ({
      ...prev,
      [docId]: !prev[docId],
    }));
  };

  const handlePrint = () => {
    window.print();
  };

  const documents = checklistData?.documents || [];
  const readyCount = Object.values(readyDocs).filter(Boolean).length;
  const progressPercent = documents.length > 0 ? Math.round((readyCount / documents.length) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto w-full space-y-6 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Navigation & Header */}
        <div className="no-print space-y-2">
          <button
            onClick={() => setCurrentScreen('S4')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t('back_to_results')}</span>
          </button>

          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight leading-snug">
                {t('checklist_title')}
              </h2>
              <p className="text-sm text-slate-500 mt-1 leading-relaxed">
                {t('checklist_subtitle')}
              </p>
            </div>
            <AudioSpeaker
              text={
                language === 'hi'
                  ? `आपकी पात्र योजनाओं के लिए कुल ${documents.length} दस्तावेज़ आवश्यक हैं। आप प्रत्येक दस्तावेज़ का नमूना और क्या जांचना है, देख सकते हैं।`
                  : `A total of ${documents.length} documents are required across your eligible schemes. Review sample previews and verification checklists.`
              }
              className="mt-1 flex-shrink-0"
            />
          </div>
        </div>

        {/* Print-Only Header */}
        <div className="hidden print-only border-b-2 border-slate-900 pb-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-extrabold text-slate-900">🏛️ योजनासारथी (YojnaSarthi)</h1>
              <p className="text-xs text-slate-700 font-bold uppercase tracking-wider mt-0.5">
                नागरिक व्यक्तिगत दस्तावेज़ चेकलिस्ट (Personalized Scheme Document Checklist)
              </p>
            </div>
            <div className="text-right text-xs text-slate-500 space-y-0.5">
              <p>
                {language === 'hi' ? 'दिनांक: ' : 'Date: '}
                {new Date().toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en-IN')}
              </p>
              <p>
                {language === 'hi'
                  ? 'आधिकारिक सत्यापन मार्गदर्शिका • सत्यापित नियम'
                  : 'Official Verification Guide • Verified Rules'}
              </p>
            </div>
          </div>
        </div>

        {/* Readiness Tracker Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1.5 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                {t('doc_readiness')}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-teal-50 text-teal-900 border border-teal-200">
                {readyCount} / {documents.length} {language === 'hi' ? 'तैयार' : 'Ready'}
              </span>
            </div>

            {/* Visual progress bar */}
            <div className="w-full max-w-md bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className="bg-teal-600 h-full transition-all duration-300 rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-500">
              {t('doc_readiness_hint')}
            </p>
          </div>

          <button
            onClick={handlePrint}
            className="no-print self-stretch sm:self-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs sm:text-sm shadow-xs transition-colors min-h-[44px]"
          >
            <Printer className="w-4 h-4" />
            <span>{t('print_save_pdf')}</span>
          </button>
        </div>

        {/* Consolidated Documents List */}
        {isLoading ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl space-y-3">
            <div className="w-8 h-8 border-3 border-teal-700 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs font-semibold text-slate-600">
              {language === 'hi' ? 'समेकित चेकलिस्ट तैयार की जा रही है...' : 'Generating de-duplicated document checklist...'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => {
              const isChecked = Boolean(readyDocs[doc.document_id]);
              const docName = language === 'hi' ? doc.name_hi : doc.name_en;
              const purpose = language === 'hi' ? doc.purpose_hi : doc.purpose_en;
              const howToGet = language === 'hi' ? doc.how_to_get_hi : doc.how_to_get_en;
              const sampleConfig = DOCUMENT_SAMPLES_CONFIG[doc.document_id];
              const isPreviewOpen = Boolean(expandedPreview[doc.document_id]);

              return (
                <div
                  key={doc.document_id}
                  className={`bg-white border rounded-2xl p-5 transition-all shadow-xs printable-doc-card space-y-4 ${
                    isChecked
                      ? 'border-emerald-300 bg-emerald-50/15'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <button
                      type="button"
                      onClick={() => toggleReady(doc.document_id)}
                      className="mt-0.5 text-slate-400 hover:text-emerald-700 flex-shrink-0 transition-colors p-1 touch-target"
                      title={isChecked ? 'तैयार है' : 'तैयार नहीं'}
                      aria-label={docName}
                    >
                      {isChecked ? (
                        <CheckSquare className="w-6 h-6 text-emerald-600" />
                      ) : (
                        <Square className="w-6 h-6 text-slate-300" />
                      )}
                    </button>

                    <div className="flex-1 space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <h3 className={`text-base font-bold ${isChecked ? 'text-emerald-950 line-through' : 'text-slate-900'}`}>
                          {docName}
                        </h3>

                        {/* Scheme tag pills */}
                        <div className="flex flex-wrap gap-1">
                          {doc.schemes_required_for?.map((sName, sIdx) => (
                            <span
                              key={sIdx}
                              className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200"
                            >
                              ✓ {sName}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Purpose */}
                      <p className="text-xs text-slate-600 leading-relaxed">
                        <strong className="text-slate-800">
                          {language === 'hi' ? 'उद्देश्य: ' : 'Purpose: '}
                        </strong>
                        {purpose}
                      </p>

                      {/* Procurement Instructions Box */}
                      <div className="bg-slate-50 border border-slate-100 rounded-xl p-3 text-xs text-slate-700 space-y-1.5">
                        <p className="leading-relaxed">
                          <strong className="text-slate-900">
                            {t('where_to_obtain')}:{' '}
                          </strong>
                          {howToGet}
                        </p>

                        <div className="flex flex-wrap items-center gap-4 pt-1 text-xs">
                          {doc.online_url && (
                            <a
                              href={doc.online_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-teal-700 hover:text-teal-900 font-bold inline-flex items-center gap-1 underline"
                            >
                              <span>{t('online_link')}</span>
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}

                          {doc.offline_office && (
                            <span className="text-slate-500 inline-flex items-center gap-1 font-medium">
                              <MapPin className="w-3.5 h-3.5 text-slate-400" />
                              <span>{doc.offline_office}</span>
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Sample Preview Button (Issue #7) */}
                      {sampleConfig && (
                        <div className="pt-1 no-print">
                          <button
                            type="button"
                            onClick={() => togglePreview(doc.document_id)}
                            className="inline-flex items-center gap-1.5 text-xs font-bold text-teal-800 hover:text-teal-950 bg-teal-50 hover:bg-teal-100/70 border border-teal-200 px-3 py-1.5 rounded-lg transition-colors"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>
                              {isPreviewOpen
                                ? (language === 'hi' ? 'नमूना एवं जांच सूची छुपाएं' : 'Hide Sample & Details')
                                : (language === 'hi' ? 'दस्तावेज़ का नमूना एवं जांच सूची देखें' : 'View Sample Preview & Checkpoints')}
                            </span>
                            {isPreviewOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Expandable Document Sample & Verification Checkpoints (Issue #7) */}
                  {sampleConfig && isPreviewOpen && (
                    <div className="mt-3 pt-3 border-t border-slate-200/80 bg-slate-50/70 rounded-xl p-4 space-y-4 animate-fade-in no-print">
                      {/* Clearly labeled illustrative sample card */}
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-700">
                            📄 {language === 'hi' ? 'सांकेतिक दस्तावेज़ नमूना (Sample Preview)' : 'Illustrative Document Sample'}
                          </span>
                          <span className="text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded-full">
                            {t('sample_preview_label')}
                          </span>
                        </div>

                        {/* Visual Mock Card with Genuine Layout */}
                        <div className="bg-white border-2 border-dashed border-slate-300 rounded-xl p-4 shadow-inner space-y-2 relative overflow-hidden">
                          {/* Watermark */}
                          <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none select-none font-extrabold text-2xl text-slate-900 rotate-[-12deg]">
                            {sampleConfig.watermark}
                          </div>

                          <div className="flex items-center justify-between border-b pb-2 border-slate-100">
                            <span className="text-xs font-extrabold text-slate-800">
                              🏛️ {language === 'hi' ? sampleConfig.issuer_hi : sampleConfig.issuer_en}
                            </span>
                            <span className="text-[10px] font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                              {sampleConfig.docNumberPlaceholder}
                            </span>
                          </div>

                          <div className="flex items-center gap-3 pt-1">
                            <div className="w-12 h-14 rounded bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 text-xs">
                              [Photo]
                            </div>
                            <div className="space-y-1 text-xs text-slate-600 flex-1">
                              <p className="font-bold text-slate-900">{docName}</p>
                              <p className="text-[11px] text-slate-500">
                                {language === 'hi' ? 'सत्यापित नागरिक पहचान / राजस्व प्रपत्र' : 'Verified Citizen Revenue / Identity Record'}
                              </p>
                              <div className="h-1.5 bg-slate-200 rounded-full w-3/4" />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* What Details to Check (Checkpoints list) */}
                      <div className="space-y-1.5">
                        <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-teal-700" />
                          <span>{t('what_to_check')}</span>
                        </h4>
                        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-700">
                          {(language === 'hi' ? sampleConfig.checkpoints_hi : sampleConfig.checkpoints_en).map((cp, cIdx) => (
                            <li key={cIdx} className="bg-white border border-slate-200 rounded-lg p-2.5 flex items-start gap-2 shadow-2xs">
                              <span className="text-teal-700 font-bold flex-shrink-0">✓</span>
                              <span className="leading-snug">{cp}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Navigation Action Bar */}
      <div className="no-print pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={handlePrint}
          className="w-full sm:w-auto px-6 py-3 bg-blue-700 hover:bg-blue-800 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all inline-flex items-center justify-center gap-2 min-h-[48px]"
        >
          <Printer className="w-4 h-4" />
          <span>{t('print_save_pdf')}</span>
        </button>

        <button
          onClick={() => setCurrentScreen('S4')}
          className="w-full sm:w-auto px-6 py-3 border border-slate-300 text-slate-700 hover:bg-slate-100 font-semibold rounded-xl text-sm transition-colors min-h-[48px]"
        >
          {t('back_to_results')}
        </button>
      </div>
    </div>
  );
}
