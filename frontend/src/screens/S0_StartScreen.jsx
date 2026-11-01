import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchRulesStatus } from '../services/api';
import {
  ClipboardList,
  Mic,
  FileText,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  FileCheck2,
  ChevronLeft,
  ChevronRight,
  Search,
  ExternalLink,
  Shield,
  HelpCircle,
  Award
} from 'lucide-react';

import heroFarmer from '../assets/hero-farmer.jpg';
import heroWidow from '../assets/hero-widow.jpg';
import heroStudents from '../assets/hero-students.jpg';
import schemeLogos from '../assets/scheme-logos.jpg';

export default function S0_StartScreen() {
  const { language, t, lt } = useLanguage();
  const { setCurrentScreen, setProfile, openDocumentGuide } = useSession();
  const [rulesStatus, setRulesStatus] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Hero Slider: 3-Second Cycle across the 4 hero assets
  const slides = [
    {
      id: 0,
      img: heroFarmer,
      tag: lt('Agriculture & Rural Welfare', 'कृषि एवं ग्रामीण कल्याण', 'कृषी आणि ग्रामीण कल्याण', 'কৃষি ও গ্রামীণ কল্যাণ'),
      title: lt('PM-Kisan & Rural Housing Support', 'पीएम-किसान एवं ग्रामीण आवास सहायता', 'पीएम-किसान आणि ग्रामीण घरकुल योजना', 'পিএম-কিষাণ ও গ্রামীণ আবাসন সহায়তা'),
      subtitle: lt(
        'Direct financial assistance & permanent shelter for eligible agricultural families.',
        'पात्र कृषक परिवारों के लिए प्रत्यक्ष वित्तीय सहायता एवं पक्का आवास।',
        'पात्र शेतकरी कुटुंबांसाठी थेट आर्थिक सहाय्य आणि पक्के घर.',
        'যোগ্য কৃষক পরিবারের জন্য প্রত্যক্ষ আর্থিক সহায়তা ও স্থায়ী বাসস্থান।'
      ),
    },
    {
      id: 1,
      img: heroWidow,
      tag: lt('Women Empowerment & Social Security', 'महिला सशक्तिकरण एवं सामाजिक सुरक्षा', 'महिला सक्षमीकरण आणि सामाजिक सुरक्षा', 'নারী ক্ষমতায়ন ও সামাজিক সুরক্ষা'),
      title: lt('Ladli Behna & Widow Pension Entitlements', 'लाड़ली बहना एवं विधवा पेंशन अधिकार', 'लाडकी बहीण आणि विधवा पेन्शन अधिकार', 'লাডলি বহনা ও বিধবা পেনশন সুবিধা'),
      subtitle: lt(
        'Monthly direct benefit transfers & dignity support for women across the state.',
        'माहवारी प्रत्यक्ष आर्थिक सहयोग एवं सामाजिक सुरक्षा पेंशन।',
        'राज्यातील महिलांसाठी मासिक थेट लाभ हस्तांतरण आणि सन्मान निधी.',
        'রাজ্যের নারীদের জন্য মাসিক প্রত্যক্ষ সুবিধা হস্তান্তর ও আর্থিক সহায়তা।'
      ),
    },
    {
      id: 2,
      img: heroStudents,
      tag: lt('Higher Education & Student Merits', 'उच्च शिक्षा एवं मेधावी विद्यार्थी', 'उच्च शिक्षण आणि मेधावी विद्यार्थी', 'উচ্চশিক্ষা ও মেধাবী শিক্ষার্থী'),
      title: lt('MMVY Full Tuition Fee Scholarships', 'मेधावी विद्यार्थी 100% शिक्षण शुल्क छात्रवृत्ति', 'मेधावी विद्यार्थी १००% शैक्षणिक शुल्क शिष्यवृत्ती', 'মেধাবী শিক্ষার্থী ১০০% টিউশন ফি স্কলারশিপ'),
      subtitle: lt(
        '100% course fee coverage for higher education in Engineering, Medical & Degree colleges.',
        'इंजीनियरिंग, मेडिकल व उच्च शिक्षा के लिए शत-प्रतिशत शुल्क प्रतिपूर्ति।',
        'अभियांत्रिकी, वैद्यकीय आणि पदवी महाविद्यालयांमधील उच्च शिक्षणासाठी १००% फी माफी.',
        'ইঞ্জিনিয়ারিং, মেডিকেল ও ডিগ্রি কলেজে উচ্চশিক্ষার জন্য ১০০% কোর্স ফি মকুব।'
      ),
    },
    {
      id: 3,
      img: schemeLogos,
      tag: lt('Flagship Government Schemes', 'प्रमुख राष्ट्रीय एवं राज्य योजनाएं', 'प्रमुख राष्ट्रीय आणि राज्य योजना', 'প্রধান জাতীয় ও রাজ্য প্রকল্প'),
      title: lt('Unified Transparent Eligibility Gateway', 'एकीकृत पारदर्शी सरकारी पात्रता मंच', 'एकीकृत पारदर्शक सरकारी पात्रता व्यासपीठ', 'একীভূত স্বচ্ছ সরকারি যোগ্যতা পোর্টাল'),
      subtitle: lt(
        'Discover every welfare scheme you qualify for using 100% deterministic official rules.',
        '100% आधिकारिक नियमों के साथ अपनी सभी पात्र योजनाओं की जांच करें।',
        '१००% अधिकृत शासकीय नियमांचा वापर करून पात्र असलेल्या प्रत्येक योजनेची माहिती मिळवा.',
        '১০০% সুনির্দিষ্ট সরকারি নিয়মের ভিত্তিতে আপনার যোগ্য প্রতিটি প্রকল্প খুঁজুন।'
      ),
    },
  ];

  const [currentSlide, setCurrentSlide] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // Exact 3-Second (3000ms) interval as requested by user
  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [slides.length, isPaused]);

  useEffect(() => {
    fetchRulesStatus()
      .then((data) => setRulesStatus(data))
      .catch((err) => console.warn('Rules status error:', err));
  }, []);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const q = searchQuery.toLowerCase().trim();
    if (!q) {
      setCurrentScreen('S1');
      return;
    }
    if (q.includes('kisan') || q.includes('farmer') || q.includes('kheti') || q.includes('कृषि')) {
      handleDemoPersona('farmer');
    } else if (q.includes('widow') || q.includes('vidhwa') || q.includes('behna') || q.includes('महिला') || q.includes('pension')) {
      handleDemoPersona('widow');
    } else if (q.includes('student') || q.includes('scholarship') || q.includes('mmvy') || q.includes('छात्र')) {
      handleDemoPersona('student');
    } else {
      setCurrentScreen('S1');
    }
  };

  const handleDemoPersona = (personaType) => {
    if (personaType === 'farmer') {
      setProfile({
        age: 48,
        gender: 'male',
        marital_status: 'married',
        state: 'Madhya Pradesh',
        residence_type: 'rural',
        occupation: 'farmer',
        landholding_hectares: 1.5,
        annual_income: 65000,
        is_institutional_landholder: false,
        holds_constitutional_post: false,
        has_pucca_house: false,
        bpl_card_holder: true,
        confirmed_fields: [
          'age',
          'gender',
          'marital_status',
          'state',
          'residence_type',
          'occupation',
          'landholding_hectares',
          'annual_income',
          'is_institutional_landholder',
          'holds_constitutional_post',
          'has_pucca_house',
          'bpl_card_holder',
        ],
      });
      setCurrentScreen('S3');
    } else if (personaType === 'widow') {
      setProfile({
        age: 52,
        gender: 'female',
        marital_status: 'widow',
        state: 'Madhya Pradesh',
        residence_type: 'rural',
        occupation: 'homemaker',
        annual_income: 24000,
        bpl_card_holder: true,
        holds_constitutional_post: false,
        landholding_hectares: 0.0,
        confirmed_fields: [
          'age',
          'gender',
          'marital_status',
          'state',
          'residence_type',
          'occupation',
          'annual_income',
          'bpl_card_holder',
          'holds_constitutional_post',
        ],
      });
      setCurrentScreen('S3');
    } else if (personaType === 'student') {
      setProfile({
        age: 19,
        gender: 'female',
        marital_status: 'single',
        state: 'Madhya Pradesh',
        residence_type: 'urban',
        occupation: 'student',
        student_class12_marks_percent: 86.0,
        enrolled_higher_education: true,
        annual_income: 450000,
        holds_constitutional_post: false,
        confirmed_fields: [
          'age',
          'gender',
          'marital_status',
          'state',
          'occupation',
          'student_class12_marks_percent',
          'enrolled_higher_education',
          'annual_income',
          'holds_constitutional_post',
        ],
      });
      setCurrentScreen('S3');
    }
  };

  return (
    <div className="w-full flex flex-col items-center select-none bg-slate-50 animate-fade-in">
      {/* 1. FULL-WIDTH GRAND HERO BANNER (Covering Whole Screen Width like india.gov.in & myscheme.gov.in) */}
      <section
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
        className="w-full relative min-h-[520px] sm:min-h-[620px] flex flex-col justify-between overflow-hidden bg-[#060e1d]"
      >
        {/* Full-bleed Background Images with 3s Smooth Crossfade & Enhanced Contrast */}
        <div className="absolute inset-0 z-0">
          {slides.map((s, idx) => (
            <img
              key={s.id}
              src={s.img}
              alt={s.tag}
              className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ease-in-out contrast-[1.08] saturate-[1.05] brightness-[0.92] ${
                idx === currentSlide ? 'opacity-100 scale-100' : 'opacity-0 scale-105 pointer-events-none'
              }`}
            />
          ))}
          {/* Subtle directional gradient: dark on left for text readability, clear & vibrant on right for the photo */}
          <div className="absolute inset-0 bg-gradient-to-r from-slate-950/80 via-slate-950/40 to-black/20" />
        </div>

        {/* Previous / Next Arrow Controls (Inspired by myscheme.gov.in) */}
        <button
          onClick={prevSlide}
          className="absolute left-3 sm:left-6 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-black/40 hover:bg-black/75 border border-white/20 text-white flex items-center justify-center backdrop-blur-md transition-all hover:scale-110 shadow-lg cursor-pointer"
          aria-label="Previous slide"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button
          onClick={nextSlide}
          className="absolute right-3 sm:right-6 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-black/40 hover:bg-black/75 border border-white/20 text-white flex items-center justify-center backdrop-blur-md transition-all hover:scale-110 shadow-lg cursor-pointer"
          aria-label="Next slide"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Hero Top & Middle Content (Centered & Spacious, crisp text without heavy shadows) */}
        <div className="relative z-10 w-full max-w-5xl mx-auto px-6 sm:px-12 pt-12 sm:pt-16 pb-8 flex flex-col items-center text-center space-y-6">
          {/* National Portal Ashoka Emblem & Convergence Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-slate-900/80 border border-amber-400/30 text-amber-300 text-xs font-bold tracking-widest uppercase backdrop-blur-md animate-fade-in">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
            <span>
              {lt(
                'YOUR GUIDE TO GOVERNMENT WELFARE • DIRECT BENEFIT PLATFORM',
                'सरकारी कल्याण योजनाओं की मार्गदर्शिका • प्रत्यक्ष लाभ मंच'
              )}
            </span>
          </div>

          {/* Majestic Hero Title (Clean, crisp typography without text shadow) */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight max-w-4xl">
            {lt('Discover Government Schemes You May Be Eligible For', 'सरकारी योजनाओं में अपने अधिकार और पात्रता जानें')}
          </h1>

          {/* Subtitle */}
          <p className="text-sm sm:text-lg text-slate-200 font-normal max-w-2xl leading-relaxed">
            {lt(
              'Find the benefits you deserve. Understand your eligibility, required documents, and application process — all in one place.',
              'अपने अधिकार और लाभ खोजें। अपनी पात्रता, आवश्यक दस्तावेज़ और आवेदन प्रक्रिया को एक ही स्थान पर समझें।'
            )}
          </p>

          {/* Central Instant Search Bar (Inspired by india.gov.in & myscheme.gov.in) */}
          <form
            onSubmit={handleSearchSubmit}
            className="w-full max-w-3xl mt-4 bg-white/95 backdrop-blur-md rounded-2xl p-2 shadow-md border border-white/30 flex flex-col sm:flex-row items-center gap-2 transition-all hover:border-amber-400"
          >
            <div className="flex items-center gap-2.5 flex-1 px-3 w-full">
              <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={lt(
                  'Search schemes, keywords, or entitlements (e.g. Kisan, Ladli Behna, Awas, Scholarship)...',
                  'योजना, कीवर्ड या लाभ खोजें (उदा. किसान, लाड़ली बहना, आवास, छात्रवृत्ति)...'
                )}
                className="w-full bg-transparent text-sm text-slate-800 placeholder-slate-400 font-medium focus:outline-hidden py-2"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-3 py-2.5 border border-slate-200 focus:outline-hidden cursor-pointer"
              >
                <option value="all">{lt('All Categories', 'सभी श्रेणियां')}</option>
                <option value="agriculture">{lt('Agriculture', 'कृषि कल्याण')}</option>
                <option value="women">{lt('Women & Child', 'महिला एवं बाल')}</option>
                <option value="students">{lt('Higher Education', 'उच्च शिक्षा')}</option>
                <option value="housing">{lt('Housing & Health', 'आवास व स्वास्थ्य')}</option>
              </select>

              <button
                type="submit"
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs sm:text-sm shadow-md transition-all cursor-pointer whitespace-nowrap"
              >
                {lt('Search Schemes', 'योजनाएं खोजें')}
              </button>
            </div>
          </form>

          {/* Trending Searches Tags (Inspired by india.gov.in) */}
          <div className="flex items-center justify-center gap-2 flex-wrap text-xs text-slate-300 pt-1">
            <span className="font-semibold text-amber-300 text-[11px] uppercase tracking-wider">
              {lt('Trending:', 'लोकप्रिय खोजें:')}
            </span>
            <button
              onClick={() => handleDemoPersona('farmer')}
              className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-slate-200 transition cursor-pointer"
            >
              🌾 PM-Kisan
            </button>
            <button
              onClick={() => handleDemoPersona('widow')}
              className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-slate-200 transition cursor-pointer"
            >
              👩 Ladli Behna
            </button>
            <button
              onClick={() => handleDemoPersona('student')}
              className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-slate-200 transition cursor-pointer"
            >
              🎓 MMVY Scholarship
            </button>
            <button
              onClick={() => handleDemoPersona('farmer')}
              className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-slate-200 transition cursor-pointer"
            >
              🏠 PMAY-G Housing
            </button>
            <button
              onClick={() => setCurrentScreen('S1')}
              className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-slate-200 transition cursor-pointer"
            >
              🏥 Ayushman Bharat
            </button>
          </div>
        </div>

        {/* Hero Bottom: Slider Dots & DPI Impact Quote Banner (Inspired by india.gov.in) */}
        <div className="relative z-10 w-full max-w-5xl mx-auto px-6 sm:px-12 pb-6 space-y-4">
          {/* Active 3s Indicator Dots */}
          <div className="flex items-center justify-center gap-2">
            {slides.map((s, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentSlide(idx)}
                className={`h-2 transition-all duration-500 rounded-full cursor-pointer ${
                  idx === currentSlide
                    ? 'w-8 bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.8)]'
                    : 'w-2.5 bg-white/35 hover:bg-white/70'
                }`}
                aria-label={`Go to slide ${idx + 1}`}
              />
            ))}
          </div>

          {/* India Digital Public Infrastructure Quote Strip */}
          <div className="rounded-xl bg-black/40 border border-white/15 backdrop-blur-md p-3 sm:p-3.5 text-center text-xs text-slate-300 font-medium">
            <p className="line-clamp-2">
              <span className="text-amber-300 font-bold mr-1.5">“</span>
              {lt(
                "India's Digital Public Infrastructure demonstrates how technology can expand opportunity, improve governance, and deliver direct benefit transfers with zero leakage.",
                'भारत का डिजिटल पब्लिक इन्फ्रास्ट्रक्चर दिखाता है कि कैसे तकनीक अवसरों का विस्तार कर सकती है और बिना किसी बिचौलिए के सीधे नागरिकों तक लाभ पहुंचा सकती है।'
              )}
              <span className="text-amber-300 font-bold ml-1.5">”</span>
            </p>
          </div>
        </div>
      </section>

      {/* 2. MAIN SPACIOUS BODY CONTAINER (Clean, Impressive, Easy to Understand) */}
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-8 py-12 sm:py-16 space-y-16">
        {/* FAST & ACCESSIBLE ELIGIBILITY: TWO SIMPLE WAYS TO FIND YOUR BENEFITS */}
        <section className="space-y-8">
          <div className="text-center space-y-3">
            <div className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-blue-50 text-blue-700 text-xs font-bold tracking-widest uppercase border border-blue-100 shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>{lt('FAST & ACCESSIBLE ELIGIBILITY', 'त्वरित एवं सुलभ पात्रता जांच')}</span>
            </div>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
              {lt('Two Simple Ways to Find Your Benefits', 'अपने लाभ खोजने के दो आसान तरीके')}
            </h2>
            <p className="text-sm sm:text-base text-slate-600 font-medium max-w-xl mx-auto leading-relaxed">
              {lt(
                "Choose how you'd like to discover schemes tailored to you and your family.",
                'चुनें कि आप अपने और अपने परिवार के लिए योजनाएं कैसे खोजना चाहते हैं।'
              )}
            </p>
          </div>

          {/* Dual Action Cards (Grand, Luxurious & Clean) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Card 1: Answer a Few Questions */}
            <div className="bg-white rounded-3xl border border-slate-200/90 p-8 sm:p-10 shadow-sm hover:shadow-xl hover:border-blue-300 transition-all duration-300 flex flex-col justify-between space-y-8 group">
              <div className="space-y-5">
                <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100 shadow-xs group-hover:scale-105 transition-transform">
                  <ClipboardList className="w-8 h-8" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-2xl font-black text-slate-900 group-hover:text-blue-700 transition-colors">
                    {lt('Answer a Few Questions', 'कुछ सरल प्रश्नों के उत्तर दें')}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed font-normal">
                    {lt(
                      'Answer simple questions about yourself to discover government schemes you may be eligible for. Every question includes context on why it is asked.',
                      'अपनी जानकारी के आधार पर 4 से 8 सीधे प्रश्नों के उत्तर दें और सटीक सरकारी योजनाओं का पता लगाएं। प्रत्येक प्रश्न के साथ कारण और उदाहरण समझाए गए हैं।'
                    )}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2.5 text-xs font-semibold pt-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-50 text-blue-800 border border-blue-100">
                    ⏱ {lt('Estimated time: 2 mins', 'अनुमानित समय: 2 मिनट')}
                  </span>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 border border-slate-200">
                    🚫 {lt('No registration required', 'कोई पंजीकरण आवश्यक नहीं')}
                  </span>
                </div>
              </div>

              <div>
                <button
                  onClick={() => setCurrentScreen('S1')}
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-[#2563EB] hover:bg-blue-700 text-white text-sm sm:text-base font-bold flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all cursor-pointer group-hover:translate-x-1"
                >
                  <span>{lt('Check Eligibility →', 'पात्रता जांचें →')}</span>
                </button>
              </div>
            </div>

            {/* Card 2: Tell Us About Yourself (Two-Way Voice AI) */}
            <div className="bg-white rounded-3xl border border-slate-200/90 p-8 sm:p-10 shadow-sm hover:shadow-xl hover:border-purple-300 transition-all duration-300 flex flex-col justify-between space-y-8 group">
              <div className="space-y-5">
                <div className="w-16 h-16 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center border border-purple-100 shadow-xs group-hover:scale-105 transition-transform">
                  <Mic className="w-8 h-8" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-2xl font-black text-slate-900 group-hover:text-purple-700 transition-colors">
                    {lt('Tell Us About Yourself', 'अपने बारे में बताएं (Voice & Text)')}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed font-normal">
                    {lt(
                      'Describe your situation naturally using your voice or text. Our two-way voice assistant listens and speaks back to confirm your eligibility details.',
                      'अपनी भाषा (हिन्दी, हिंग्लिश या अंग्रेजी) में बोलकर या लिखकर बताएं। हमारा दो-तरफ़ा आवाज़ सहायक आपसे बातचीत करेगा और सभी विवरण निकाल लेगा।'
                    )}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2.5 text-xs font-semibold pt-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-800 border border-indigo-100">
                    🌐 {lt('English Hindi both available', 'अंग्रेजी और हिन्दी दोनों उपलब्ध')}
                  </span>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-50 text-purple-800 border border-purple-100">
                    🎙️ {lt('Voice & text input', 'आवाज़ और टेक्स्ट इनपुट')}
                  </span>
                </div>
              </div>

              <div>
                <button
                  onClick={() => setCurrentScreen('S2')}
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-[#2563EB] hover:bg-blue-700 text-white text-sm sm:text-base font-bold flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all cursor-pointer group-hover:translate-x-1"
                >
                  <span>{lt('Get Started →', 'शुरू करें →')}</span>
                </button>
              </div>
            </div>
          </div>

          {/* 3. Golden Document Guide Feature Card */}
          <div className="pt-4 flex flex-col items-center">
            <button
              onClick={openDocumentGuide}
              className="w-full max-w-3xl py-4 px-8 rounded-2xl bg-[#FCD34D] hover:bg-[#FBBF24] text-slate-950 font-black text-base sm:text-lg border-2 border-amber-400 shadow-md hover:shadow-xl transition-all flex items-center justify-center gap-3 cursor-pointer transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <FileCheck2 className="w-5 h-5 text-slate-900" />
              <span>{lt('Document Guide & Sample Previews', 'दस्तावेज़ मार्गदर्शिका एवं सांकेतिक नमूने')}</span>
              <ArrowRight className="w-5 h-5 text-slate-900" />
            </button>
            <p className="text-xs text-slate-500 mt-2 font-medium">
              {lt(
                'View required certificates (Income, Domicile, Caste, Land), issuing authorities, and direct links to official application portals.',
                'आय, मूल निवास, जाति, खसरा-खतौनी आदि के जारीकर्ता, आवश्यक विवरण एवं आधिकारिक सरकारी आवेदन पोर्टल लिंक देखें।'
              )}
            </p>
          </div>
        </section>

        {/* 4. MENTOR & JUDGE INSTANT EVALUATION SHORTCUTS */}
        <section className="bg-white rounded-3xl border border-slate-200/90 p-8 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div className="space-y-1">
              <h3 className="text-base font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <span>{lt('Mentor & Judge Instant Test Personas', 'मेंटर एवं निर्णायक त्वरित परीक्षण (Demo Personas)')}</span>
              </h3>
              <p className="text-xs sm:text-sm text-slate-500">
                {lt(
                  'Click any profile below to instantly evaluate and verify 100% deterministic rules without manual typing:',
                  'हैकथॉन मूल्यांकन हेतु एक क्लिक में तीनों प्रमुख प्रोफाइल का सटीक परीक्षण करें:'
                )}
              </p>
            </div>
            {rulesStatus && (
              <div className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl flex items-center gap-1.5 self-start sm:self-auto font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>{rulesStatus.verified_schemes} Verified Schemes Active</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            {/* Persona 1: Farmer */}
            <button
              onClick={() => handleDemoPersona('farmer')}
              className="p-5 rounded-2xl border-2 border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/20 text-left transition-all hover:shadow-md group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-3xl">🌾</span>
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100/70 px-2.5 py-0.5 rounded-full border border-emerald-300">
                  {lt('Farmer', 'किसान')}
                </span>
              </div>
              <h4 className="font-extrabold text-slate-900 text-base group-hover:text-emerald-800 transition-colors">
                {lt('Rural Farmer (Sehore)', 'ग्रामीण किसान (सीहोर)')}
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                48y, 1.5 ha land, MP resident, kutcha house
              </p>
              <div className="mt-3 text-xs font-bold text-emerald-700 flex items-center gap-1">
                <span>{lt('Eligible: PM-Kisan, PMAY-G', 'पात्र: PM-Kisan, PMAY-G')}</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>

            {/* Persona 2: Widow */}
            <button
              onClick={() => handleDemoPersona('widow')}
              className="p-5 rounded-2xl border-2 border-slate-200 hover:border-rose-400 hover:bg-rose-50/20 text-left transition-all hover:shadow-md group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-3xl">👩</span>
                <span className="text-[11px] font-bold uppercase tracking-wider text-rose-800 bg-rose-100/70 px-2.5 py-0.5 rounded-full border border-rose-300">
                  {lt('Widow', 'विधवा महिला')}
                </span>
              </div>
              <h4 className="font-extrabold text-slate-900 text-base group-hover:text-rose-800 transition-colors">
                {lt('Widowed Woman', 'विधवा महिला')}
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                52y, BPL ration card, ₹24,000 annual income
              </p>
              <div className="mt-3 text-xs font-bold text-rose-700 flex items-center gap-1">
                <span>{lt('Eligible: IGNWPS, Ladli Behna', 'पात्र: IGNWPS, लाड़ली बहना')}</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>

            {/* Persona 3: Student */}
            <button
              onClick={() => handleDemoPersona('student')}
              className="p-5 rounded-2xl border-2 border-slate-200 hover:border-blue-500 hover:bg-blue-50/20 text-left transition-all hover:shadow-md group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-3xl">🎓</span>
                <span className="text-[11px] font-bold uppercase tracking-wider text-blue-800 bg-blue-100/70 px-2.5 py-0.5 rounded-full border border-blue-300">
                  {lt('Student', 'विद्यार्थी')}
                </span>
              </div>
              <h4 className="font-extrabold text-slate-900 text-base group-hover:text-blue-800 transition-colors">
                {lt('College Student', 'कॉलेज विद्यार्थी')}
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                19y, 86% in 12th board exams, MP resident
              </p>
              <div className="mt-3 text-xs font-bold text-blue-700 flex items-center gap-1">
                <span>{lt('Eligible: MMVY Scholarship', 'पात्र: MMVY छात्रवृत्ति')}</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          </div>
        </section>

        {/* 5. NATIONAL CIVIC TRUST PILLARS */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 text-center space-y-2 shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h5 className="font-extrabold text-sm text-slate-900">
              {lt('Deterministic Rules', 'सत्यापित नियम')}
            </h5>
            <p className="text-xs text-slate-500 leading-snug">
              {lt('100% verified official policy rules without AI hallucination.', 'बिना किसी भ्रम के शत-प्रतिशत आधिकारिक सरकारी नियम।')}
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 text-center space-y-2 shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
              <Shield className="w-5 h-5" />
            </div>
            <h5 className="font-extrabold text-sm text-slate-900">
              {lt('Zero Data Retention', 'शून्य डेटा संचयन')}
            </h5>
            <p className="text-xs text-slate-500 leading-snug">
              {lt('No citizen Aadhaar or personal profile is ever stored.', 'नागरिक का कोई भी आधार या डेटा सहेजा नहीं जाता।')}
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 text-center space-y-2 shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mx-auto">
              <Award className="w-5 h-5" />
            </div>
            <h5 className="font-extrabold text-sm text-slate-900">
              {lt('Multilingual Accessibility', 'बहुभाषी पहुंच')}
            </h5>
            <p className="text-xs text-slate-500 leading-snug">
              {lt('Seamless voice & text in Hindi, English, Marathi, and Bengali.', 'हिन्दी, अंग्रेजी, मराठी एवं बांग्ला में सहज संवाद।')}
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 text-center space-y-2 shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto">
              <ExternalLink className="w-5 h-5" />
            </div>
            <h5 className="font-extrabold text-sm text-slate-900">
              {lt('Direct Portal Links', 'सीधे आधिकारिक पोर्टल')}
            </h5>
            <p className="text-xs text-slate-500 leading-snug">
              {lt('One-click redirection to official government application portals.', 'सीधे अधिकृत सरकारी पोर्टल (MP e-District आदि) पर आवेदन।')}
            </p>
          </div>
        </section>
      </div>

      {/* 6. FULL-WIDTH CIVIC FOOTER (Covering Whole Screen Width like india.gov.in & myscheme.gov.in) */}
      <footer className="w-full bg-[#081225] text-slate-300 py-16 px-6 sm:px-12 lg:px-20 border-t border-slate-800 shadow-2xl">
        <div className="w-full max-w-7xl mx-auto space-y-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 pb-10 border-b border-slate-800/80">
            {/* Column 1: Brand & Civic Mandate */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-md border border-blue-400/30">
                  🏛️
                </div>
                <div>
                  <span className="font-black text-white text-xl tracking-tight block">YojnaSarthi</span>
                  <span className="text-[11px] text-slate-400 font-medium">National Citizen Welfare Platform</span>
                </div>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
                {lt(
                  'Official Citizen Welfare Discovery and Direct Benefit Facilitation Portal. Delivering transparent governance and socio-economic support schemes nationwide.',
                  'आधिकारिक नागरिक कल्याण एवं प्रत्यक्ष लाभ सुविधा पोर्टल। देश भर में पारदर्शी सुशासन और सामाजिक-आर्थिक योजनाओं की सुगम पहुंच।'
                )}
              </p>
            </div>

            {/* Column 2: Citizen Services */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400">
                {lt('CITIZEN SERVICES', 'नागरिक सेवाएं')}
              </h4>
              <ul className="space-y-2.5 text-xs text-slate-300 font-medium">
                <li>
                  <button
                    onClick={() => setCurrentScreen('S1')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    {lt('All Welfare Schemes', 'सभी कल्याणकारी योजनाएं')}
                  </button>
                </li>
                <li>
                  <button
                    onClick={openDocumentGuide}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    {lt('Document Checklist & Procurement Guide', 'दस्तावेज़ चेकलिस्ट एवं आवेदन गाइड')}
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => setCurrentScreen('S7')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    {lt('Application Tracking & Forms Help', 'आवेदन स्थिति व फॉर्म सहायता')}
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => setCurrentScreen('S1')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    {lt('Check Eligibility', 'पात्रता जांच')}
                  </button>
                </li>
              </ul>
            </div>

            {/* Column 3: Assistance & Helpdesk */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400">
                {lt('ASSISTANCE & HELPDESK', 'सहायता एवं हेल्पलाइन')}
              </h4>
              <div className="space-y-2 text-xs text-slate-300 font-medium">
                <p className="flex items-center gap-2">
                  <span className="text-slate-400">Toll-Free:</span>
                  <span className="font-bold text-white text-sm">1800-11-2024</span>
                </p>
                <p className="flex items-center gap-2">
                  <span className="text-slate-400">Email:</span>
                  <span className="text-cyan-400 font-mono">helpdesk@yojnasarthi.gov.in</span>
                </p>
                <p className="text-slate-400 pt-1">
                  {lt('Grievance Redressal: 24x7 Digital Public Portal', 'शिकायत निवारण: 24x7 डिजिटल सहायता')}
                </p>
              </div>
            </div>
          </div>

          {/* Bottom Bar: Copyright & Legal */}
          <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
            <p>© 2025 Ministry of Citizen Welfare & Empowerment. All Rights Reserved.</p>
            <div className="flex items-center gap-4 text-slate-400 font-medium">
              <span className="hover:text-white cursor-pointer">{lt('Privacy Policy', 'गोपनीयता नीति')}</span>
              <span>•</span>
              <span className="hover:text-white cursor-pointer">{lt('Terms of Service', 'सेवा की शर्तें')}</span>
              <span>•</span>
              <span className="hover:text-white cursor-pointer">{lt('Accessibility Statement', 'सुलभता विवरण')}</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
