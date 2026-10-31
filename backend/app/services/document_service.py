from typing import Dict, List, Optional
from ..models.document import DocumentDefinition, DocumentSamplePreview, DocumentSummary

DOCUMENT_CATALOG: Dict[str, DocumentDefinition] = {
    "income_certificate": DocumentDefinition(
        id="income_certificate",
        aliases=["income_cert", "income_cert_tehsildar", "aay_praman_patra"],
        name_en="Income Certificate",
        name_hi="आय प्रमाण पत्र (Income Certificate)",
        category="Revenue",
        short_explanation_en="An official certificate issued by the state revenue department certifying the total annual earnings of a citizen's family from all sources.",
        short_explanation_hi="राज्य के राजस्व विभाग द्वारा जारी एक आधिकारिक प्रमाण पत्र जो सभी स्रोतों से नागरिक के परिवार की कुल वार्षिक आय को प्रमाणित करता है।",
        why_schemes_ask_en="Government welfare programs and scholarships (e.g. MMVY, Ladli Behna, Sanjay Gandhi Niradhar) are targeted at specific income groups. The income certificate provides statutory proof that family income does not exceed the scheme's ceiling.",
        why_schemes_ask_hi="सरकारी कल्याणकारी योजनाएं और छात्रवृत्तियां (जैसे MMVY, लाड़ली बहना, संजय गांधी निराधार) विशिष्ट आय वर्गों के लिए होती हैं। यह प्रमाण पत्र सिद्ध करता है कि पारिवारिक आय योजना की सीमा से कम है।",
        issuer_en="Sub-Divisional Magistrate (SDM) / Tehsildar / Revenue Department",
        issuer_hi="अनुविभागीय अधिकारी (SDM) / तहसीलदार / राजस्व विभाग",
        contents_en=[
            "Applicant's and Head of Household's full name",
            "Permanent address and village/ward name",
            "Certified annual family income in INR (both numeric and words)",
            "Financial year of assessment and validity period (typically 3 years in MP)",
            "Digital signature and unique certificate verification number with QR code"
        ],
        contents_hi=[
            "आवेदक एवं परिवार के मुखिया का पूरा नाम",
            "स्थायी पता, गांव/वार्ड और तहसील",
            "रुपयों में प्रमाणित कुल वार्षिक पारिवारिक आय (अंकों और शब्दों में)",
            "आकलन वित्तीय वर्ष एवं वैधता अवधि (मध्य प्रदेश में सामान्यतः 3 वर्ष)",
            "डिजिटल हस्ताक्षर, मुहर और ऑनलाइन सत्यापन क्यूआर कोड"
        ],
        required_for_application_en=[
            "Aadhaar Card of the applicant",
            "Ration Card or Samagra Family ID (in Madhya Pradesh)",
            "Self-declaration affidavit of annual income",
            "Salary slip / Form 16 (for salaried) or Patwari report (for agricultural income)",
            "Electricity bill or local residence proof"
        ],
        required_for_application_hi=[
            "आवेदक का आधार कार्ड",
            "राशन कार्ड अथवा समग्र परिवार आईडी (मध्य प्रदेश में)",
            "वार्षिक आय का स्व-घोषणा शपथ पत्र",
            "वेतन पर्ची (वेतनभोगियों के लिए) अथवा पटवारी जांच आख्या (कृषि आय के लिए)",
            "बिजली बिल या स्थानीय निवास प्रमाण"
        ],
        application_steps_en=[
            "Step 1: Visit the official state portal (MP: mpedistrict.gov.in) or your nearest Lok Seva Kendra / CSC.",
            "Step 2: Fill in the applicant profile, family member count, and declared income sources.",
            "Step 3: Upload Aadhaar card copy and the self-attested income declaration form.",
            "Step 4: Submit application and receive an acknowledgment receipt with an RS/Application tracking number.",
            "Step 5: The Tehsildar verifies the application. Once approved (within 3 to 7 working days), download the digitally signed certificate online."
        ],
        application_steps_hi=[
            "चरण 1: राज्य ई-डिस्ट्रिक्ट पोर्टल (एमपी: mpedistrict.gov.in) पर जाएं अथवा निकटतम लोक सेवा केंद्र (CSC) जाएं।",
            "चरण 2: आवेदक की जानकारी, पारिवारिक सदस्यों की संख्या और आय के स्रोत दर्ज करें।",
            "चरण 3: आधार कार्ड और स्व-घोषणा पत्र संलग्न करें।",
            "चरण 4: आवेदन जमा कर पावती रसीद (RS नंबर) प्राप्त करें।",
            "चरण 5: तहसीलदार द्वारा सत्यापन के बाद (3 से 7 कार्य दिवस में) डिजिटल हस्ताक्षरित प्रमाण पत्र ऑनलाइन डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="certificate",
            holder_name="JOHN DOE",
            document_number="MP/INC/2026/89421",
            issuing_authority="Office of the Tehsildar, Sehore, Madhya Pradesh",
            key_fields={
                "Applicant Name": "JOHN DOE",
                "Father / Guardian": "RICHARD DOE",
                "Annual Family Income": "₹ 65,000 (Rupees Sixty-Five Thousand Only)",
                "Village / Tehsil": "Bhopal Rural, Madhya Pradesh",
                "Issued Date": "15-JAN-2026",
                "Valid Upto": "14-JAN-2029 (3 Financial Years)"
            }
        ),
        apply_url="https://mpedistrict.gov.in/",
        is_online_available=True,
        application_mode_note_en="Can be applied 100% online through MP e-District or offline at Lok Seva Kendras / Tehsil offices.",
        application_mode_note_hi="मध्य प्रदेश ई-डिस्ट्रिक्ट पोर्टल से पूर्णतः ऑनलाइन या लोक सेवा केंद्र / तहसील कार्यालय से ऑफलाइन आवेदन किया जा सकता है।",
        issuing_authority_note_en="Madhya Pradesh: Public Service Management Department (mpedistrict.gov.in); Other states: State e-District portal.",
        issuing_authority_note_hi="मध्य प्रदेश: लोक सेवा प्रबंधन विभाग (mpedistrict.gov.in); अन्य राज्य: राज्य ई-डिस्ट्रिक्ट पोर्टल।"
    ),

    "domicile_certificate": DocumentDefinition(
        id="domicile_certificate",
        aliases=["mp_domicile", "mh_domicile_15years", "niwas_praman_patra", "mool_niwas"],
        name_en="Domicile / Permanent Residence Certificate",
        name_hi="मूल निवास प्रमाण पत्र (Domicile Certificate)",
        category="Residence",
        short_explanation_en="A legal document proving that a citizen is a permanent resident of a specific Indian state or Union Territory.",
        short_explanation_hi="एक वैधानिक प्रमाण पत्र जो सिद्ध करता है कि नागरिक किसी विशिष्ट भारतीय राज्य या केंद्र शासित प्रदेश का स्थायी मूल निवासी है।",
        why_schemes_ask_en="State-sponsored schemes (such as MMVY and Ladli Behna in MP, or Sanjay Gandhi Niradhar in MH) utilize state exchequer funds exclusively for their own residents. Domicile proof prevents non-residents from claiming state-only benefits.",
        why_schemes_ask_hi="राज्य प्रायोजित योजनाएं (जैसे एमपी में MMVY, लाड़ली बहना या महाराष्ट्र में संजय गांधी निराधार) केवल राज्य के मूल निवासियों के लिए होती हैं। यह प्रमाण पत्र राज्य पात्रता सुनिश्चित करता है।",
        issuer_en="Sub-Divisional Officer (Civil) / Tehsildar / District Magistrate",
        issuer_hi="अनुविभागीय अधिकारी (नागरिक) / तहसीलदार / जिला मजिस्ट्रेट",
        contents_en=[
            "Citizen full legal name and parent/spouse name",
            "Permanent address with district, tehsil, and pin code",
            "Duration of residence in the state (e.g., continuous residence since birth or 10-15+ years)",
            "Designation of issuing magistrate and official digital seal"
        ],
        contents_hi=[
            "नागरिक का पूरा नाम और पिता/पति का नाम",
            "स्थायी पता, जिला, तहसील और पिन कोड",
            "राज्य में निवास की अवधि (जैसे जन्म से अथवा 10-15 वर्ष से निरंतर निवास)",
            "जारीकर्ता अधिकारी के डिजिटल हस्ताक्षर एवं पदमुहर"
        ],
        required_for_application_en=[
            "Aadhaar Card / Voter ID",
            "School Leaving Certificate (TC) or 10th marksheet showing study in the state",
            "Parents' domicile certificate or land registry / property tax receipt",
            "Continuous 10-15 year residence proof (electricity bills, voter list extract)",
            "Samagra ID (in MP)"
        ],
        required_for_application_hi=[
            "आधार कार्ड / वोटर आईडी",
            "स्कूल छोड़ने का प्रमाण पत्र (TC) या 10वीं की अंकसूची (राज्य में पढ़ाई का प्रमाण)",
            "माता-पिता का निवास प्रमाण पत्र अथवा जमीन की रजिस्ट्री / हाउस टैक्स रसीद",
            "10 से 15 वर्षों के निवास का प्रमाण (बिजली बिल, मतदाता सूची की प्रति)",
            "समग्र आईडी (मध्य प्रदेश में)"
        ],
        application_steps_en=[
            "Step 1: Open the state service portal (e.g. mpedistrict.gov.in for MP or aaplesarkar.mahaonline.gov.in for MH).",
            "Step 2: Choose 'Domicile / Resident Certificate' (मूल निवास प्रमाण पत्र).",
            "Step 3: Attach educational or land records establishing continuous residence.",
            "Step 4: Submit self-declaration form and pay nominal government portal fee (₹0 - ₹30).",
            "Step 5: Receive digitally signed certificate with verifiable barcode within 7 working days."
        ],
        application_steps_hi=[
            "चरण 1: राज्य सेवा पोर्टल (एमपी: mpedistrict.gov.in, महाराष्ट्र: aaplesarkar.mahaonline.gov.in) पर जाएं।",
            "चरण 2: 'स्थानीय मूल निवासी प्रमाण पत्र' सेवा चुनें।",
            "चरण 3: निरंतर निवास सिद्ध करने वाले शैक्षणिक या राजस्व दस्तावेज अपलोड करें।",
            "चरण 4: स्व-घोषणा पत्र जमा कर आवेदन सबमिट करें।",
            "चरण 5: 7 कार्य दिवसों में बारकोड युक्त डिजिटल प्रमाण पत्र डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="certificate",
            holder_name="JOHN DOE",
            document_number="MP/DOM/2026/33102",
            issuing_authority="Office of the Sub-Divisional Officer (Civil), MP",
            key_fields={
                "Citizen Name": "JOHN DOE",
                "Father's Name": "RICHARD DOE",
                "Residential Status": "Permanent Resident of Madhya Pradesh (Since Birth)",
                "District": "Sehore, Madhya Pradesh",
                "Verification Barcode": "MP-LOK-SEVA-88219"
            }
        ),
        apply_url="https://mpedistrict.gov.in/",
        is_online_available=True,
        application_mode_note_en="Online via MP e-District; physical assistance available at Lok Seva Kendra.",
        application_mode_note_hi="एमपी ई-डिस्ट्रिक्ट से ऑनलाइन अथवा लोक सेवा केंद्र पर जाकर आसानी से बनवाया जा सकता है।",
        issuing_authority_note_en="Lok Seva Management / Revenue Department (MP: mpedistrict.gov.in).",
        issuing_authority_note_hi="लोक सेवा प्रबंधन एवं राजस्व विभाग, मध्य प्रदेश।"
    ),

    "caste_certificate": DocumentDefinition(
        id="caste_certificate",
        aliases=["caste_cert", "jati_praman_patra", "sc_st_obc_certificate"],
        name_en="Caste / Community Certificate (SC / ST / OBC / EWS)",
        name_hi="जाति प्रमाण पत्र (Caste Certificate - SC/ST/OBC/EWS)",
        category="Identity",
        short_explanation_en="A government certificate validating a citizen's belonging to a Scheduled Caste (SC), Scheduled Tribe (ST), Other Backward Class (OBC), or Economically Weaker Section (EWS).",
        short_explanation_hi="एक सरकारी प्रमाण पत्र जो यह सत्यापित करता है कि नागरिक अनुसूचित जाति (SC), अनुसूचित जनजाति (ST), अन्य पिछड़ा वर्ग (OBC) अथवा EWS श्रेणी से संबंधित है।",
        why_schemes_ask_en="Affirmative action programs, reservation benefits, targeted educational fee waivers, and social welfare pensions require verified proof of affirmative social category.",
        why_schemes_ask_hi="आरक्षण लाभ, विशेष छात्रवृत्तियां और लक्षित सामाजिक सुरक्षा योजनाओं के लिए आरक्षित वर्ग का आधिकारिक सत्यापन आवश्यक होता है।",
        issuer_en="Sub-Divisional Magistrate (SDM) / Tehsildar / District Welfare Officer",
        issuer_hi="अनुविभागीय अधिकारी (राजस्व) / तहसीलदार / जिला कल्याण अधिकारी",
        contents_en=[
            "Applicant full name and parentage",
            "Specific caste / sub-caste name as specified in Presidential Orders",
            "Constitutional category (SC, ST, OBC, or EWS)",
            "Creamy layer non-inclusion declaration (for OBC applicants)",
            "Issuing authority seal and digital signature"
        ],
        contents_hi=[
            "आवेदक का पूरा नाम और माता-पिता का नाम",
            "संवैधानिक आदेशों में सूचीबद्ध विशिष्ट जाति/उपजाति का नाम",
            "श्रेणी (अनुसूचित जाति, अनुसूचित जनजाति, अन्य पिछड़ा वर्ग या ईडब्ल्यूएस)",
            "क्रीमी लेयर में न होने का प्रमाण (ओबीसी आवेदकों के लिए)",
            "डिजिटल हस्ताक्षर और सक्षम प्राधिकारी की मुहर"
        ],
        required_for_application_en=[
            "Aadhaar Card of the applicant",
            "Pre-1950 (for SC/ST) or pre-1984 (for OBC) family caste record or father's/blood relative's caste certificate",
            "School Transfer Certificate (TC) or birth record showing caste",
            "Patwari verification report or Gram Sabha recommendation",
            "Passport-sized photograph"
        ],
        required_for_application_hi=[
            "आवेदक का आधार कार्ड",
            "पिता अथवा रक्त संबंधी का पहले से जारी जाति प्रमाण पत्र या पुराना राजस्व रिकॉर्ड",
            "स्कूल टीसी या जन्म प्रमाण पत्र जिसमें जाति दर्ज हो",
            "पटवारी पंचनामा / ग्राम सभा प्रस्ताव",
            "पासपोर्ट साइज फोटो"
        ],
        application_steps_en=[
            "Step 1: Access the state e-District portal (e.g., mpedistrict.gov.in) or visit local Tehsil Lok Seva Kendra.",
            "Step 2: Choose SC/ST or OBC/EWS Caste Certificate service.",
            "Step 3: Enter paternal lineage and upload father's caste certificate or old land revenue records.",
            "Step 4: Submit application; local Revenue Inspector conducts verification.",
            "Step 5: Approved certificate is issued permanently (SC/ST lifetime validity; OBC non-creamy layer certificate renewed every 3 years)."
        ],
        application_steps_hi=[
            "चरण 1: राज्य ई-डिस्ट्रिक्ट पोर्टल (mpedistrict.gov.in) पर जाएं या तहसील लोक सेवा केंद्र जाएं।",
            "चरण 2: अनुसूचित जाति/जनजाति या पिछड़ा वर्ग जाति प्रमाण पत्र सेवा चुनें।",
            "चरण 3: वंशावली विवरण भरें और पिता का जाति प्रमाण पत्र या पुराना रिकॉर्ड अपलोड करें।",
            "चरण 4: राजस्व निरीक्षक द्वारा जांच के बाद प्रमाण पत्र स्वीकृत होता है।",
            "चरण 5: एससी/एसटी हेतु आजीवन वैध प्रमाण पत्र जारी होता है (ओबीसी नॉन-क्रीमी लेयर 3 वर्ष हेतु मान्य)।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="certificate",
            holder_name="JOHN DOE",
            document_number="MP/CST/2026/19402",
            issuing_authority="Office of the Sub-Divisional Magistrate, MP",
            key_fields={
                "Beneficiary Name": "JOHN DOE",
                "Father's Name": "RICHARD DOE",
                "Recognized Caste": "Recognized Community",
                "Category": "Scheduled Tribe (ST) / Other Backward Class (OBC)",
                "Statutory Validity": "Permanent (Life-Time)"
            }
        ),
        apply_url="https://mpedistrict.gov.in/",
        is_online_available=True,
        application_mode_note_en="Apply online on state e-District portal or at Lok Seva Kendra with family lineage proof.",
        application_mode_note_hi="राज्य ई-डिस्ट्रिक्ट पोर्टल या लोक सेवा केंद्र से वंशावली साक्ष्य प्रस्तुत कर आवेदन करें।",
        issuing_authority_note_en="MP Public Service Management / Social Welfare Dept (mpedistrict.gov.in).",
        issuing_authority_note_hi="लोक सेवा प्रबंधन एवं सामाजिक न्याय विभाग, मध्य प्रदेश।"
    ),

    "aadhaar": DocumentDefinition(
        id="aadhaar",
        aliases=["aadhaar_card", "uidai_aadhaar"],
        name_en="Aadhaar Card",
        name_hi="आधार कार्ड (Aadhaar Card)",
        category="Identity",
        short_explanation_en="A 12-digit unique biometric identity number issued by the Unique Identification Authority of India (UIDAI) to every Indian resident.",
        short_explanation_hi="भारतीय विशिष्ट पहचान प्राधिकरण (UIDAI) द्वारा प्रत्येक भारतीय निवासी को जारी किया जाने वाला 12-अंकों का बायोमेट्रिक पहचान पत्र।",
        why_schemes_ask_en="Universal identity foundation for government welfare in India. It enables Direct Benefit Transfer (DBT), prevents duplicate claims, and facilitates paperless e-KYC.",
        why_schemes_ask_hi="भारत में सरकारी कल्याणकारी योजनाओं की रीढ़। यह बैंक में सीधे सब्सिडी (DBT) भेजने, फर्जीवाड़े को रोकने और त्वरित ई-केवाईसी हेतु अनिवार्य है।",
        issuer_en="Unique Identification Authority of India (UIDAI)",
        issuer_hi="भारतीय विशिष्ट पहचान प्राधिकरण (UIDAI), भारत सरकार",
        contents_en=[
            "12-digit unique Aadhaar number (e.g. XXXX XXXX 1234)",
            "Full legal name, gender, and photograph",
            "Exact Date of Birth (DOB) and registered residential address",
            "Secure QR code containing cryptographically signed demographic and biometric hashes"
        ],
        contents_hi=[
            "12 अंकों का विशिष्ट आधार क्रमांक",
            "पूरा नाम, लिंग एवं रंगीन फोटो",
            "सटीक जन्म तिथि और पंजीकृत स्थायी पता",
            "डिजिटल हस्ताक्षरित सुरक्षित क्यूआर कोड"
        ],
        required_for_application_en=[
            "Proof of Identity (POI): Voter ID, Passport, PAN Card, or Ration Card",
            "Proof of Address (POA): Electricity bill, Water bill, or Domicile certificate",
            "Proof of Date of Birth (DOB): Birth certificate or school marksheet",
            "Live biometric capture (fingerprints, iris scan, and facial photo)"
        ],
        required_for_application_hi=[
            "पहचान का प्रमाण (वोटर आईडी, पैन कार्ड, राशन कार्ड या स्कूल आईडी)",
            "पते का प्रमाण (बिजली बिल, पानी का बिल, निवास प्रमाण पत्र या बैंक पासबुक)",
            "जन्म तिथि प्रमाण (जन्म प्रमाण पत्र या 10वीं की अंकसूची)",
            "प्रत्यक्ष बायोमेट्रिक (उंगलियों के निशान, आंख की पुतली और फोटो)"
        ],
        application_steps_en=[
            "Step 1: Book an appointment online on myaadhaar.uidai.gov.in or visit any authorized Aadhaar Seva Kendra / Post Office / Bank.",
            "Step 2: Submit enrollment form along with identity and address proofs.",
            "Step 3: Provide biometric scan (all 10 fingerprints, both iris scans, and photograph).",
            "Step 4: Collect Enrollment Slip containing 28-digit Enrollment ID (EID).",
            "Step 5: Track status on myaadhaar.uidai.gov.in. Once generated, download electronic e-Aadhaar PDF."
        ],
        application_steps_hi=[
            "चरण 1: myaadhaar.uidai.gov.in पर ऑनलाइन अप्वाइंटमेंट बुक करें या नजदीकी आधार केंद्र/डाकघर जाएं।",
            "चरण 2: नामांकन फॉर्म भरकर पहचान व पते का प्रमाण प्रस्तुत करें।",
            "चरण 3: बायोमेट्रिक विवरण (10 उंगलियां, आंखें और चेहरा) दर्ज कराएं।",
            "चरण 4: 28 अंकों की नामांकन आईडी (EID) वाली पावती पर्ची प्राप्त करें।",
            "चरण 5: आधार बनने के बाद myaadhaar.uidai.gov.in से ई-आधार पीडीएफ डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="id_card",
            holder_name="JOHN DOE",
            document_number="XXXX XXXX 1234",
            issuing_authority="Unique Identification Authority of India (UIDAI)",
            key_fields={
                "Name": "JOHN DOE",
                "DOB": "01/01/1990",
                "Gender": "Male / Purush",
                "Aadhaar No": "XXXX XXXX 1234",
                "e-KYC Status": "Active & Mobile Linked"
            }
        ),
        apply_url="https://myaadhaar.uidai.gov.in/",
        is_online_available=False,
        application_mode_note_en="New enrollment requires an in-person visit to an Aadhaar Seva Kendra for biometrics. Address updates and e-Aadhaar downloads can be done 100% online.",
        application_mode_note_hi="नया आधार बनवाने हेतु बायोमेट्रिक के लिए आधार सेवा केंद्र जाना अनिवार्य है। पता अपडेट व ई-आधार डाउनलोड ऑनलाइन संभव है।",
        issuing_authority_note_en="UIDAI, Ministry of Electronics & IT (myaadhaar.uidai.gov.in / Helpline: 1947).",
        issuing_authority_note_hi="UIDAI, इलेक्ट्रॉनिक्स और आईटी मंत्रालय (हेल्पलाइन: 1947)।"
    ),

    "bank_passbook": DocumentDefinition(
        id="bank_passbook",
        aliases=["bank_account", "bank_account_seeded", "npci_dbt_account"],
        name_en="Bank Passbook / Aadhaar-NPCI DBT Account Proof",
        name_hi="बैंक पासबुक (आधार एनपीसीआई / डीबीटी सक्रिय)",
        category="Revenue",
        short_explanation_en="A physical or digital bank statement showing account ownership, branch IFSC, and active Aadhaar-NPCI mapping for Direct Benefit Transfer (DBT).",
        short_explanation_hi="बैंक खाते का विवरण (पासबुक या खाता विवरण) जिसमें खाता क्रमांक, आईएफएससी कोड और सरकारी सब्सिडी सीधे पाने हेतु आधार-एनपीसीआई मैपिंग दर्ज हो।",
        why_schemes_ask_en="Government financial grants (PM-KISAN ₹6,000, Ladli Behna ₹1,250/month, MMVY tuition fees, pensions) are disbursed solely via Direct Benefit Transfer (DBT). If an account is not seeded with Aadhaar on the NPCI mapper, payments fail.",
        why_schemes_ask_hi="पीएम किसान, लाड़ली बहना, छात्रवृत्ति और सामाजिक सुरक्षा पेंशन का पैसा सीधे बैंक खाते में (DBT) भेजा जाता है। इसके लिए बैंक खाता एनपीसीआई से सक्रिय होना अनिवार्य है।",
        issuer_en="Public Sector / Scheduled Commercial Bank / India Post Payments Bank",
        issuer_hi="राष्ट्रीयकृत बैंक / क्षेत्रीय ग्रामीण बैंक / डाकघर बैंक",
        contents_en=[
            "Account holder legal name matching Aadhaar",
            "Account number and Bank Customer ID (CIF)",
            "Branch 11-character IFSC code and MICR code",
            "Aadhaar seeding / NPCI mandate confirmation stamp"
        ],
        contents_hi=[
            "खाताधारक का पूरा नाम (जो आधार से मेल खाता हो)",
            "बैंक खाता क्रमांक एवं सीआईएफ नंबर",
            "शाखा का 11-अक्षरों का IFSC कोड",
            "आधार सीडिंग एवं डीबीटी सक्रियता की स्थिति"
        ],
        required_for_application_en=[
            "Aadhaar Card",
            "PAN Card or Form 60",
            "Recent passport-sized photographs",
            "Completed bank account opening form and Aadhaar NPCI DBT Consent Form"
        ],
        required_for_application_hi=[
            "आधार कार्ड",
            "पैन कार्ड अथवा फॉर्म 60",
            "पासपोर्ट साइज फोटो",
            "बैंक खाता खोलने का फॉर्म एवं आधार एनपीसीआई डीबीटी सहमति प्रपत्र"
        ],
        application_steps_en=[
            "Step 1: Open an account at any public sector bank, rural bank, or Post Office (IPPB).",
            "Step 2: Submit the 'Aadhaar NPCI DBT Mandate' form to link your account on the NPCI mapper.",
            "Step 3: Ensure your account is regular/active (make a small transaction of ₹100).",
            "Step 4: Check DBT seeding status online via myaadhaar.uidai.gov.in ('Bank Seeding Status').",
            "Step 5: Get passbook front page printed clearly showing Name, Account Number, and IFSC."
        ],
        application_steps_hi=[
            "चरण 1: किसी भी सरकारी बैंक, ग्रामीण बैंक या डाकघर (IPPB) में बचत खाता खोलें।",
            "चरण 2: बैंक शाखा में 'आधार एनपीसीआई डीबीटी सहमति प्रपत्र' भरकर जमा करें।",
            "चरण 3: खाते में छोटा लेनदेन (जैसे ₹100) कर सुनिश्चित करें कि खाता सक्रिय है।",
            "चरण 4: myaadhaar.uidai.gov.in पर जाकर 'Bank Seeding Status' जांचें।",
            "चरण 5: पासबुक के पहले पन्ने की स्पष्ट फोटो या प्रिंट प्राप्त करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="passbook",
            holder_name="JOHN DOE",
            document_number="A/C: 9182XXXX3401",
            issuing_authority="State Bank of India / Scheduled Commercial Bank",
            key_fields={
                "Account Holder": "JOHN DOE",
                "Account Number": "9182XXXX3401",
                "IFSC Code": "SBIN0001234",
                "Branch": "Main Branch, Bhopal",
                "DBT Status": "Aadhaar NPCI Mapped (Active)"
            }
        ),
        apply_url="https://www.npci.org.in/",
        is_online_available=False,
        application_mode_note_en="Requires visiting a local bank branch or India Post Payments Bank (IPPB) to submit the Aadhaar NPCI DBT mandate form.",
        application_mode_note_hi="बैंक शाखा अथवा नजदीकी डाकघर जाकर आधार डीबीटी मैपिंग फॉर्म जमा करना होता है।",
        issuing_authority_note_en="Your banking institution / National Payments Corporation of India (npci.org.in).",
        issuing_authority_note_hi="संबंधित बैंक शाखा एवं भारतीय राष्ट्रीय भुगतान निगम (NPCI)।"
    ),

    "birth_certificate": DocumentDefinition(
        id="birth_certificate",
        aliases=["birth_cert", "janam_praman_patra"],
        name_en="Birth Certificate",
        name_hi="जन्म प्रमाण पत्र (Birth Certificate)",
        category="Identity",
        short_explanation_en="A vital statutory record documenting the birth of a child, issued by the Registrar of Births and Deaths under the Registration of Births and Deaths Act, 1969.",
        short_explanation_hi="जन्म-मृत्यु पंजीकरण अधिनियम 1969 के तहत जन्म एवं मृत्यु रजिस्ट्रार द्वारा जारी आधिकारिक जन्म प्रमाण पत्र।",
        why_schemes_ask_en="Statutory age verification for child nutrition programs, school admissions, ladli laxmi schemes, and establishing date of birth across all welfare schemes.",
        why_schemes_ask_hi="बाल कल्याण योजनाओं, लाड़ली लक्ष्मी योजना, स्कूल प्रवेश और सरकारी योजनाओं में जन्म तिथि के सबसे पुख्ता वैधानिक प्रमाण हेतु आवश्यक है।",
        issuer_en="Registrar of Births and Deaths / Municipal Corporation / Gram Panchayat",
        issuer_hi="जन्म एवं मृत्यु रजिस्ट्रार / नगर निगम / ग्राम पंचायत कार्यालय",
        contents_en=[
            "Child's full name, gender, and date of birth",
            "Place of birth (Hospital / Health Center / Home residence)",
            "Mother's and Father's full names and Aadhaar numbers",
            "Registration number and official registration date",
            "Registrar signature and digital seal"
        ],
        contents_hi=[
            "बच्चे का नाम, लिंग और सटीक जन्म तिथि",
            "जन्म का स्थान (अस्पताल / प्राथमिक स्वास्थ्य केंद्र / घर)",
            "माता एवं पिता का पूरा नाम और आधार क्रमांक",
            "पंजीकरण संख्या एवं पंजीकरण की तारीख",
            "रजिस्ट्रार के हस्ताक्षर और मुहर"
        ],
        required_for_application_en=[
            "Birth discharge slip from hospital / maternity home",
            "Parents' Aadhaar cards and marriage certificate (if available)",
            "Identity and residence proof of parents",
            "Affidavit (if applying after 21 days or 1 year of birth)"
        ],
        required_for_application_hi=[
            "अस्पताल / प्रसूति गृह से प्राप्त जन्म सूचना पर्ची (डिस्चार्ज स्लिप)",
            "माता-पिता के आधार कार्ड",
            "माता-पिता का निवास प्रमाण",
            "शपथ पत्र (यदि जन्म के 21 दिन या 1 वर्ष बाद आवेदन कर रहे हों)"
        ],
        application_steps_en=[
            "Step 1: If birth occurred in an institutional hospital, registration is initiated automatically.",
            "Step 2: For home births or delayed registration, visit the local Municipal Corporation office or Gram Panchayat within 21 days.",
            "Step 3: Online application available on the Civil Registration System portal (crsorgi.gov.in) or state portals (e.g. mpedistrict.gov.in).",
            "Step 4: Registrar verifies records and enters birth details in the civil register.",
            "Step 5: Download Form-5 Birth Certificate with QR code online or collect hardcopy."
        ],
        application_steps_hi=[
            "चरण 1: अस्पताल में जन्म होने पर अस्पताल द्वारा सीधे पंजीकरण दर्ज किया जाता है।",
            "चरण 2: घरेलू जन्म के मामले में 21 दिनों के भीतर नगर निगम या ग्राम पंचायत में सूचना दें।",
            "चरण 3: राष्ट्रीय नागरिक पंजीकरण पोर्टल (crsorgi.gov.in) अथवा राज्य पोर्टल पर ऑनलाइन आवेदन करें।",
            "चरण 4: रजिस्ट्रार द्वारा विवरण सत्यापित होने पर प्रपत्र-5 जन्म प्रमाण पत्र जारी होता है।",
            "चरण 5: ऑनलाइन पोर्टल से क्यूआर कोड युक्त प्रमाण पत्र डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="certificate",
            holder_name="JOHN DOE",
            document_number="CRS/BIRTH/2026/04128",
            issuing_authority="Office of the Registrar of Births & Deaths, Municipal Corporation",
            key_fields={
                "Child Name": "JOHN DOE",
                "Date of Birth": "12-MAY-2005",
                "Place of Birth": "District Hospital, Sehore",
                "Mother's Name": "JANE DOE",
                "Father's Name": "RICHARD DOE"
            }
        ),
        apply_url="https://crsorgi.gov.in/",
        is_online_available=True,
        application_mode_note_en="Apply online on crsorgi.gov.in or locally at your Nagar Nigam / Gram Panchayat office.",
        application_mode_note_hi="नागरिक पंजीकरण पोर्टल (crsorgi.gov.in) पर ऑनलाइन या नगर निगम/ग्राम पंचायत में ऑफलाइन उपलब्ध।",
        issuing_authority_note_en="Office of the Registrar General of India (crsorgi.gov.in) / Local Urban Body.",
        issuing_authority_note_hi="भारत का महारजिस्ट्रार कार्यालय (crsorgi.gov.in) एवं स्थानीय निकाय।"
    ),

    "ration_card": DocumentDefinition(
        id="ration_card",
        aliases=["bpl_ration_card", "nfsa_card", "antyodaya_card"],
        name_en="Ration Card (NFSA / BPL / Antyodaya)",
        name_hi="राशन कार्ड (बीपीएल / अंत्योदय / खाद्य सुरक्षा कार्ड)",
        category="Social Security",
        short_explanation_en="A state-issued document entitling households to purchase subsidized foodgrains under the National Food Security Act (NFSA) and serving as proof of poverty/family composition.",
        short_explanation_hi="राष्ट्रीय खाद्य सुरक्षा अधिनियम (NFSA) के तहत रियायती खाद्यान्न प्राप्त करने और परिवार की गरीबी रेखा (BPL/AAY) स्थिति प्रमाणित करने वाला सरकारी कार्ड।",
        why_schemes_ask_en="Used as benchmark eligibility proof for housing (PMAY-G), free healthcare (Ayushman Bharat PM-JAY), and social security widow pensions (IGNWPS).",
        why_schemes_ask_hi="पीएम आवास ग्रामीण, आयुष्मान भारत (₹5 लाख फ्री इलाज) और इंदिरा गांधी राष्ट्रीय पेंशन योजनाओं में बीपीएल/गरीबी रेखा का प्राथमिक आधार राशन कार्ड होता है।",
        issuer_en="Department of Food, Civil Supplies and Consumer Protection",
        issuer_hi="खाद्य, नागरिक आपूर्ति एवं उपभोक्ता संरक्षण विभाग",
        contents_en=[
            "Unique Ration Card Number and scheme entitlement category (BPL / AAY / PHH)",
            "Head of Household (often senior female member as per NFSA norms)",
            "Names, ages, and Aadhaar numbers of all registered family members",
            "Designated Fair Price Shop (FPS) location and monthly grain quota"
        ],
        contents_hi=[
            "विशिष्ट राशन कार्ड क्रमांक एवं श्रेणी (अंत्योदय / बीपीएल / प्राथमिकता परिवार)",
            "परिवार की मुखिया (एनएफएसए के अनुसार परिवार की वरिष्ठ महिला)",
            "परिवार के सभी सदस्यों के नाम, आयु और आधार क्रमांक",
            "उचित मूल्य की दुकान (कोटा) का पता एवं आवंटित खाद्यान्न मात्रा"
        ],
        required_for_application_en=[
            "Aadhaar cards of all family members",
            "Income certificate or BPL survey enrollment slip",
            "Proof of current residential address",
            "Family group photograph",
            "Bank passbook of female head of household"
        ],
        required_for_application_hi=[
            "परिवार के सभी सदस्यों के आधार कार्ड",
            "आय प्रमाण पत्र अथवा बीपीएल सर्वे पर्ची",
            "स्थायी निवास का प्रमाण",
            "परिवार का संयुक्त फोटो",
            "परिवार की महिला मुखिया की बैंक पासबुक"
        ],
        application_steps_en=[
            "Step 1: Check if family is listed in SECC or state BPL survey.",
            "Step 2: Apply online on the state Food Portal (e.g. rationmitra.nic.in in MP or nfsa.gov.in) or visit local Food Supply Office / Gram Panchayat.",
            "Step 3: Attach Aadhaar copies of all household members and income declaration.",
            "Step 4: Food Inspector conducts field inquiry to verify economic condition.",
            "Step 5: Card is sanctioned and digital e-Ration card can be downloaded via DigiLocker or state portal."
        ],
        application_steps_hi=[
            "चरण 1: जांचें कि परिवार बीपीएल सर्वे अथवा खाद्य सुरक्षा पात्रता सूची में है या नहीं।",
            "चरण 2: राज्य खाद्य पोर्टल (एमपी: rationmitra.nic.in, राष्ट्रीय: nfsa.gov.in) पर आवेदन करें या खाद्य आपूर्ति अधिकारी से संपर्क करें।",
            "चरण 3: सभी सदस्यों के आधार कार्ड और आय घोषणा पत्र संलग्न करें।",
            "चरण 4: खाद्य निरीक्षक द्वारा भौतिक सत्यापन किया जाता है।",
            "चरण 5: राशन कार्ड स्वीकृत होने पर डिजिटल ई-राशन कार्ड डाउनलोड किया जा सकता है।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="id_card",
            holder_name="JANE DOE",
            document_number="NFSA/BPL/2026/99120",
            issuing_authority="Dept of Food & Civil Supplies, Madhya Pradesh",
            key_fields={
                "Head of Household": "JANE DOE",
                "Card Type": "Below Poverty Line (BPL) / Priority Household",
                "Registered Members": "4 Members",
                "Fair Price Shop No": "FPS-MP-04-118",
                "Aadhaar e-KYC": "Seeded for all members"
            }
        ),
        apply_url="https://nfsa.gov.in/",
        is_online_available=True,
        application_mode_note_en="Online registration on state food portal (MP: rationmitra.nic.in); physical inquiry conducted by food inspector.",
        application_mode_note_hi="राज्य खाद्य पोर्टल पर ऑनलाइन आवेदन अथवा तहसील खाद्य आपूर्ति कार्यालय से संपर्क करें।",
        issuing_authority_note_en="State Food, Civil Supplies & Consumer Protection Dept / NFSA (nfsa.gov.in).",
        issuing_authority_note_hi="खाद्य, नागरिक आपूर्ति एवं उपभोक्ता संरक्षण विभाग (nfsa.gov.in)।"
    ),

    "land_record": DocumentDefinition(
        id="land_record",
        aliases=["khasra_khatauni", "7_12_extract", "land_ownership_record", "bhulekh"],
        name_en="Land Ownership Records (Khasra / Khatauni / 7-12 Extract)",
        name_hi="भूमि स्वामित्व अभिलेख (खसरा / खतौनी / 7/12 नकल)",
        category="Land",
        short_explanation_en="A statutory land title registry extract demonstrating agricultural or residential landholding acreage, plot boundaries, and ownership shares.",
        short_explanation_hi="एक वैधानिक राजस्व अभिलेख जो कृषि या आवासीय भूमि के स्वामित्व, खसरा क्रमांक, रकबा (क्षेत्रफल) और हिस्सेदारी को प्रमाणित करता है।",
        why_schemes_ask_en="Mandatory for farmer welfare benefits (PM-KISAN ₹6,000, PM Fasal Bima, agricultural subsidies). It proves that the applicant owns cultivable land within permissible acreage ceilings.",
        why_schemes_ask_hi="पीएम किसान सम्मान निधि, फसल बीमा और कृषि अनुदान हेतु अनिवार्य। यह प्रमाणित करता है कि किसान के नाम पर कृषि भूमि दर्ज है।",
        issuer_en="Revenue Department / Directorate of Land Records (Bhulekh / Patwari)",
        issuer_hi="राजस्व विभाग / भू-अभिलेख संचालनालय (भूलेख / पटवारी / तहसीलदार)",
        contents_en=[
            "Land parcel unique Khasra number and Khatauni account number",
            "Acreage / Area in hectares or square meters",
            "Names of all recorded co-owners and respective land shares",
            "Classification of land (cultivable, irrigated, barren, or residential)",
            "Encumbrance / Bank mortgage / loan lien remarks if any"
        ],
        contents_hi=[
            "खसरा क्रमांक और खतौनी खाता संख्या",
            "कुल रकबा (क्षेत्रफल हेक्टेयर या एकड़ में)",
            "भूमि स्वामियों के नाम और उनके हिस्से",
            "भूमि का प्रकार (सिंचित, असिंचित, कृषि योग्य)",
            "बैंक बंधक या किसी ऋण का विवरण"
        ],
        required_for_application_en=[
            "Aadhaar Card of the landowner",
            "Village name, Tehsil, and District",
            "Existing Khasra / Khata number or previous sale deed (Registry copy)",
            "Inheritance mutation order (Namantaran) in case of inherited land"
        ],
        required_for_application_hi=[
            "भूमि स्वामी का आधार कार्ड",
            "गांव का नाम, तहसील और जिला",
            "खसरा या खाता क्रमांक अथवा पुरानी बैनामा (रजिस्ट्री) की प्रति",
            "वारिसाना नामांतरण आदेश (यदि पैतृक भूमि हो)"
        ],
        application_steps_en=[
            "Step 1: Open the state Bhulekh portal (MP: mpbhulekh.gov.in, Maharashtra: bhulekh.mahabhumi.gov.in).",
            "Step 2: Select District -> Tehsil -> Village.",
            "Step 3: Search by Khasra Number, Plot Number, or Landowner Name.",
            "Step 4: View the digital record online for free.",
            "Step 5: For official scheme submission, pay a nominal fee (₹10 - ₹30) on the portal to download a digitally signed certified copy with QR code."
        ],
        application_steps_hi=[
            "चरण 1: राज्य भूलेख पोर्टल (मध्य प्रदेश: mpbhulekh.gov.in, महाराष्ट्र: mahabhumi.gov.in) पर जाएं।",
            "चरण 2: जिला, तहसील और गांव का चयन करें।",
            "चरण 3: खसरा नंबर, खाता नंबर या भू-स्वामी के नाम से खोजें।",
            "चरण 4: अपनी भूमि का रिकॉर्ड ऑनलाइन मुफ्त में देखें।",
            "चरण 5: योजनाओं में लगाने के लिए पोर्टल से मात्र ₹10-30 का शुल्क देकर डिजिटल हस्ताक्षरित एवं प्रमाणित नकल डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="land_record",
            holder_name="JOHN DOE",
            document_number="KHASRA NO: 142/1 • KHATA: 88",
            issuing_authority="Directorate of Land Records, Government of Madhya Pradesh",
            key_fields={
                "Owner Name": "JOHN DOE",
                "Father's Name": "RICHARD DOE",
                "Khasra Number": "142/1",
                "Area (Hectares)": "1.50 Hectares (Cultivable)",
                "Village / Tehsil": "Sehore Rural, Madhya Pradesh",
                "Digital Signature": "Digitally Signed by Revenue Department"
            }
        ),
        apply_url="https://mpbhulekh.gov.in/",
        is_online_available=True,
        application_mode_note_en="100% online on state Bhulekh portal (MP: mpbhulekh.gov.in); certified copies also available from local Patwari or Lok Seva Kendra.",
        application_mode_note_hi="राज्य भूलेख पोर्टल (mpbhulekh.gov.in) से तुरंत डिजिटल प्रमाणित प्रति ऑनलाइन डाउनलोड की जा सकती है।",
        issuing_authority_note_en="Directorate of Land Records, Revenue Dept (mpbhulekh.gov.in).",
        issuing_authority_note_hi="राजस्व विभाग, भू-अभिलेख संचालनालय।"
    ),

    "death_certificate": DocumentDefinition(
        id="death_certificate",
        aliases=["death_certificate_husband", "mrityu_praman_patra"],
        name_en="Husband's Death Certificate",
        name_hi="पति का मृत्यु प्रमाण पत्र (Death Certificate)",
        category="Social Security",
        short_explanation_en="The official civil registration record certifying the death of an individual, issued under the statutory authority of the Registration of Births and Deaths Act.",
        short_explanation_hi="जन्म एवं मृत्यु पंजीकरण अधिनियम के तहत जारी आधिकारिक वैधानिक प्रमाण पत्र जो किसी व्यक्ति के देहांत की पुष्टि करता है।",
        why_schemes_ask_en="Statutory requirement for Indira Gandhi National Widow Pension Scheme (IGNWPS), Sanjay Gandhi Niradhar Yojana, and widow support grants to establish widowhood legally.",
        why_schemes_ask_hi="इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना (IGNWPS), संजय गांधी निराधार योजना और राज्य विधवा सहायता योजनाओं हेतु वैधानिक प्रमाण।",
        issuer_en="Registrar of Births and Deaths / Municipal Corporation / Gram Panchayat",
        issuer_hi="जन्म एवं मृत्यु रजिस्ट्रार / नगर निगम / ग्राम पंचायत कार्यालय",
        contents_en=[
            "Deceased husband's full legal name",
            "Exact date and place of death",
            "Applicant's (wife's) name recorded as informant / spouse",
            "Unique civil death registration number and issuance date",
            "Official seal of the local civil registrar"
        ],
        contents_hi=[
            "दिवंगत पति का पूरा नाम",
            "मृत्यु की सटीक तिथि और स्थान",
            "पत्नी का नाम (आवेदिका) जीवनसाथी के रूप में दर्ज हो",
            "मृत्यु पंजीकरण क्रमांक और जारी करने की तारीख",
            "स्थानीय नागरिक रजिस्ट्रार की आधिकारिक मुहर"
        ],
        required_for_application_en=[
            "Hospital death report / cremation ground receipt / burial certificate",
            "Deceased husband's Aadhaar Card",
            "Wife's Aadhaar Card and Marriage certificate or Joint Ration Card",
            "Self-attested identity proof of the applicant"
        ],
        required_for_application_hi=[
            "अस्पताल की मृत्यु पर्ची अथवा श्मशान घाट/कब्रिस्तान की रसीद",
            "दिवंगत पति का आधार कार्ड",
            "पत्नी का आधार कार्ड एवं विवाह प्रमाण पत्र अथवा संयुक्त राशन कार्ड",
            "आवेदक का पहचान पत्र"
        ],
        application_steps_en=[
            "Step 1: Obtain medical death certificate from the hospital or cremation ground slip.",
            "Step 2: Submit notification to the local Registrar of Births and Deaths (Gram Panchayat or Municipal Corporation) within 21 days.",
            "Step 3: Can also be applied on the Civil Registration System portal (crsorgi.gov.in) or state portals (e.g. mpedistrict.gov.in).",
            "Step 4: Registrar verifies entries against local cremation / medical reports.",
            "Step 5: Form 6 Death Certificate is issued with official verification seal."
        ],
        application_steps_hi=[
            "चरण 1: अस्पताल की मृत्यु पर्ची या श्मशान घाट की रसीद प्राप्त करें।",
            "चरण 2: 21 दिनों के भीतर स्थानीय रजिस्ट्रार (ग्राम पंचायत अथवा नगर निगम) में आवेदन करें।",
            "चरण 3: राष्ट्रीय पोर्टल crsorgi.gov.in या राज्य ई-डिस्ट्रिक्ट पर ऑनलाइन भी आवेदन कर सकते हैं।",
            "चरण 4: रजिस्ट्रार द्वारा सत्यापन के बाद आधिकारिक प्रपत्र-6 मृत्यु प्रमाण पत्र जारी होता है।",
            "चरण 5: ऑनलाइन पोर्टल से क्यूआर कोड युक्त प्रमाण पत्र डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="certificate",
            holder_name="LATE RICHARD DOE",
            document_number="CRS/DTH/2025/11094",
            issuing_authority="Office of the Registrar of Births and Deaths, MP",
            key_fields={
                "Name of Deceased": "LATE RICHARD DOE",
                "Spouse / Wife Name": "JANE DOE",
                "Date of Death": "10-AUG-2025",
                "Place of Death": "Bhopal, Madhya Pradesh",
                "Registration No": "CRS/DTH/2025/11094"
            }
        ),
        apply_url="https://crsorgi.gov.in/",
        is_online_available=True,
        application_mode_note_en="Online through crsorgi.gov.in or state e-District; offline at local Nagar Nigam / Gram Panchayat.",
        application_mode_note_hi="crsorgi.gov.in पर ऑनलाइन या स्थानीय नगर निगम / ग्राम पंचायत कार्यालय से प्राप्त करें।",
        issuing_authority_note_en="Office of the Registrar of Births and Deaths (crsorgi.gov.in) / Urban Local Body.",
        issuing_authority_note_hi="जन्म एवं मृत्यु रजिस्ट्रार कार्यालय एवं स्थानीय निकाय।"
    ),

    "disability_certificate": DocumentDefinition(
        id="disability_certificate",
        aliases=["disability_cert", "divyangjan_card", "udid_card"],
        name_en="Unique Disability ID (UDID) / Disability Certificate",
        name_hi="दिव्यांगता प्रमाण पत्र / यूडीआईडी कार्ड (UDID Card)",
        category="Social Security",
        short_explanation_en="A government-issued national identity card for persons with disabilities (Divyangjan), stating disability type and medical benchmark percentage.",
        short_explanation_hi="दिव्यांगजन सशक्तिकरण विभाग द्वारा जारी राष्ट्रीय विशिष्ट दिव्यांगता पहचान पत्र, जिसमें दिव्यांगता का प्रकार और प्रतिशत दर्ज होता है।",
        why_schemes_ask_en="Government disability pensions, assistive device distributions, transport concessions, and welfare schemes mandate a verified medical board disability certificate with >=40% benchmark disability.",
        why_schemes_ask_hi="दिव्यांग पेंशन, निःशुल्क सहायक उपकरण और विशेष कल्याणकारी योजनाओं हेतु न्यूनतम 40% दिव्यांगता का चिकित्सकीय प्रमाण अनिवार्य होता है।",
        issuer_en="Department of Empowerment of Persons with Disabilities / District Medical Board",
        issuer_hi="दिव्यांगजन सशक्तिकरण विभाग / जिला मेडिकल बोर्ड / मुख्य चिकित्सा अधिकारी (CMO)",
        contents_en=[
            "18-digit unique UDID Number",
            "Applicant full name, photograph, and contact details",
            "Type of Disability (locomotor, visual, hearing, intellectual, etc.)",
            "Percentage of disability certified by the Medical Authority (e.g. 40%, 60%)",
            "Validity (Permanent or Temporary with renewal date)"
        ],
        contents_hi=[
            "18-अंकों का विशिष्ट UDID क्रमांक",
            "दिव्यांगजन का नाम, फोटो और पता",
            "दिव्यांगता का प्रकार (दृष्टिबाधित, अस्थिबाधित, मूक-बधिर आदि)",
            "मेडिकल बोर्ड द्वारा प्रमाणित दिव्यांगता प्रतिशत (जैसे 40% या अधिक)",
            "प्रमाण पत्र की वैधता (स्थायी अथवा अस्थायी)"
        ],
        required_for_application_en=[
            "Aadhaar Card or voter ID of the applicant",
            "Proof of residence",
            "Recent passport-sized photographs showing disability if visible",
            "Previous hospital diagnosis papers or surgical history reports"
        ],
        required_for_application_hi=[
            "आवेदक का आधार कार्ड",
            "स्थायी निवास का प्रमाण",
            "पासपोर्ट साइज रंगीन फोटो",
            "अस्पताल के पुराने इलाज या ऑपरेशन के पर्चे"
        ],
        application_steps_en=[
            "Step 1: Register online on the national UDID portal: swavlambancard.gov.in.",
            "Step 2: Fill personal details, disability details, and upload photo and Aadhaar.",
            "Step 3: Choose nearest District Hospital for medical assessment.",
            "Step 4: Visit the District Hospital on the allotted appointment date for clinical examination by the Medical Board.",
            "Step 5: Once certified, download digital e-UDID card immediately; physical smart card is posted to residential address."
        ],
        application_steps_hi=[
            "चरण 1: राष्ट्रीय स्वावलंबन पोर्टल (swavlambancard.gov.in) पर ऑनलाइन पंजीकरण करें।",
            "चरण 2: व्यक्तिगत जानकारी और दिव्यांगता का प्रकार भरें, फोटो व आधार अपलोड करें।",
            "चरण 3: चिकित्सकीय जांच हेतु निकटतम जिला अस्पताल का चयन करें।",
            "चरण 4: निर्धारित तिथि पर जिला अस्पताल जाकर मेडिकल बोर्ड के समक्ष परीक्षण कराएं।",
            "चरण 5: जांच के बाद ऑनलाइन ई-यूडीआईडी कार्ड डाउनलोड करें; प्लास्टिक कार्ड डाक द्वारा घर आता है।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="id_card",
            holder_name="JOHN DOE",
            document_number="UDID: MP04102928374610",
            issuing_authority="District Medical Board & Dept of Empowerment of Persons with Disabilities",
            key_fields={
                "Cardholder Name": "JOHN DOE",
                "Disability Type": "Locomotor Disability",
                "Disability Percentage": "50% (Benchmark Disability)",
                "Issuing Medical Authority": "Chief Medical Officer (CMO), District Hospital",
                "UDID No": "MP04102928374610"
            }
        ),
        apply_url="https://www.swavlambancard.gov.in/",
        is_online_available=True,
        application_mode_note_en="Apply online on swavlambancard.gov.in; physical medical assessment required at designated District Hospital.",
        application_mode_note_hi="swavlambancard.gov.in पर ऑनलाइन आवेदन, जिसके बाद जिला अस्पताल में मेडिकल बोर्ड द्वारा जांच की जाती है।",
        issuing_authority_note_en="Dept of Empowerment of Persons with Disabilities, Govt of India (swavlambancard.gov.in).",
        issuing_authority_note_hi="दिव्यांगजन सशक्तिकरण विभाग, भारत सरकार (swavlambancard.gov.in)।"
    ),

    "samagra_id": DocumentDefinition(
        id="samagra_id",
        aliases=["samagra_card", "samagra_family_id", "samagra_member_id"],
        name_en="Samagra Family & Member ID (Madhya Pradesh)",
        name_hi="समग्र परिवार एवं सदस्य आईडी (Samagra ID - मध्य प्रदेश)",
        category="Identity",
        short_explanation_en="A unified citizen registry identifier in Madhya Pradesh consisting of an 8-digit family code and a 9-digit member code used for transparent civic welfare delivery.",
        short_explanation_hi="मध्य प्रदेश शासन का एकीकृत नागरिक डेटाबेस कोड जिसमें 8-अंकों का परिवार कोड और 9-अंकों का व्यक्तिगत सदस्य कोड होता है।",
        why_schemes_ask_en="Mandatory for all Madhya Pradesh welfare schemes (Ladli Behna ₹1,250/month, MMVY scholarships, social security pensions, and PDS ration eligibility).",
        why_schemes_ask_hi="मध्य प्रदेश की समस्त योजनाओं (लाड़ली बहना, मेधावी विद्यार्थी MMVY, सामाजिक सुरक्षा पेंशन, राशन) के लिए समग्र आईडी व आधार ई-केवाईसी अनिवार्य है।",
        issuer_en="Samagra Samajik Suraksha Mission, Directorate of Social Justice, MP Government",
        issuer_hi="समग्र सामाजिक सुरक्षा मिशन, सामाजिक न्याय संचालनालय, मध्य प्रदेश शासन",
        contents_en=[
            "8-digit Family ID (परिवार आईडी)",
            "9-digit Individual Member ID (सदस्य आईडी)",
            "Head of Family name, address, and category",
            "Aadhaar e-KYC status and mobile number linkage status",
            "Bank account DBT linkage indicator"
        ],
        contents_hi=[
            "8 अंकों की समग्र परिवार आईडी",
            "9 अंकों की व्यक्तिगत सदस्य आईडी",
            "परिवार के मुखिया का नाम, पता एवं सामाजिक श्रेणी",
            "आधार ई-केवाईसी सत्यापन स्थिति (हाँ/नहीं)",
            "बैंक खाता डीबीटी लिंकेज स्थिति"
        ],
        required_for_application_en=[
            "Aadhaar Card of all household members",
            "Active mobile number linked with Aadhaar for OTP",
            "Bank passbook",
            "Ration Card or Voter ID"
        ],
        required_for_application_hi=[
            "परिवार के सभी सदस्यों के आधार कार्ड",
            "आधार से जुड़ा सक्रिय मोबाइल नंबर (ओटीपी हेतु)",
            "बैंक पासबुक",
            "राशन कार्ड अथवा निवास प्रमाण"
        ],
        application_steps_en=[
            "Step 1: Open the official Samagra Portal: samagra.gov.in.",
            "Step 2: Click on 'Register New Family / Member' (परिवार/सदस्य पंजीकृत करें) or complete 'e-KYC' (ई-केवाईसी करें).",
            "Step 3: Enter your 9-digit Samagra Member ID and Aadhaar Number.",
            "Step 4: Authenticate with Aadhaar OTP sent to your registered mobile phone.",
            "Step 5: Once verified by the local Gram Panchayat Secretary or Ward In-charge, download the Samagra Card PDF."
        ],
        application_steps_hi=[
            "चरण 1: आधिकारिक समग्र पोर्टल samagra.gov.in पर जाएं।",
            "चरण 2: 'समग्र ई-केवाईसी करें' या 'नवीन परिवार/सदस्य पंजीकृत करें' पर क्लिक करें।",
            "चरण 3: अपनी 9 अंकों की सदस्य आईडी और आधार क्रमांक दर्ज करें।",
            "चरण 4: आधार से जुड़े मोबाइल पर आए ओटीपी से सत्यापन पूरा करें।",
            "चरण 5: ग्राम पंचायत सचिव या वार्ड प्रभारी द्वारा अनुमोदन के बाद समग्र कार्ड डाउनलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="id_card",
            holder_name="JOHN DOE",
            document_number="Family: 81094321 • Member: 198452310",
            issuing_authority="Samagra Social Security Mission, Government of MP",
            key_fields={
                "Family ID": "81094321",
                "Member ID": "198452310",
                "Member Name": "JOHN DOE",
                "e-KYC Status": "Completed (पूर्ण)",
                "Bank DBT Seeding": "Yes (सक्रिय)",
                "District": "Sehore, MP"
            }
        ),
        apply_url="https://samagra.gov.in/",
        is_online_available=True,
        application_mode_note_en="100% online on samagra.gov.in with Aadhaar OTP; offline help available at Gram Panchayat or Lok Seva Kendra.",
        application_mode_note_hi="samagra.gov.in पोर्टल पर आधार ओटीपी से पूर्णतः ऑनलाइन; ग्राम पंचायत अथवा लोक सेवा केंद्र से भी संभव।",
        issuing_authority_note_en="Samagra Samajik Suraksha Mission, MP Govt (samagra.gov.in).",
        issuing_authority_note_hi="समग्र सामाजिक सुरक्षा मिशन, मध्य प्रदेश शासन (samagra.gov.in)।"
    ),

    "job_card_mgnrega": DocumentDefinition(
        id="job_card_mgnrega",
        aliases=["mgnrega_card", "nrega_job_card", "job_card"],
        name_en="MGNREGA Job Card",
        name_hi="मनरेगा जॉब कार्ड (MGNREGA Job Card)",
        category="Social Security",
        short_explanation_en="A statutory work entitlement card issued to rural adult citizens guaranteeing 100 days of unskilled wage employment per financial year.",
        short_explanation_hi="ग्रामीण वयस्क नागरिकों को प्रति वित्तीय वर्ष 100 दिनों के अकुशल रोजगार का कानूनी अधिकार प्रदान करने वाला आधिकारिक जॉब कार्ड।",
        why_schemes_ask_en="Required for Pradhan Mantri Awas Yojana - Gramin (PMAY-G) to receive direct financial credit for 90 to 95 days of unskilled construction labor assistance directly to the beneficiary.",
        why_schemes_ask_hi="पीएम आवास योजना ग्रामीण (PMAY-G) के तहत मकान निर्माण हेतु 90-95 दिनों की अकुशल मनरेगा मजदूरी सीधे बैंक खाते में पाने हेतु अनिवार्य है।",
        issuer_en="Ministry of Rural Development / Gram Panchayat Office",
        issuer_hi="ग्रामीण विकास मंत्रालय / ग्राम पंचायत कार्यालय",
        contents_en=[
            "Unique State/District/Block/Panchayat Job Card Number",
            "Names, ages, and genders of registered adult household members",
            "Recorded employment days worked and wage disbursement ledger",
            "Aadhaar-linked bank account number for wage payments"
        ],
        contents_hi=[
            "राज्य, जिला, जनपद एवं ग्राम पंचायत कोड सहित विशिष्ट जॉब कार्ड नंबर",
            "परिवार के पंजीकृत सभी वयस्क सदस्यों के नाम और फोटो",
            "किए गए कार्य दिवसों और मजदूरी भुगतान का आधिकारिक रिकॉर्ड",
            "मजदूरी जमा होने वाला आधार-सीडेड बैंक खाता"
        ],
        required_for_application_en=[
            "Aadhaar Card of all adult applicants in the rural household",
            "Passport-sized photograph of family members",
            "Proof of residence in the Gram Panchayat",
            "Bank passbook details with Aadhaar seeding"
        ],
        required_for_application_hi=[
            "ग्रामीण परिवार के सभी वयस्क सदस्यों के आधार कार्ड",
            "परिवार के सदस्यों की पासपोर्ट साइज फोटो",
            "ग्राम पंचायत में स्थायी निवास का प्रमाण",
            "बैंक पासबुक की प्रति (आधार सीडेड)"
        ],
        application_steps_en=[
            "Step 1: Submit a simple written application or Form 1 to the local Gram Panchayat Secretary (Sachiv) or Gram Rozgar Sahayak (GRS).",
            "Step 2: Panchayat conducts door-to-door verification to register adult members willing to do unskilled manual work.",
            "Step 3: Data is entered on the national nrega.nic.in database.",
            "Step 4: Laminated Job Card is issued within 15 days of application completely free of cost.",
            "Step 5: View or verify your digital Job Card on nrega.nic.in."
        ],
        application_steps_hi=[
            "चरण 1: ग्राम पंचायत सचिव अथवा ग्राम रोजगार सहायक (GRS) को प्रपत्र-1 में सादे कागज पर आवेदन दें।",
            "चरण 2: पंचायत द्वारा सत्यापन कर वयस्क सदस्यों का नाम दर्ज किया जाता है।",
            "चरण 3: nrega.nic.in पोर्टल पर जॉब कार्ड की प्रविष्टि होती है।",
            "चरण 4: आवेदन के 15 दिनों के भीतर ग्राम पंचायत द्वारा निःशुल्क जॉब कार्ड जारी किया जाता है।",
            "चरण 5: nrega.nic.in पोर्टल पर जाकर अपना जॉब कार्ड नंबर कभी भी देखा जा सकता है।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="id_card",
            holder_name="JOHN DOE",
            document_number="MP-04-002-019/3321",
            issuing_authority="Gram Panchayat / Ministry of Rural Development",
            key_fields={
                "Head of Household": "JOHN DOE",
                "Job Card Number": "MP-04-002-019/3321",
                "Panchayat": "Gram Panchayat Sehore Rural",
                "Bank Account Linked": "Yes (DBT Active)",
                "Guaranteed Days": "100 Days Unskilled Labor"
            }
        ),
        apply_url="https://nrega.nic.in/",
        is_online_available=False,
        application_mode_note_en="Issued locally and free of charge by your Gram Panchayat office within 15 days of applying.",
        application_mode_note_hi="ग्राम पंचायत कार्यालय में सचिव या रोजगार सहायक द्वारा 15 दिनों में निःशुल्क बनाया जाता है।",
        issuing_authority_note_en="Ministry of Rural Development / Local Gram Panchayat (nrega.nic.in).",
        issuing_authority_note_hi="ग्रामीण विकास मंत्रालय एवं स्थानीय ग्राम पंचायत (nrega.nic.in)।"
    ),

    "marksheet_12th": DocumentDefinition(
        id="marksheet_12th",
        aliases=["12th_marksheet", "class_12_certificate", "higher_secondary_marksheet"],
        name_en="Class 12th Passing Marksheet & Certificate",
        name_hi="12वीं बोर्ड अंकसूची एवं उत्तीर्ण प्रमाण पत्र (Class 12 Marksheet)",
        category="Education",
        short_explanation_en="Official academic marksheet issued by a recognized education board certifying secondary education completion and subject-wise examination scores.",
        short_explanation_hi="मान्यता प्राप्त शिक्षा मंडल (एमपी बोर्ड, सीबीएसई, आईसीएसई) द्वारा जारी आधिकारिक 12वीं परीक्षा अंकसूची।",
        why_schemes_ask_en="Mandatory for higher education scholarship schemes like Mukhyamantri Medhavi Vidyarthi Yojana (MMVY), where tuition waiver requires >=70% in MP Board or >=85% in CBSE/ICSE.",
        why_schemes_ask_hi="मुख्यमंत्री मेधावी विद्यार्थी योजना (MMVY) जैसी उच्च शिक्षा योजनाओं हेतु अनिवार्य, जहां एमपी बोर्ड में 70%+ या सीबीएसई/आईसीएसई में 85%+ अंक होना अनिवार्य है।",
        issuer_en="Board of Secondary Education (MPBSE / CBSE / ICSE)",
        issuer_hi="माध्यमिक शिक्षा मंडल (MPBSE) / केंद्रीय माध्यमिक शिक्षा बोर्ड (CBSE)",
        contents_en=[
            "Candidate full name, roll number, and center code",
            "Parents' names matching Aadhaar details",
            "Subject-wise marks obtained, practical scores, and total aggregate percentage",
            "Result division / grade and official board seal with DigiLocker verification hash"
        ],
        contents_hi=[
            "परीक्षार्थी का नाम, रोल नंबर एवं केंद्र क्रमांक",
            "माता-पिता का नाम",
            "विषयवार प्राप्तांक, प्रायोगिक अंक और कुल प्रतिशत",
            "उत्तीर्ण श्रेणी और डिजीलॉकर सत्यापन डिजिटल हस्ताक्षर"
        ],
        required_for_application_en=[
            "Class 12 board admit card or roll number",
            "School verification code"
        ],
        required_for_application_hi=[
            "12वीं बोर्ड परीक्षा प्रवेश पत्र या रोल नंबर",
            "संबंधित विद्यालय का रिकॉर्ड"
        ],
        application_steps_en=[
            "Step 1: Collect original printed marksheet from your school after board result declaration.",
            "Step 2: Instant digital copy can be fetched 24/7 on DigiLocker (digilocker.gov.in) using your Aadhaar and roll number.",
            "Step 3: DigiLocker verified digital marksheet is legally recognized under the IT Act for MMVY scholarship application.",
            "Step 4: Upload the clear digital copy on the MP Scholarship Portal (scholarshipportal.mp.nic.in)."
        ],
        application_steps_hi=[
            "चरण 1: परीक्षा परिणाम घोषित होने के बाद अपने विद्यालय से मूल अंकसूची प्राप्त करें।",
            "चरण 2: डिजीलॉकर (digilocker.gov.in) पर आधार और रोल नंबर डालकर तुरंत डिजिटल सत्यापित अंकसूची डाउनलोड करें।",
            "चरण 3: डिजीलॉकर अंकसूची आईटी एक्ट के तहत मूल अंकसूची के समान ही कानूनी रूप से मान्य है।",
            "चरण 4: मध्य प्रदेश छात्रवृत्ति पोर्टल (scholarshipportal.mp.nic.in) पर अपलोड करें।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="marksheet",
            holder_name="JOHN DOE",
            document_number="ROLL NO: 26189042",
            issuing_authority="Madhya Pradesh Board of Secondary Education (MPBSE)",
            key_fields={
                "Candidate Name": "JOHN DOE",
                "Roll Number": "26189042",
                "Examination": "Higher Secondary Certificate (10+2)",
                "Percentage Secured": "86.4% (First Division)",
                "DigiLocker Status": "Digitally Signed & Verified"
            }
        ),
        apply_url="https://www.digilocker.gov.in/",
        is_online_available=True,
        application_mode_note_en="Issued by schools; digital verified copies immediately available anytime via DigiLocker.",
        application_mode_note_hi="स्कूल से प्राप्त करें अथवा डिजीलॉकर (digilocker.gov.in) से तुरंत डिजिटल कॉपी डाउनलोड करें।",
        issuing_authority_note_en="MPBSE (mpbse.nic.in) / CBSE (cbse.gov.in) / DigiLocker (digilocker.gov.in).",
        issuing_authority_note_hi="माध्यमिक शिक्षा मंडल (mpbse.nic.in) एवं डिजीलॉकर।"
    ),

    "admission_fee_receipt": DocumentDefinition(
        id="admission_fee_receipt",
        aliases=["college_fee_receipt", "allotment_letter", "admission_proof"],
        name_en="College Admission Slip & Fee Receipt",
        name_hi="कॉलेज प्रवेश पत्र एवं शुल्क रसीद (Admission Proof)",
        category="Education",
        short_explanation_en="An official enrollment voucher issued by an accredited university or higher education institution certifying student admission into an undergraduate degree course.",
        short_explanation_hi="मान्यता प्राप्त विश्वविद्यालय या उच्च शिक्षण संस्थान द्वारा जारी आधिकारिक प्रवेश पत्र और शुल्क रसीद जो डिग्री पाठ्यक्रम में प्रवेश को प्रमाणित करती है।",
        why_schemes_ask_en="Mukhyamantri Medhavi Vidyarthi Yojana (MMVY) reimburses or pays 100% of the tuition fees directly to the admitted government or recognized private college/university.",
        why_schemes_ask_hi="मेधावी विद्यार्थी योजना (MMVY) के तहत सरकार द्वारा पूरी ट्यूशन फीस कॉलेज को सीधे भुगतान करने हेतु प्रवेश का पुख्ता प्रमाण आवश्यक होता है।",
        issuer_en="Admitted University / Professional College / Central Counseling Committee (DTE/NEET/CLAT)",
        issuer_hi="प्रवेशित विश्वविद्यालय / शासकीय कॉलेज / काउंसलिंग समिति",
        contents_en=[
            "Student legal name, allotment rank, and application ID",
            "Allotted course name (e.g., B.Tech, MBBS, B.A. LL.B., B.Sc)",
            "College affiliation code and official institution bank account",
            "Itemized statutory tuition fee structure payable for the academic year",
            "College Registrar or Principal signature and seal"
        ],
        contents_hi=[
            "छात्र का नाम, काउंसलिंग आवंटन रैंक और आवेदन क्रमांक",
            "आवंटित पाठ्यक्रम (जैसे बीटेक, एमबीबीएस, बीए एलएलबी, बीएससी आदि)",
            "कॉलेज का नाम और संस्था का बैंक खाता विवरण",
            "शैक्षणिक वर्ष हेतु देय ट्यूशन फीस का विवरण",
            "कॉलेज रजिस्ट्रार / प्राचार्य के हस्ताक्षर एवं मुहर"
        ],
        required_for_application_en=[
            "Seat allotment letter from centralized admission authority",
            "College verification letter and fee estimate on institution letterhead",
            "Class 12th marksheet and entrance exam scorecard (JEE/NEET/CLAT)"
        ],
        required_for_application_hi=[
            "काउंसलिंग आवंटन पत्र (Allotment Letter)",
            "कॉलेज के लेटरहेड पर फीस का विवरण (Fee Structure)",
            "12वीं की अंकसूची एवं प्रवेश परीक्षा का स्कोरकार्ड"
        ],
        application_steps_en=[
            "Step 1: Secure admission through centralized merit counseling or direct institutional round.",
            "Step 2: Collect the official Admission Slip and fee receipt from the college finance office.",
            "Step 3: Log in to the MP Scholarship Portal (scholarshipportal.mp.nic.in).",
            "Step 4: Register under MMVY scheme and link your college code and enrollment number.",
            "Step 5: College nodal officer approves verification online, and the fee grant is processed directly."
        ],
        application_steps_hi=[
            "चरण 1: केंद्रीकृत काउंसलिंग अथवा कॉलेज प्रवेश प्रक्रिया के माध्यम से प्रवेश प्राप्त करें।",
            "चरण 2: कॉलेज के लेखा कार्यालय से अधिकृत प्रवेश रसीद एवं फीस का विवरण प्राप्त करें।",
            "चरण 3: मध्य प्रदेश छात्रवृत्ति पोर्टल (scholarshipportal.mp.nic.in) पर लॉग इन करें।",
            "चरण 4: मेधावी विद्यार्थी (MMVY) योजना में कॉलेज कोड और नामांकन क्रमांक दर्ज करें।",
            "चरण 5: कॉलेज नोडल अधिकारी द्वारा ऑनलाइन सत्यापन के बाद फीस का भुगतान स्वीकृत होता है।"
        ],
        sample_preview=DocumentSamplePreview(
            sample_type="certificate",
            holder_name="JOHN DOE",
            document_number="ADM/2026/ENGG/8821",
            issuing_authority="Admitted Institute / University Administration",
            key_fields={
                "Student Name": "JOHN DOE",
                "Enrollment / Allotment No": "ADM/2026/ENGG/8821",
                "Course Enrolled": "Bachelor of Technology (B.Tech - Computer Science)",
                "Tuition Fee Demand": "₹ 1,50,000 (To be reimbursed under MMVY)",
                "College Verification": "Verified by College Registrar"
            }
        ),
        apply_url="https://scholarshipportal.mp.nic.in/",
        is_online_available=True,
        application_mode_note_en="Obtained from your admitted college/university; uploaded on MP Scholarship Portal.",
        application_mode_note_hi="प्रवेशित कॉलेज से प्राप्त कर मध्य प्रदेश छात्रवृत्ति पोर्टल पर अपलोड करें।",
        issuing_authority_note_en="Higher Education Dept / Admitted College / MP Scholarship Portal.",
        issuing_authority_note_hi="उच्च शिक्षा विभाग एवं संबंधित महाविद्यालय।"
    )
}

