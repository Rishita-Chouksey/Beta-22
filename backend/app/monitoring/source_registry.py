from typing import List, Optional

from .models import SourceDefinition, SourceCategory, SourceType, MonitoringFrequency, AccessibilityStatus


# These scheme pages were reviewed manually and are the source links shown in
# the citizen catalogue. Automated fetches are intentionally disabled.
MYSCHEME_MANUAL_PAGES = [
    ("pm_kisan", "PM Kisan Samman Nidhi", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/pm-kisan"),
    ("pm_jay_ayushman", "Ayushman Bharat PM-JAY", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/ab-pmjay"),
    ("ladli_behna_mp", "Chief Minister Ladli Behna Yojana", SourceCategory.MADHYA_PRADESH, "https://www.myscheme.gov.in/schemes/cmlby"),
    ("pm_kisan_maandhan", "Pradhan Mantri Kisan Maandhan Yojana", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/pmkmdy"),
    ("pm_vishwakarma", "PM Vishwakarma", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/pmv"),
    ("pmay_urban", "Pradhan Mantri Awas Yojana - Urban 2.0", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/pmay-u"),
    ("pm_surya_ghar", "PM - Surya Ghar: Muft Bijli Yojana", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/pmsgmb"),
    ("pmsby", "Pradhan Mantri Suraksha Bima Yojana", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/hi/schemes/pmsby"),
    ("mp_student_welfare", "Student Welfare Scheme (Madhya Pradesh)", SourceCategory.MADHYA_PRADESH, "https://www.myscheme.gov.in/schemes/sws"),
    ("gaon_ki_beti", "Gaon Ki Beti", SourceCategory.MADHYA_PRADESH, "https://www.myscheme.gov.in/schemes/gkb"),
    ("pragati_scholarship_degree", "Pragati Scholarship for Girl Students", SourceCategory.CENTRAL, "https://www.myscheme.gov.in/schemes/psgs-deg"),
    ("post_metric_mp", "Post Metric Scholarship - Madhya Pradesh", SourceCategory.MADHYA_PRADESH, "https://www.myscheme.gov.in/schemes/pmsm"),
    ("mp_swarojgar", "Mukhya Mantri Swarojgar Yojana", SourceCategory.MADHYA_PRADESH, "https://www.myscheme.gov.in/schemes/msy"),
    ("ignoaps_punjab", "Indira Gandhi National Old Age Pension Scheme (Punjab)", SourceCategory.OTHER, "https://www.myscheme.gov.in/hi/schemes/ignoapsp"),
    ("ignwps_sikkim", "Indira Gandhi National Widow Pension Scheme (Sikkim)", SourceCategory.OTHER, "https://www.myscheme.gov.in/hi/schemes/ignwps-sikkim"),
]

OFFICIAL_SOURCE_CATALOG: List[SourceDefinition] = [
    SourceDefinition(
        source_id=f"src_myscheme_{scheme_id}",
        name=f"{name} (myScheme manual reference)",
        category=category,
        official_url=url,
        source_type=SourceType.HTML,
        monitoring_frequency=MonitoringFrequency.WEEKLY,
        target_scheme_ids=[scheme_id],
        automated_monitoring_permitted=False,
        accessibility_status=AccessibilityStatus.PENDING,
    )
    for scheme_id, name, category, url in MYSCHEME_MANUAL_PAGES
]


class SourceRegistry:
    """Registry for manually curated source references."""

    @staticmethod
    def get_all_sources() -> List[SourceDefinition]:
        return list(OFFICIAL_SOURCE_CATALOG)

    @staticmethod
    def get_source_by_id(source_id: str) -> Optional[SourceDefinition]:
        return next((src for src in OFFICIAL_SOURCE_CATALOG if src.source_id == source_id), None)

    @staticmethod
    def get_sources_for_scheme(scheme_id: str) -> List[SourceDefinition]:
        return [src for src in OFFICIAL_SOURCE_CATALOG if scheme_id in src.target_scheme_ids]
