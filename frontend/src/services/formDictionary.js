// Client-side instant grounded knowledge base for public welfare application form terminology
// Guarantees zero-latency (<1ms) explanations and reliable offline/Vercel performance.

export const CLIENT_FORM_DICTIONARY = [
  {
    id: 'vakil_nama',
    aliases: ['vakil nama', 'vakalatnama', 'vakalat nama', 'vakil', 'vakeel', 'advocate', 'वकालतनामा', 'वकील नामा', 'वकील', 'वकालत', 'ওয়াকালাতনামা', 'উকিলনামা'],
    field_name: 'Vakalatnama / Memorandum of Advocate Appearance',
    field_name_hi: 'वकालतनामा (अधिवक्ता नियुक्ति अधिकार पत्र)',
    field_name_mr: 'वकालतनामा (कायदेशीर प्रतिनिधी नियुक्ती पत्र)',
    field_name_bn: 'ওয়াকালাতনামা / আইনজীবী নিয়োগপত্র',
    explanations: {
      hi: 'राजस्व न्यायालय, तहसीलदार, एसडीएम अथवा अपीलीय अधिकरण में योजना विवाद, ज़मीन नामांतरण, या पेंशन अपील में नागरिक की ओर से अधिवक्ता/वकील नियुक्त करने का वैधानिक अधिकार पत्र।',
      en: 'Official legal authorization document empowering an advocate/lawyer to represent a citizen before a revenue court, Tehsildar, SDM, or appellate tribunal in welfare dispute, land mutation, or pension appeal proceedings.',
      mr: 'महसूल न्यायालय, तहसीलदार अथवा अपीलीय प्राधिकाऱ्यासमोर नागरिकाच्या वतीने कायदेशीर बाजू मांडण्यासाठी वकिलाची नियुक्ती करणारे अधिकृत अधिकारपत्र.',
      bn: 'রাজস্ব আদালত, এসডিএম বা সংশ্লিষ্ট দপ্তরে আবেদনের শুনানিতে নাগরিকের পক্ষে প্রতিনিধিত্ব করার জন্য আইনজীবী নিয়োগের আইনি প্রমাণপত্র।'
    },
    example: 'Duly signed by applicant with ₹10 Welfare Stamp / Court Fee affixed (Obtained from Court / Bar Council / Notary)'
  },
  {
    id: 'khasra',
    aliases: ['khasra', 'khatauni', '7/12', 'satbara', 'bhulekh', 'survey number', 'खसरा', 'खतौनी', 'सातबारा', 'गावाचा नमुना', 'খতিয়ান', 'দাগ', 'खसरा नंबर', 'खसरा क्रमांक'],
    field_name: 'Khasra / Khatauni / 7/12 Survey Number',
    field_name_hi: 'खसरा / खतौनी / सर्वे क्रमांक',
    field_name_mr: 'सातबारा (७/१२) / गट / सर्व्हे नंबर',
    field_name_bn: 'খতিয়ান ও দাগ নম্বর (Khasra No.)',
    explanations: {
      hi: 'राज्य राजस्व अभिलेखों (भूलेख/सातबारा) में दर्ज कृषि भूमि का विशिष्ट पहचान सर्वे नंबर, जिससे आपकी जमीन के मालिकाना हक या जोत की पुष्टि होती है।',
      en: 'Specific agricultural land parcel survey number in state revenue records (Bhulekh / 7/12 extract) verifying legal land ownership or tenancy.',
      mr: 'जमीन महसूल नोंदीतील शेतजमिनीचा सातबारा (७/१२) व गट/सर्व्हे क्रमांक, ज्यावरून कायदेशीर मालकी हक्क सिद्ध होतो.',
      bn: 'রাজস্ব রেকর্ডে কৃষিজমির নির্দিষ্ট খতিয়ান বা দাগ নম্বর, যা জমির আইনি মালিকানা নির্দেশ করে।'
    },
    example: 'Khasra No. 142/2, Khatauni 58 (Look at top of your Bhulekh / 7/12 slip)'
  },
  {
    id: 'npci',
    aliases: ['npci', 'dbt', 'seeding', 'direct benefit', 'डीबीटी', 'एनपीसीआई', 'सीडिंग', 'मॅपिंग', 'आधार बैंक डीबीटी'],
    field_name: 'Aadhaar NPCI / DBT Seeding Status',
    field_name_hi: 'आधार बैंक एनपीसीआई / डीबीटी मैपिंग',
    field_name_mr: 'आधार बँक डीबीटी / NPCI संलग्नता',
    field_name_bn: 'আধার ব্যাঙ্ক এনপিসিআই / ডিবিটি ম্যাপিং',
    explanations: {
      hi: 'यह प्रमाणित करता है कि आपका बैंक खाता एनपीसीआई (NPCI) मैपर पर आधार से लिंक है, ताकि सरकारी सब्सिडी और किसान सम्मान निधि सीधे बैंक खाते में पहुंचे।',
      en: 'Confirms your bank account is mapped on NPCI Aadhaar Payment Bridge to receive direct welfare subsidies and cash transfers without middleman delay.',
      mr: 'तुमचे बँक खाते आधार व NPCI शी संलग्न आहे की नाही याची नोंद, जेणेकरून शासकीय अनुदानाचा थेट लाभ (DBT) त्वरित खात्यात जमा होतो.',
      bn: 'আপনার ব্যাঙ্ক অ্যাকাউন্টটি আধার এবং NPCI-এর সাথে যুক্ত যাতে সরকারি ভাতার টাকা সরাসরি অ্যাকাউন্টে ঢোকে।'
    },
    example: 'Active / Linked (Submit "NPCI Aadhaar Mandate" form at your home bank branch)'
  },
  {
    id: 'samagra',
    aliases: ['samagra', 'samagra id', 'sssmid', 'समग्र', 'समग्र आईडी', 'समग्र परिवार', 'सदस्य आईडी'],
    field_name: 'Samagra Family & Member ID (MP)',
    field_name_hi: 'समग्र परिवार एवं सदस्य आईडी',
    field_name_mr: 'समग्र कुटुंब व सदस्य आयडी (मध्य प्रदेश)',
    field_name_bn: 'সমগ্র পরিবার ও সদস্য আইডি (মধ্যপ্রদেশ)',
    explanations: {
      hi: 'मध्य प्रदेश राज्य में 8-अंकों का परिवार आईडी और 9-अंकों का व्यक्तिगत सदस्य आईडी कोड, जो लाड़ली बहना, छात्रवृत्ति और राशन के लिए अनिवार्य है।',
      en: 'Madhya Pradesh 8-digit family and 9-digit member identity code printed on Samagra portal (samagra.gov.in) for citizen welfare entitlements.',
      mr: 'मध्य प्रदेशातील ८ अंकी कुटुंब आयडी आणि ९ अंकी वैयक्तिक सदस्य आयडी, जो सर्व शासकीय योजनांसाठी अनिवार्य आहे.',
      bn: 'মধ্যপ্রদেশের ৮-সংখ্যার পরিবার আইডি এবং ৯-সংখ্যার সদস্য আইডি, যা সরকারি সুবিধার জন্য প্রয়োজন।'
    },
    example: 'Family ID: 12345678, Member ID: 123456789'
  },
  {
    id: 'ration_card',
    aliases: ['ration', 'ration card', 'bpl', 'aay', 'phh', 'राशन कार्ड', 'बीपीएल', 'अंत्योदय', 'रेशन कार्ड', 'রেশন কার্ড', 'राशन कार्ड क्रमांक'],
    field_name: 'Ration Card Number & Category (BPL/AAY)',
    field_name_hi: 'राशन कार्ड क्रमांक एवं श्रेणी (BPL / AAY)',
    field_name_mr: 'रेशन कार्ड क्रमांक व वर्गवारी (बीपीएल / अंत्योदय)',
    field_name_bn: 'রেশন কার্ড নম্বর ও শ্রেণি (BPL/AAY)',
    explanations: {
      hi: 'खाद्य एवं नागरिक आपूर्ति विभाग द्वारा जारी राशन कार्ड संख्या और श्रेणी (BPL - गरीबी रेखा से नीचे, AAY - अंत्योदय अन्न योजना)।',
      en: 'Food security ration card number and socio-economic category (BPL - Below Poverty Line, AAY - Antyodaya Anna Yojana) proving economic status.',
      mr: 'अन्न व नागरी पुरवठा विभागाने दिलेला रेशन कार्ड क्रमांक आणि संवर्ग (पिवळे/केशरी/बीपीएल/अंत्योदय).',
      bn: 'খাদ্য সরবরাহ দপ্তর প্রদত্ত রেশন কার্ড নম্বর এবং অর্থনৈতিক শ্রেণি (BPL/AAY/SPHH)।'
    },
    example: 'Card No: 231908412091, Category: BPL (Yellow/Pink Card)'
  },
  {
    id: 'income',
    aliases: ['income', 'income cert', 'aay', 'आय', 'आय प्रमाण पत्र', 'उत्पन्न दाखला', 'আয়ের শংসাপত্র', 'पारिवारिक आय'],
    field_name: 'Annual Family Income Certificate Number',
    field_name_hi: 'वार्षिक पारिवारिक आय प्रमाण पत्र क्रमांक',
    field_name_mr: 'वार्षिक कौटुंबिक उत्पन्न दाखला क्रमांक',
    field_name_bn: 'বার্ষিক পারিবারিক আয়ের শংসাপত্র নম্বর',
    explanations: {
      hi: 'सक्षम राजस्व अधिकारी (तहसीलदार/एसडीएम) द्वारा जारी प्रमाण पत्र क्रमांक, जो सभी स्रोतों से कुल वार्षिक पारिवारिक आय सिद्ध करता है।',
      en: 'Official certificate number issued by the Tehsildar or e-District certifying total annual household earnings from all sources.',
      mr: 'तहसीलदार किंवा अधिकृत अधिकाऱ्याने दिलेला कौटुंबिक वार्षिक उत्पन्नाचा दाखला क्रमांक.',
      bn: 'সক্ষম রাজস্ব আধিকারিক কর্তৃক প্রদত্ত বার্ষিক পারিবারিক আয়ের প্রমাণপত্র নম্বর।'
    },
    example: 'Certificate No: INC/2024/99120, Annual Amount: ₹60,000'
  },
  {
    id: 'domicile',
    aliases: ['domicile', 'mool niwas', 'niwas', 'resident', 'निवास', 'मूल निवास', 'अधिवास', 'আবাসিক', 'मूल निवास प्रमाण पत्र'],
    field_name: 'Domicile / Resident Certificate Number',
    field_name_hi: 'मूल निवास / अधिवास प्रमाण पत्र क्रमांक',
    field_name_mr: 'अधिवास (डोमिसाईल) दाखला क्रमांक',
    field_name_bn: 'আবাসিক শংসাপত্র নম্বর (Domicile No.)',
    explanations: {
      hi: 'वैधानिक प्रमाण पत्र क्रमांक जो यह प्रमाणित करता है कि आप संबंधित राज्य (जैसे मध्य प्रदेश या महाराष्ट्र) के स्थायी मूल निवासी हैं।',
      en: 'Legal statutory certificate number verifying permanent state domicile / residential status required for state welfare schemes.',
      mr: 'संबंधित राज्याचे कायमस्वरूपी रहिवासी असल्याचा अधिकृत पुरावा देणारा अधिवास प्रमाणपत्र क्रमांक.',
      bn: 'রাজ্যের স্থায়ী বাসিন্দা হিসেবে প্রমাণকারী আবাসিক শংসাপত্র নম্বর।'
    },
    example: 'Certificate No: RS/2023/182405 (Issued via Lok Seva Kendra / MahaOnline)'
  },
  {
    id: 'affidavit',
    aliases: ['affidavit', 'shapath patra', 'self declaration', 'शपथ पत्र', 'घोषणा पत्र', 'प्रतिज्ञापत्र', 'হলফনামা'],
    field_name: 'Notarized Affidavit / Self-Declaration',
    field_name_hi: 'शपथ पत्र / स्व-प्रमाणित घोषणा पत्र',
    field_name_mr: 'प्रतिज्ञापत्र / स्वघोषणा पत्र',
    field_name_bn: 'হলফনামা / স্ব-ঘোষণাপত্র',
    explanations: {
      hi: '₹10 या ₹50 के स्टांप पेपर पर नोटरी द्वारा सत्यापित वैधानिक हलफनामा (जैसे गैर-आयकर दाता होने या भूमिहीन होने की पुष्टि हेतु)।',
      en: 'Sworn legal declaration on non-judicial stamp paper verified by an Executive Magistrate or Notary (e.g. non-taxpayer or single status).',
      mr: 'नोटाऱ्याने प्रमाणित केलेले प्रतिज्ञापत्र, ज्यामध्ये उत्पन्नाची किंवा स्थितीची सत्यता घोषित केलेली असते.',
      bn: 'নোটারি বা ম্যাজিস্ট্রেটের মাধ্যমে শপথপূর্বক লিখিত স্ব-ঘোষণাপত্র।'
    },
    example: 'Affidavit on ₹50 Stamp Paper attested by Notary Public / Oath Commissioner'
  },
  {
    id: 'ifsc',
    aliases: ['ifsc', 'ifsc code', 'branch code', 'आईएफएससी', 'आयएफएससी', 'बैंक शाखा कोड'],
    field_name: 'Bank Branch IFSC Code',
    field_name_hi: 'बैंक शाखा आईएफएससी (IFSC) कोड',
    field_name_mr: 'बँक शाखा आयएफएससी (IFSC) कोड',
    field_name_bn: 'ব্যাঙ্ক শাখা আইএফএসসি (IFSC) কোড',
    explanations: {
      hi: '11-अक्षरों का अद्वितीय कोड जो सीधे आपकी बैंक शाखा की पहचान करता है। पासबुक के पहले पन्ने या चेक बुक पर छपा होता है।',
      en: '11-character alphanumeric code uniquely identifying your bank branch for electronic money transfers. Found on the 1st page of your passbook.',
      mr: '११ अक्षरी कोड जो थेट तुमच्या बँकेच्या शाखेचा पत्ता निश्चित करतो. बँक पासबुकच्या पहिल्या पानावर नोंदवलेला असतो.',
      bn: '১১ অক্ষরের অনন্য কোড যা ইলেকট্রনিক ফান্ড ট্রান্সফারের জন্য নির্দিষ্ট ব্যাঙ্ক শাখা নির্দেশ করে।'
    },
    example: 'SBIN0001234, PUNB0245100, BKID0009012'
  },
  {
    id: 'caste',
    aliases: ['caste', 'jati', 'category', 'जाति', 'जाति प्रमाण पत्र', 'जात प्रमाणपत्र', 'তফসিলি', 'জাতি', 'वर्ग प्रमाण पत्र'],
    field_name: 'Caste / Social Category Certificate',
    field_name_hi: 'जाति / सामाजिक वर्ग प्रमाण पत्र क्रमांक',
    field_name_mr: 'जात प्रमाणपत्र क्रमांक (SC/ST/OBC/EWS)',
    field_name_bn: 'জাতি শংসাপত্র নম্বর (SC/ST/OBC)',
    explanations: {
      hi: 'सक्षम राजस्व अधिकारी द्वारा जारी प्रमाण पत्र जो आपकी सामाजिक श्रेणी (SC, ST, OBC, या EWS) प्रमाणित करता है।',
      en: 'Government-issued caste certificate number certifying SC, ST, OBC, or EWS category for reservation or target welfare grants.',
      mr: 'सक्षम प्राधिकाऱ्याने दिलेला जात प्रमाणपत्र क्रमांक, जो सामाजिक आरक्षणासाठी अनिवार्य आहे.',
      bn: 'তফসিলি জাতি, উপজাতি বা অন্যান্য অনগ্রসর শ্রেণিভুক্তির প্রমাণপত্র নম্বর।'
    },
    example: 'Certificate No: CST/2023/45102 (Issuing Authority: SDO / Tehsildar)'
  },
  {
    id: 'udid',
    aliases: ['udid', 'disability', 'divyang', 'handicap', 'दिव्यांग', 'यूडीआईडी', 'अपंगत्व', 'প্রতিবন্ধী', 'दिव्यांगता प्रमाण पत्र'],
    field_name: 'Unique Disability ID (UDID) / Swavlamban Card',
    field_name_hi: 'दिव्यांग यूडीआईडी (UDID) / स्वावलंबन कार्ड संख्या',
    field_name_mr: 'दिव्यांग स्वावलंबन (UDID) कार्ड क्रमांक',
    field_name_bn: 'ইউডিআইডি (UDID) বা প্রতিবন্ধী কার্ড নম্বর',
    explanations: {
      hi: 'दिव्यांगजन सशक्तिकरण विभाग या मेडिकल बोर्ड द्वारा जारी 18-अंकों का विशिष्ट पहचान पत्र, जिसमें दिव्यांगता प्रतिशत (उदा. 40%+) अंकित होता है।',
      en: '18-character unique disability identification number issued by medical board/Swavlamban portal certifying disability percentage.',
      mr: 'वैद्यकीय मंडळाने दिलेला स्वावलंबन (UDID) कार्ड क्रमांक, ज्यामध्ये अपंगत्वाची टक्केवारी नमूद असते.',
      bn: 'মেডিকেল বোর্ড কর্তৃক প্রদত্ত ইউডিআইডি কার্ড নম্বর, যাতে প্রতিবন্ধকতার শতকরা হার উল্লেখিত থাকে।'
    },
    example: 'UDID No: MP1420119900014298 (40% Loco-motor disability)'
  }
];

