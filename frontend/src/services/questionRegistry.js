// ==============================================================================
// Citizen Profile Question Registry for Verification and Dynamic Queries
// Complete bilingual (Hindi, English, Bengali) field metadata and question options
// ==============================================================================

export const QUESTION_METADATA = {
  state: {
    title_en: "Which state do you reside in?",
    title_hi: "आप किस राज्य के निवासी हैं?",
    title_bn: "আপনি কোন রাজ্যের বাসিন্দা?",
    subtitle_en: "Government welfare schemes are often state-specific.",
    subtitle_hi: "कई सरकारी योजनाएं राज्य-विशिष्ट होती हैं।",
    subtitle_bn: "সরকারি কল্যাণমূলক প্রকল্পগুলি প্রায়শই নির্দিষ্ট রাজ্যের জন্য হয়।",
    type: "single_choice",
    options: [
      { label_en: "Madhya Pradesh", label_hi: "मध्य प्रदेश", label_bn: "মধ্যপ্রদেশ", value: "Madhya Pradesh" },
      { label_en: "Maharashtra", label_hi: "महाराष्ट्र", label_bn: "মহারাষ্ট্র", value: "Maharashtra" },
      { label_en: "Uttar Pradesh", label_hi: "उत्तर प्रदेश", label_bn: "উত্তর প্রদেশ", value: "Uttar Pradesh" },
      { label_en: "Rajasthan", label_hi: "राजस्थान", label_bn: "রাজস্থান", value: "Rajasthan" },
      { label_en: "Bihar", label_hi: "बिहार", label_bn: "বিহার", value: "Bihar" },
      { label_en: "Other State / UT", label_hi: "अन्य राज्य / केंद्र शासित प्रदेश", label_bn: "অন্যান্য রাজ্য", value: "Other" }
    ]
  },
  residence_type: {
    title_en: "What is your residence area type?",
    title_hi: "आपका निवास क्षेत्र किस प्रकार का है?",
    title_bn: "আপনার বসবাসের এলাকা কোন ধরনের?",
    subtitle_en: "Identifies eligibility for rural vs urban development schemes.",
    subtitle_hi: "ग्रामीण एवं शहरी विकास योजनाओं की पात्रता तय करता है।",
    subtitle_bn: "গ্রামীণ বনাম শহুরে উন্নয়ন প্রকল্পের যোগ্যতা নির্ধারণ করে।",
    type: "single_choice",
    options: [
      { label_en: "Rural (Village / Gram Panchayat)", label_hi: "ग्रामीण (गांव / ग्राम पंचायत)", label_bn: "গ্রামীণ (গ্রাম / গ্রাম পঞ্চায়েত)", value: "rural" },
      { label_en: "Urban (City / Municipality)", label_hi: "शहरी (शहर / नगर पालिका)", label_bn: "শহুরে (শহর / পৌরসভা)", value: "urban" }
    ]
  },
  gender: {
    title_en: "What is your gender?",
    title_hi: "आपका लिंग क्या है?",
    title_bn: "আপনার লিঙ্গ কি?",
    subtitle_en: "Certain schemes offer dedicated assistance for women or transgender citizens.",
    subtitle_hi: "कुछ योजनाएं महिलाओं या ट्रांसजेंडर नागरिकों के लिए विशेष सहायता प्रदान करती हैं।",
    subtitle_bn: "কিছু প্রকল্প নারী বা রূপান্তরিত লিঙ্গের জন্য নির্দিষ্ট সহায়তা দেয়।",
    type: "single_choice",
    options: [
      { label_en: "Female", label_hi: "महिला (Female)", label_bn: "মহিলা", value: "female" },
      { label_en: "Male", label_hi: "पुरुष (Male)", label_bn: "পুরুষ", value: "male" },
      { label_en: "Transgender / Other", label_hi: "ट्रांसजेंडर / अन्य", label_bn: "রূপান্তরিত লিঙ্গ", value: "transgender" }
    ]
  },
  age: {
    title_en: "What is your age in completed years?",
    title_hi: "आपकी आयु कितने वर्ष है?",
    title_bn: "আপনার বয়স কত বছর?",
    subtitle_en: "Pensions, scholarships and welfare grants have specific age brackets.",
    subtitle_hi: "पेंशन, छात्रवृत्ति और कल्याणकारी अनुदानों की निर्धारित आयु सीमा होती है।",
    subtitle_bn: "পেনশন ও বৃত্তির জন্য নির্দিষ্ট বয়সসীমা রয়েছে।",
    type: "number",
    min: 1,
    max: 120,
    unit_en: "Years",
    unit_hi: "वर्ष",
    unit_bn: "বছর",
    presets: [19, 25, 35, 45, 52, 60, 65]
  },
  marital_status: {
    title_en: "What is your marital status?",
    title_hi: "आपकी वैवाहिक स्थिति क्या है?",
    title_bn: "আপনার বৈবাহিক অবস্থা কি?",
    subtitle_en: "Special security pensions exist for widows, single women, and deserted citizens.",
    subtitle_hi: "विधवाओं, एकल महिलाओं और निराधार नागरिकों के लिए विशेष सुरक्षा सहायता उपलब्ध है।",
    subtitle_bn: "বিধবা এবং নিঃস্ব নাগরিকদের জন্য বিশেষ সামাজিক সুরক্ষা রয়েছে।",
    type: "single_choice",
    options: [
      { label_en: "Widow / Widower", label_hi: "विधवा / विधुर", label_bn: "বিধবা / বিপত্নীক", value: "widow" },
      { label_en: "Married", label_hi: "विवाहित", label_bn: "বিবাহিত", value: "married" },
      { label_en: "Unmarried / Single", label_hi: "अविवाहित / अकेला", label_bn: "অবিবাহিত", value: "single" },
      { label_en: "Divorced / Deserted", label_hi: "तलाकशुदा / परित्यक्ता", label_bn: "তালাকপ্রাপ্ত / পরিত্যক্ত", value: "divorced" }
    ]
  },
  occupation: {
    title_en: "What is your primary occupation or current status?",
    title_hi: "आपका मुख्य व्यवसाय या वर्तमान स्थिति क्या है?",
    title_bn: "আপনার প্রধান পেশা বা বর্তমান অবস্থা কি?",
    subtitle_en: "Identifies targeted schemes for farmers, students, laborers and homemakers.",
    subtitle_hi: "किसानों, छात्रों, मजदूरों और गृहिणियों के लिए विशिष्ट योजनाओं की पहचान करता है।",
    subtitle_bn: "কৃষক, ছাত্র, শ্রমিকদের জন্য নির্দিষ্ট প্রকল্প চিহ্নিত করে।",
    type: "single_choice",
    options: [
      { label_en: "Farmer / Cultivator", label_hi: "किसान / काश्तकार", label_bn: "কৃষক", value: "farmer" },
      { label_en: "College / Higher Education Student", label_hi: "कॉलेज / उच्च शिक्षा छात्र", label_bn: "কলেজ / উচ্চশিক্ষার ছাত্র", value: "student" },
      { label_en: "Agricultural Laborer / Daily Wage Worker", label_hi: "खेतिहर मजदूर / दैनिक श्रमिक", label_bn: "কৃষি শ্রমিক / দিনমজুর", value: "agricultural_worker" },
      { label_en: "Homemaker", label_hi: "गृहिणी", label_bn: "গৃহিনী", value: "homemaker" },
      { label_en: "Self-Employed / Small Vendor", label_hi: "स्व-रोजगार / छोटा दुकानदार", label_bn: "স্ব-নিযুক্ত / ক্ষুদ্র ব্যবসায়ী", value: "self_employed" },
      { label_en: "Unemployed / Looking for Work", label_hi: "बेरोजगार / काम की तलाश", label_bn: "বেকার", value: "unemployed" },
      { label_en: "Private / Informal Sector Job", label_hi: "निजी / असंगठित क्षेत्र", label_bn: "বেসরকারি চাকরি", value: "private_job" }
    ]
  },
  annual_income: {
    title_en: "What is your approximate annual family income?",
    title_hi: "आपके परिवार की अनुमानित वार्षिक आय कितनी है?",
    title_bn: "আপনার পরিবারের আনুমানিক বার্ষিক আয় কত?",
    subtitle_en: "Combined gross income of all earning family members in INR.",
    subtitle_hi: "परिवार के सभी कमाने वाले सदस्यों की कुल संयुक्त वार्षिक आय।",
    subtitle_bn: "পরিবারের সকল উপার্জনকারী সদস্যের মোট বার্ষিক আয়।",
    type: "single_choice",
    options: [
      { label_en: "Less than ₹1,00,000 (Low income / BPL)", label_hi: "₹1,00,000 से कम (अति निम्न आय / बीपीएल)", label_bn: "₹১,০০,০০০ এর কম (বিপিএল)", value: 65000 },
      { label_en: "₹1,00,000 to ₹2,50,000", label_hi: "₹1,00,000 से ₹2,50,000", label_bn: "₹১,০০,০০০ থেকে ₹২,৫০,০০০", value: 180000 },
      { label_en: "₹2,50,000 to ₹6,00,000", label_hi: "₹2,50,000 से ₹6,00,000", label_bn: "₹২,৫০,০০০ থেকে ₹৬,০০,০০০", value: 450000 },
      { label_en: "Above ₹6,00,000", label_hi: "₹6,00,000 से अधिक", label_bn: "₹৬,০০,০০০ এর বেশি", value: 750000 }
    ]
  },
  landholding_hectares: {
    title_en: "How much cultivable agricultural land does your family own?",
    title_hi: "आपके परिवार के पास कितनी कृषि भूमि है?",
    title_bn: "আপনার পরিবারের কত পরিমাণ কৃষি জমি আছে?",
    subtitle_en: "1 hectare is approx 2.47 acres. Small farmers hold up to 2.0 hectares.",
    subtitle_hi: "1 हेक्टेयर लगभग 2.47 एकड़ होता है। लघु किसानों के पास 2 हेक्टेयर तक भूमि होती है।",
    subtitle_bn: "১ হেক্টর প্রায় ২.৪৭ একর। ক্ষুদ্র কৃষকদের ২ হেক্টর পর্যন্ত জমি থাকে।",
    type: "single_choice",
    options: [
      { label_en: "No land (0 hectares / Landless)", label_hi: "कोई कृषि भूमि नहीं (0 हेक्टेयर / भूमिहीन)", label_bn: "কোনো জমি নেই (ভূমিহীন)", value: 0.0 },
      { label_en: "Small / Marginal (Up to 2.0 hectares / ~5 acres)", label_hi: "लघु एवं सीमांत किसान (2 हेक्टेयर तक)", label_bn: "ক্ষুদ্র কৃষক (২ হেক্টর পর্যন্ত)", value: 1.5 },
      { label_en: "Large landholder (More than 2.0 hectares)", label_hi: "बड़ा भूमिधारक (2 हेक्टेयर से अधिक)", label_bn: "বড় কৃষক (২ হেক্টরের বেশি)", value: 3.5 }
    ]
  },
  student_class12_marks_percent: {
    title_en: "What was your score percentage in Class 12 board examination?",
    title_hi: "12वीं बोर्ड परीक्षा में आपका प्रतिशत कितना था?",
    title_bn: "দ্বাদশ শ্রেণির বোর্ড পরীক্ষায় আপনার শতাংশ কত ছিল?",
    subtitle_en: "Merit scholarships like MMVY require >=70% (State Board) or >=85% (CBSE/ICSE).",
    subtitle_hi: "मेधावी छात्रवृत्ति के लिए 70% (एमपी बोर्ड) या 85% (सीबीएसई) अंक आवश्यक हैं।",
    subtitle_bn: "মেধা বৃত্তির জন্য ৭০%+ বা ৮৫%+ নম্বর প্রয়োজন।",
    type: "number",
    min: 33,
    max: 100,
    unit_en: "%",
    unit_hi: "%",
    unit_bn: "%",
    presets: [65, 72, 80, 86, 92]
  },
  enrolled_higher_education: {
    title_en: "Are you admitted or enrolled in recognized higher education?",
    title_hi: "क्या आप किसी मान्यता प्राप्त उच्च शिक्षा / कॉलेज में अध्ययनरत हैं?",
    title_bn: "আপনি কি কোনো স্বীকৃত উচ্চশিক্ষায় ভর্তি হয়েছেন?",
    subtitle_en: "Undergraduate degree, Engineering, Medical, Polytechnic diploma, or Law.",
    subtitle_hi: "स्नातक डिग्री, इंजीनियरिंग, मेडिकल, पॉलिटेक्निक डिप्लोमा या लॉ।",
    subtitle_bn: "স্নাতক ডিগ্রি, ইঞ্জিনিয়ারিং, মেডিকেল বা পলিটেকনিক।",
    type: "boolean",
    options: [
      { label_en: "Yes, enrolled in Higher Education", label_hi: "हाँ, उच्च शिक्षा में प्रवेश लिया है", label_bn: "হ্যাঁ, উচ্চশিক্ষায় ভর্তি আছি", value: true },
      { label_en: "No / Not enrolled", label_hi: "नहीं / अध्ययनरत नहीं हैं", label_bn: "না, ভর্তি নেই", value: false }
    ]
  },
  has_pucca_house: {
    title_en: "Does your family own a permanent pucca house?",
    title_hi: "क्या आपके परिवार के पास कोई पक्का मकान है?",
    title_bn: "আপনার পরিবারের কি কোনো পাকা বাড়ি আছে?",
    subtitle_en: "PMAY housing grants prioritize families residing in kutcha or makeshift dwellings.",
    subtitle_hi: "पीएम आवास योजना कच्चे मकानों में रहने वाले परिवारों को प्राथमिकता देती है।",
    subtitle_bn: "আবাস যোজনা কাঁচা বাড়িতে বসবাসকারী পরিবারকে অগ্রাধিকার দেয়।",
    type: "boolean",
    options: [
      { label_en: "No, we live in a Kutcha / mud house", label_hi: "नहीं, हम कच्चे मकान में रहते हैं", label_bn: "না, আমরা কাঁচা বাড়িতে থাকি", value: false },
      { label_en: "Yes, we own a Pucca house", label_hi: "हाँ, हमारे पास पक्का मकान है", label_bn: "হ্যাঁ, আমাদের পাকা বাড়ি আছে", value: true }
    ]
  },
  bpl_card_holder: {
    title_en: "Does your family hold an active BPL / Antyodaya Ration Card?",
    title_hi: "क्या आपके परिवार के पास बीपीएल / अंत्योदय राशन कार्ड है?",
    title_bn: "আপনার পরিবারের কি বিপিএল / অন্ত্যোদয় রেশন কার্ড আছে?",
    subtitle_en: "State Food & Civil Supplies below-poverty-line proof.",
    subtitle_hi: "खाद्य एवं नागरिक आपूर्ति विभाग द्वारा जारी गरीबी रेखा से नीचे का कार्ड।",
    subtitle_bn: "খাদ্য ও সরবরাহ দপ্তর কর্তৃক প্রদত্ত বিপিএল কার্ড।",
    type: "boolean",
    options: [
      { label_en: "Yes, we have BPL / Antyodaya Card", label_hi: "हाँ, हमारे पास बीपीएल / अंत्योदय कार्ड है", label_bn: "হ্যাঁ, আমাদের বিপিএল কার্ড আছে", value: true },
      { label_en: "No BPL Card", label_hi: "बीपीएल कार्ड नहीं है", label_bn: "না, বিপিএল কার্ড নেই", value: false }
    ]
  },
  is_institutional_landholder: {
    title_en: "Is the agricultural land registered under an institution, trust, or company?",
    title_hi: "क्या कृषि भूमि किसी संस्थागत, ट्रस्ट या कंपनी के नाम पर है?",
    title_bn: "কৃষি জমি কি কোনো সংস্থা, ট্রাস্ট বা কোম্পানির নামে?",
    subtitle_en: "PM-KISAN only benefits individual family cultivators.",
    subtitle_hi: "पीएम-किसान केवल व्यक्तिगत किसान परिवारों को लाभ देती है।",
    subtitle_bn: "পিএম-কিষাণ কেবল ব্যক্তি কৃষকদের জন্য প্রযোজ্য।",
    type: "boolean",
    options: [
      { label_en: "No, land is individually / family owned", label_hi: "नहीं, भूमि व्यक्तिगत / परिवार के नाम है", label_bn: "না, জমি ব্যক্তিগত মালিকানাধীন", value: false },
      { label_en: "Yes, land is institutionally held", label_hi: "हाँ, भूमि संस्थागत या ट्रस्ट के नाम है", label_bn: "হ্যাঁ, জমি প্রাতিষ্ঠানিক মালিকানাধীন", value: true }
    ]
  },
  holds_constitutional_post: {
    title_en: "Does anyone in your family hold a government job or constitutional post?",
    title_hi: "क्या आपके परिवार में कोई सरकारी नौकरी या संवैधानिक पद पर है?",
    title_bn: "আপনার পরিবারের কেউ কি সরকারি চাকরি বা সাংবিধানিক পদে আছেন?",
    subtitle_en: "Serving government employees and constitutional post-holders are excluded from farm income aid.",
    subtitle_hi: "सरकारी कर्मचारी और संवैधानिक पदधारक किसान सम्मान निधि के अंतर्गत अपात्र हैं।",
    subtitle_bn: "সরকারি চাকরিজীবী বা সাংবিধানিক পদাধিকারীরা বাদ পড়েন।",
    type: "boolean",
    options: [
      { label_en: "No government employee / post in family", label_hi: "नहीं, परिवार में कोई सरकारी कर्मचारी नहीं है", label_bn: "না, কেউ সরকারি পদে নেই", value: false },
      { label_en: "Yes, family member holds govt job", label_hi: "हाँ, परिवार में सरकारी नौकरी है", label_bn: "হ্যাঁ, সরকারি চাকরিজীবী আছেন", value: true }
    ]
  },
  category: {
    title_en: "What is your social / reservation category?",
    title_hi: "आपकी सामाजिक / आरक्षण श्रेणी क्या है?",
    title_bn: "আপনার সামাজিক শ্রেণী কি?",
    subtitle_en: "Helps identify targeted grants, fee waivers, and reservation quotas.",
    subtitle_hi: "लक्षित योजनाओं, शुल्क प्रतिपूर्ति एवं आरक्षण लाभों की पहचान करता है।",
    subtitle_bn: "সংরক্ষণ সুবিধা এবং নির্দিষ্ট প্রকল্পের জন্য।",
    type: "single_choice",
    options: [
      { label_en: "General", label_hi: "सामान्य (General)", label_bn: "সাধারণ (General)", value: "General" },
      { label_en: "OBC (Other Backward Class)", label_hi: "ओबीसी (अन्य पिछड़ा वर्ग)", label_bn: "ওবিসি", value: "OBC" },
      { label_en: "SC (Scheduled Caste)", label_hi: "अनुसूचित जाति (SC)", label_bn: "তপশিলি জাতি (SC)", value: "SC" },
      { label_en: "ST (Scheduled Tribe)", label_hi: "अनुसूचित जनजाति (ST)", label_bn: "তপশিলি উপজাতি (ST)", value: "ST" },
      { label_en: "EWS (Economically Weaker Section)", label_hi: "ईडब्ल्यूएस (EWS)", label_bn: "ইডব্লিউএস", value: "EWS" }
    ]
  },
  disability_status: {
    title_en: "Do you have an officially certified disability (>=40%)?",
    title_hi: "क्या आपके पास 40% या अधिक का दिव्यांगता प्रमाण पत्र है?",
    title_bn: "আপনার কি ৪০% বা তার বেশি প্রতিবন্ধী সার্টিফিকেট আছে?",
    subtitle_en: "Special pensions and assistive equipment grants are available for Divyangjan.",
    subtitle_hi: "दिव्यांगजनों के लिए विशेष पेंशन एवं सहायक उपकरण योजनाएं उपलब्ध हैं।",
    subtitle_bn: "প্রতিবন্ধী ব্যক্তিদের জন্য বিশেষ আর্থিক সহায়তা।",
    type: "boolean",
    options: [
      { label_en: "Yes, have disability certificate (>=40%)", label_hi: "हाँ, दिव्यांगता प्रमाण पत्र उपलब्ध है", label_bn: "হ্যাঁ, সার্টিফিকেট আছে", value: true },
      { label_en: "No disability / Not certified", label_hi: "नहीं, कोई दिव्यांगता नहीं है", label_bn: "না, কোনো প্রতিবন্ধকতা নেই", value: false }
    ]
  }
};

/**
 * Returns formatted question metadata for a given field
 */
export function getFieldQuestion(fieldName, language = "hi") {
  const meta = QUESTION_METADATA[fieldName];
  if (!meta) {
    return {
      title: language === "hi" ? `कृपया ${fieldName} दर्ज करें` : `Please enter ${fieldName}`,
      subtitle: language === "hi" ? "सत्यापन हेतु आवश्यक" : "Required for verification",
      type: "text",
      options: []
    };
  }

  const title = meta[`title_${language}`] || meta.title_hi || meta.title_en;
  const subtitle = meta[`subtitle_${language}`] || meta.subtitle_hi || meta.subtitle_en;
  const unit = meta[`unit_${language}`] || meta.unit_hi || meta.unit_en || "";

  return {
    ...meta,
    title,
    subtitle,
    unit
  };
}
