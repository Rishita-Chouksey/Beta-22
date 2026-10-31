from typing import List, Dict, Optional
from .models import SourceDefinition, SourceCategory, SourceType, MonitoringFrequency, AccessibilityStatus

# Central source registry of verified public government portals.
# Sources can be monitored independently via HTTP/RSS/HTML parsing.
# All sources adhere to polite civic scraping policies and robots.txt.

OFFICIAL_SOURCE_CATALOG: List[SourceDefinition] = [
    # --- CENTRAL GOVERNMENT SOURCES ---
    SourceDefinition(
        source_id="src_central_pmkisan",
        name="PM-KISAN Samman Nidhi Official Portal",
        category=SourceCategory.CENTRAL,
        official_url="https://pmkisan.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.DAILY,
        target_scheme_ids=["pm_kisan"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_central_pmjay",
        name="Ayushman Bharat PM-JAY Portal (National Health Authority)",
        category=SourceCategory.CENTRAL,
        official_url="https://pmjay.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.DAILY,
        target_scheme_ids=["pm_jay_ayushman"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_central_pmayg",
        name="Pradhan Mantri Awaas Yojana - Gramin (MoRD)",
        category=SourceCategory.CENTRAL,
        official_url="https://pmayg.nic.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=["pm_awas_yojana_gramin"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_central_nsap_ignwps",
        name="National Social Assistance Programme (NSAP) Portal",
        category=SourceCategory.CENTRAL,
        official_url="https://nsap.nic.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=["ignwps_widow_pension"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_central_nsp",
        name="National Scholarship Portal (Central Scholarships)",
        category=SourceCategory.CENTRAL,
        official_url="https://scholarships.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.DAILY,
        target_scheme_ids=["nsp_central_sector"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_central_myscheme_public",
        name="myScheme Public Discovery Portal (Reference)",
        category=SourceCategory.CENTRAL,
        official_url="https://www.myscheme.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.DAILY,
        target_scheme_ids=["pm_kisan", "pm_jay_ayushman", "pm_awas_yojana_gramin"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_central_datagov_schemes",
        name="Open Government Data Platform (data.gov.in Public Catalog)",
        category=SourceCategory.CENTRAL,
        official_url="https://data.gov.in/",
        source_type=SourceType.API,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=["central_welfare_catalog"],
        automated_monitoring_permitted=True,
    ),

    # --- MADHYA PRADESH GOVERNMENT SOURCES ---
    SourceDefinition(
        source_id="src_mp_ladlibehna",
        name="Mukhyamantri Ladli Behna Yojana Portal (Govt of MP)",
        category=SourceCategory.MADHYA_PRADESH,
        official_url="https://cmladlibahna.mp.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.DAILY,
        target_scheme_ids=["ladli_behna_mp"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_mp_scholarship_mmvy",
        name="MP State Scholarship Portal 2.0 (MMVY Scheme)",
        category=SourceCategory.MADHYA_PRADESH,
        official_url="http://scholarshipportal.mp.nic.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.DAILY,
        target_scheme_ids=["mmvy_scholarship"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_mp_edistrict",
        name="MP e-District Lok Seva Kendra Citizen Services",
        category=SourceCategory.MADHYA_PRADESH,
        official_url="http://mpedistrict.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=["ladli_behna_mp", "mmvy_scholarship"],
        automated_monitoring_permitted=True,
    ),
    SourceDefinition(
        source_id="src_mp_farmer_dbt",
        name="Madhya Pradesh Kisan Kalyan & Agriculture DBT Portal",
        category=SourceCategory.MADHYA_PRADESH,
        official_url="https://dbt.mp.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=["mp_kisan_kalyan"],
        automated_monitoring_permitted=True,
    ),

    # --- OTHER AUTHENTIC SOURCES ---
    SourceDefinition(
        source_id="src_mh_sjsa_niradhar",
        name="Maharashtra Social Justice Dept - Sanjay Gandhi Niradhar",
        category=SourceCategory.OTHER,
        official_url="https://sjsa.maharashtra.gov.in/",
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=["sanjay_gandhi_niradhar_mh"],
        automated_monitoring_permitted=True,
    ),
]

class SourceRegistry:
    """In-memory and persistent source registry manager."""
    
    @staticmethod
    def get_all_sources() -> List[SourceDefinition]:
        return list(OFFICIAL_SOURCE_CATALOG)

    @staticmethod
    def get_source_by_id(source_id: str) -> Optional[SourceDefinition]:
        for src in OFFICIAL_SOURCE_CATALOG:
            if src.source_id == source_id:
                return src
        return None

    @staticmethod
    def get_sources_for_scheme(scheme_id: str) -> List[SourceDefinition]:
        return [src for src in OFFICIAL_SOURCE_CATALOG if scheme_id in src.target_scheme_ids]