export function lookupFormTerm(query, lang = 'hi') {
  if (!query || typeof query !== 'string') return null;
  const q = query.trim().toLowerCase();
  
  const matched = CLIENT_FORM_DICTIONARY.find(item =>
    item.aliases.some(alias => alias.toLowerCase() === q || q.includes(alias.toLowerCase()) || alias.toLowerCase().includes(q))
  );

  if (matched) {
    const primary = {
      field_name: matched.field_name,
      field_name_hi: matched.field_name_hi,
      field_name_mr: matched.field_name_mr,
      field_name_bn: matched.field_name_bn,
      explanation: matched.explanations[lang] || matched.explanations.hi || matched.explanations.en,
      example: matched.example
    };

    // Include 2 top related terms for richer guidance
    const related = CLIENT_FORM_DICTIONARY
      .filter(it => it.id !== matched.id)
      .slice(0, 2)
      .map(it => ({
        field_name: it.field_name,
        field_name_hi: it.field_name_hi,
        field_name_mr: it.field_name_mr,
        field_name_bn: it.field_name_bn,
        explanation: it.explanations[lang] || it.explanations.hi || it.explanations.en,
        example: it.example
      }));

    return {
      explanations: [primary, ...related],
      general_guidance: lang === 'hi'
        ? '💡 सुनिश्चित करें कि फॉर्म पर आपका नाम और वर्तनी आधार कार्ड तथा बैंक पासबुक से हूबहू मेल खाती हो।'
        : '💡 Double-check that your name spelling on the form matches your Aadhaar Card and Bank Passbook exactly to prevent payment rejections.',
      disclaimer: 'AI Guidance is for assistance only. Official sanction is subject to physical verification by authorized revenue / welfare officers.'
    };
  }

  // Fallback for uncatalogued query
  return {
    explanations: [
      {
        field_name: query,
        field_name_hi: query,
        field_name_mr: query,
        field_name_bn: query,
        explanation: lang === 'hi'
          ? `आधिकारिक कॉलम '${query}': अपने संबंधित सरकारी प्रमाण पत्र अथवा राजस्व दस्तावेज़ पर दर्ज सटीक पंजीयन संख्या या विवरण दर्ज करें। यदि आवश्यक हो तो निकटतम लोक सेवा केंद्र (CSC) से संपर्क करें।`
          : `Official form field '${query}': Enter the exact registered value as recorded on your verified government certificate or revenue document. Contact your nearest Lok Seva Kendra or CSC if clarification is needed.`,
        example: 'Refer to your Aadhaar card or official certificate for the matching registration number.'
      },
      ...CLIENT_FORM_DICTIONARY.slice(0, 2).map(it => ({
        field_name: it.field_name,
        field_name_hi: it.field_name_hi,
        field_name_mr: it.field_name_mr,
        field_name_bn: it.field_name_bn,
        explanation: it.explanations[lang] || it.explanations.hi || it.explanations.en,
        example: it.example
      }))
    ],
    general_guidance: '💡 Always confirm unknown field details with your local Gram Panchayat, Ward Office, or CSC operator before final submission.',
    disclaimer: 'AI Guidance is for assistance only. Official sanction is subject to physical verification.'
  };
}