class DocumentService:
    def __init__(self):
        self._catalog = DOCUMENT_CATALOG
        self._alias_map: Dict[str, str] = {}
        for doc_id, doc in self._catalog.items():
            self._alias_map[doc_id.lower()] = doc_id
            for alias in doc.aliases:
                self._alias_map[alias.lower()] = doc_id

    def get_all_documents(self) -> List[DocumentSummary]:
        """Returns summary list of all available document guides."""
        summaries = []
        for doc in self._catalog.values():
            summaries.append(DocumentSummary(
                id=doc.id,
                name_en=doc.name_en,
                name_hi=doc.name_hi,
                category=doc.category,
                short_explanation_en=doc.short_explanation_en,
                short_explanation_hi=doc.short_explanation_hi,
                issuer_en=doc.issuer_en,
                issuer_hi=doc.issuer_hi,
                is_online_available=doc.is_online_available,
                apply_url=doc.apply_url
            ))
        return summaries

    def get_document_by_id(self, doc_id: str) -> Optional[DocumentDefinition]:
        """Resolves canonical document ID or alias, returning full details."""
        clean_id = doc_id.strip().lower()
        canonical_id = self._alias_map.get(clean_id)
        if not canonical_id:
            return None
        return self._catalog.get(canonical_id)

    def search_documents(self, query: str) -> List[DocumentSummary]:
        """Searches documents by name, category, or alias."""
        q = query.strip().lower()
        if not q:
            return self.get_all_documents()
        results = []
        for doc in self._catalog.values():
            if (q in doc.name_en.lower() or
                q in doc.name_hi.lower() or
                q in doc.category.lower() or
                any(q in alias.lower() for alias in doc.aliases) or
                q in doc.short_explanation_en.lower() or
                q in doc.short_explanation_hi.lower()):
                results.append(DocumentSummary(
                    id=doc.id,
                    name_en=doc.name_en,
                    name_hi=doc.name_hi,
                    category=doc.category,
                    short_explanation_en=doc.short_explanation_en,
                    short_explanation_hi=doc.short_explanation_hi,
                    issuer_en=doc.issuer_en,
                    issuer_hi=doc.issuer_hi,
                    is_online_available=doc.is_online_available,
                    apply_url=doc.apply_url
                ))
        return results

document_service = DocumentService()
