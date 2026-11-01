// Resilient client-side mock data for Multi-Agent Monitoring Dashboard
// Enables offline/demo mode when backend is unreachable or not yet deployed.

export function getOfflineMonitoringOverview() {
  return {
    success: true,
    overview: {
      total_sources_discovered: 24,
      active_monitors: 18,
      schemes_discovered: 20,
      pending_human_review: 2,
      approved_updates: 6,
      failed_agent_runs: 0,
      last_crawl_time: new Date().toISOString(),
      system_health: 'Healthy (Deterministic Grounding Active)',
    },
  };
}

export function getOfflineAgentsStatus() {
  return {
    success: true,
    agents: [
      {
        agent_id: 'source_discovery',
        name: 'Source Discovery Agent',
        status: 'active',
        last_run: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
        total_runs: 148,
        success_rate: '100%',
        last_log: 'Scanned data.gov.in & MP e-Seva; 24 official seed links active.',
      },
      {
        agent_id: 'crawling',
        name: 'Crawling Agent',
        status: 'active',
        last_run: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
        total_runs: 312,
        success_rate: '100%',
        last_log: 'Extracted clean HTML & gazette circular text via SSL resilient client.',
      },
      {
        agent_id: 'change_detection',
        name: 'Change Detection Agent',
        status: 'idle',
        last_run: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
        total_runs: 285,
        success_rate: '100%',
        last_log: 'SHA-256 fingerprint verified; 1 semantic change detected in guidelines.',
      },
      {
        agent_id: 'information_extraction',
        name: 'Information Extraction Agent',
        status: 'active',
        last_run: new Date(Date.now() - 1000 * 60 * 6).toISOString(),
        total_runs: 198,
        success_rate: '100%',
        last_log: 'Structured AST eligibility conditions and benefits extracted.',
      },
      {
        agent_id: 'classification',
        name: 'Classification Agent',
        status: 'idle',
        last_run: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        total_runs: 198,
        success_rate: '100%',
        last_log: 'Categorized under "Higher Education Scholarship" & "State Welfare".',
      },
      {
        agent_id: 'evidence_validation',
        name: 'Evidence Validation Agent',
        status: 'active',
        last_run: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
        total_runs: 195,
        success_rate: '100%',
        last_log: 'Official circular cross-referenced against gazette notification. Grounded: 100%.',
      },
      {
        agent_id: 'policy_review_gate',
        name: 'Policy Review Gate',
        status: 'waiting_review',
        last_run: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
        total_runs: 45,
        success_rate: '100%',
        last_log: '2 proposed updates staged for Human-in-the-Loop admin officer review.',
      },
      {
        agent_id: 'publishing_service',
        name: 'Publishing Service',
        status: 'idle',
        last_run: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        total_runs: 42,
        success_rate: '100%',
        last_log: 'Immutable audit version created; updated scheme rules deployed to live engine.',
      },
      {
        agent_id: 'monitoring',
        name: 'Monitoring Agent',
        status: 'active',
        last_run: new Date(Date.now() - 1000 * 60 * 1).toISOString(),
        total_runs: 450,
        success_rate: '100%',
        last_log: 'Polite polling heartbeat active; 18/18 live endpoints responding 200 OK.',
      },
    ],
  };
}

export function getOfflineDiscoveredSources() {
  return {
    success: true,
    count: 6,
    sources: [
      {
        id: 'src_data_gov',
        title: 'Open Government Data Platform (data.gov.in)',
        url: 'https://data.gov.in/datasets/central-schemes',
        status: 'active',
        frequency: 'Daily (02:00 UTC)',
        last_checked: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        http_status: 200,
        category: 'central',
        discovered_schemes_count: 8,
      },
      {
        id: 'src_mp_eseva',
        title: 'MP e-Seva / Citizen Welfare Portal',
        url: 'https://eseva.mp.gov.in/schemes',
        status: 'active',
        frequency: 'Daily (03:00 UTC)',
        last_checked: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
        http_status: 200,
        category: 'state',
        discovered_schemes_count: 5,
      },
      {
        id: 'src_pm_kisan',
        title: 'Pradhan Mantri Kisan Samman Nidhi Portal',
        url: 'https://pmkisan.gov.in/',
        status: 'active',
        frequency: 'Bi-daily',
        last_checked: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
        http_status: 200,
        category: 'central',
        discovered_schemes_count: 1,
      },
      {
        id: 'src_pmayg',
        title: 'Ministry of Rural Development - PMAY-G',
        url: 'https://pmayg.nic.in/netiay/home.aspx',
        status: 'active',
        frequency: 'Daily (04:00 UTC)',
        last_checked: new Date(Date.now() - 1000 * 60 * 50).toISOString(),
        http_status: 200,
        category: 'central',
        discovered_schemes_count: 1,
      },
      {
        id: 'src_ladli_behna',
        title: 'Mukhyamantri Ladli Behna Yojana Portal',
        url: 'https://cmladlibahna.mp.gov.in/',
        status: 'active',
        frequency: 'Daily (01:00 UTC)',
        last_checked: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        http_status: 200,
        category: 'state',
        discovered_schemes_count: 1,
      },
      {
        id: 'src_mp_scholarship',
        title: 'MP State Scholarship Portal 2.0 (MMVY / Gaon Ki Beti)',
        url: 'https://scholarshipportal.mp.nic.in/',
        status: 'active',
        frequency: 'Daily (02:30 UTC)',
        last_checked: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
        http_status: 200,
        category: 'state',
        discovered_schemes_count: 2,
      },
    ],
  };
}

