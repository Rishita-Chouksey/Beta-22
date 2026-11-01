import { getOfflineAllSchemes } from './schemesCatalog';

export function generateOfflineDocumentChecklist(schemeIds = []) {
  const allSchemes = getOfflineAllSchemes();
  const schemesCovered = [];
  const docMap = {};

  const targetIds = new Set(schemeIds);

  for (const scheme of allSchemes) {
    if (targetIds.size > 0 && !targetIds.has(scheme.id)) continue;

    schemesCovered.push(scheme.name_en || scheme.id);
    const reqDocs = scheme.required_documents || [];

    for (const doc of reqDocs) {
      const docId = doc.id || doc.document_id;
      if (!docId) continue;

      if (docMap[docId]) {
        if (!docMap[docId].schemes_required_for.includes(scheme.name_en)) {
          docMap[docId].schemes_required_for.push(scheme.name_en);
        }
      } else {
        docMap[docId] = {
          document_id: docId,
          name_en: doc.name_en,
          name_hi: doc.name_hi,
          name_mr: doc.name_mr || doc.name_hi,
          name_bn: doc.name_bn || doc.name_hi,
          schemes_required_for: [scheme.name_en],
          purpose_en: doc.purpose_en || 'Required for identity and eligibility verification.',
          purpose_hi: doc.purpose_hi || 'पहचान एवं पात्रता सत्यापन हेतु आवश्यक।',
          purpose_mr: doc.purpose_mr || 'ओळख आणि पात्रता पडताळणीसाठी आवश्यक.',
          purpose_bn: doc.purpose_bn || 'পরিচয় এবং যোগ্যতা যাচাইয়ের জন্য আবশ্যক।',
          how_to_get_en: doc.how_to_get_en || 'Apply online via State Citizen Portal or visit your local CSC / Tehsil office.',
          how_to_get_hi: doc.how_to_get_hi || 'नागरिक सेवा पोर्टल पर ऑनलाइन आवेदन करें या निकटतम सीएससी / तहसील केंद्र जाएं।',
          how_to_get_mr: doc.how_to_get_mr || 'नागरी सेवा पोर्टलवर ऑनलाइन अर्ज करा किंवा जवळच्या सीएससी / तहसील कार्यालयाला भेट द्या.',
          how_to_get_bn: doc.how_to_get_bn || 'সিটিজেন সার্ভিস পোর্টালে অনলাইন আবেদন করুন বা স্থানীয় সিএসসি / তহশিল অফিসে যান।',
          online_url: doc.online_url || 'https://serviceonline.gov.in/',
          offline_office: doc.offline_office || 'Tehsil Office / CSC Center / Gram Panchayat',
        };
      }
    }
  }

  const documents = Object.values(docMap);
  return {
    documents,
    total_documents: documents.length,
    schemes_covered: schemesCovered,
  };
}