export function getOfflineAgentUpdates() {
  return {
    success: true,
    count: 2,
    updates: [
      {
        id: 'upd_mmvy_income_2026',
        scheme_id: 'mmvy',
        scheme_name: 'Mukhyamantri Medhavi Vidyarthi Yojana (MMVY)',
        change_type: 'Rule Modification (Income Ceiling Revision)',
        proposed_value: 'Family annual income limit updated to ₹6,00,000 (from ₹8,00,000 threshold check)',
        confidence_score: 0.96,
        status: 'pending',
        evidence_url: 'https://scholarshipportal.mp.nic.in/circulars/2026/mmvy_income_guideline.pdf',
        source_title: 'MP State Higher Education Department Circular No. F-17/2026',
        extracted_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        requires_human_approval: true,
      },
      {
        id: 'upd_ladli_behna_dbt',
        scheme_id: 'ladli_behna',
        scheme_name: 'Mukhyamantri Ladli Behna Yojana',
        change_type: 'Benefit Augmentation',
        proposed_value: 'Direct bank transfer monthly installment confirmed at ₹1,250 with LPG subsidy integration',
        confidence_score: 0.98,
        status: 'pending',
        evidence_url: 'https://cmladlibahna.mp.gov.in/circulars/2026/dbt_installment.pdf',
        source_title: 'Women & Child Development Department MP Order',
        extracted_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
        requires_human_approval: true,
      },
    ],
  };
}

export function getOfflineAgentRuns() {
  return {
    success: true,
    count: 6,
    runs: [
      {
        id: 'run_908',
        agent_id: 'evidence_validation',
        agent_name: 'Evidence Validation Agent',
        target_source: 'scholarshipportal.mp.nic.in',
        status: 'success',
        duration_ms: 380,
        timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
        summary: 'Cross-checked circular PDF against gazette rules. Grounding confidence 96%.',
      },
      {
        id: 'run_907',
        agent_id: 'information_extraction',
        agent_name: 'Information Extraction Agent',
        target_source: 'cmladlibahna.mp.gov.in',
        status: 'success',
        duration_ms: 540,
        timestamp: new Date(Date.now() - 1000 * 60 * 6).toISOString(),
        summary: 'Extracted rule conditions and benefit parameters without hallucinations.',
      },
      {
        id: 'run_906',
        agent_id: 'change_detection',
        agent_name: 'Change Detection Agent',
        target_source: 'eseva.mp.gov.in',
        status: 'success',
        duration_ms: 120,
        timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
        summary: 'SHA-256 fingerprint delta matched. Identified 1 modified guideline.',
      },
      {
        id: 'run_905',
        agent_id: 'crawling',
        agent_name: 'Crawling Agent',
        target_source: 'pmkisan.gov.in',
        status: 'success',
        duration_ms: 610,
        timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
        summary: 'Fetched portal HTML via legacy-resilient SSL client. 200 OK.',
      },
      {
        id: 'run_904',
        agent_id: 'source_discovery',
        agent_name: 'Source Discovery Agent',
        target_source: 'data.gov.in',
        status: 'success',
        duration_ms: 820,
        timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
        summary: 'Discovered 4 public datasets and circular PDFs across central ministries.',
      },
    ],
  };
}

export function getOfflineSchemeVersions(schemeId = 'gaon_ki_beti') {
  return {
    success: true,
    scheme_id: schemeId,
    count: 2,
    versions: [
      {
        version_id: 'v2.1',
        scheme_id: schemeId,
        change_type: 'Gazette Alignment',
        summary: 'Eligibility conditions verified and locked against official gazette notification.',
        reviewed_by: 'Admin Officer (Authorized)',
        approved_at: '2026-10-28T10:00:00Z',
        hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        status: 'active',
      },
      {
        version_id: 'v2.0',
        scheme_id: schemeId,
        change_type: 'Initial Digitization',
        summary: 'Initial baseline rules established from official state department notification.',
        reviewed_by: 'Policy Review Gate',
        approved_at: '2026-10-15T09:30:00Z',
        hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
        status: 'archived',
      },
    ],
  };
}
