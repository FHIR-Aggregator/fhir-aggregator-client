import pytest


@pytest.fixture
def fhir_base_urls():
    """Return a list of FHIR base URLs."""
    return ["https://google-fhir.test-fhir-aggregator.org", "https://google-fhir.fhir-aggregator.org"]


@pytest.fixture
def expected_study_identifiers():
    identifiers = """GTEX_V10
1KG
APOLLO-LUAD,phs003011
BEATAML1.0-COHORT,phs001657
BEATAML1.0-CRENOLANIB,phs001628
BU
CDDP_EAGLE-1,phs001239
CGCI-BLGSP,phs000527
CGCI-HTMCP-CC,phs000528
CGCI-HTMCP-DLBCL,phs000529
CGCI-HTMCP-LC,phs000530
CHOP
CMI-ASC,phs001931
CMI-MBC,phs001709
CMI-MPC,phs001939
CPTAC-2,phs000892
CPTAC-3,phs001287
CTSP-DLBCL1,phs001184
Cellosaurus
DFCI
Duke
EXCEPTIONAL_RESPONDERS-ER
FM-AD,phs001179
ICGC-LUCA_KR
HCMI-CMDC
HMS
HTAPP
MATCH-B,phs002028
MATCH-C1,phs002177
MATCH-H,phs001888
MATCH-I,phs002181
MATCH-N,phs002151
MATCH-P,phs002152
MATCH-Q,phs001926
MATCH-R,phs002029
MATCH-S1,phs002153
MATCH-S2,phs002178
MATCH-U,phs002179
MATCH-W,phs001948
MATCH-Y,phs001904
MATCH-Z1A,phs001973
MATCH-Z1B,phs002180
MATCH-Z1D,phs001859
MATCH-Z1I,phs002058
MMRF-COMMPASS,phs000748
MP2PRT-ALL,phs002005
MP2PRT-WT,phs001965
MSK
NCICCR-DLBCL
OHSU
OHSU-CNL,phs001799
ORGANOID-PANCREATIC,phs001611
REBC-THYR
Stanford
TARGET-ALL-P1,phs000463
TARGET-ALL-P2,phs000464
TARGET-ALL-P3
TARGET-AML,phs000465
TARGET-CCSK,phs000466
TARGET-NBL,phs000467
TARGET-OS,phs000468
TARGET-RT,phs000470
TARGET-WT,phs000471
TCGA-ACC
TCGA-BLCA
TCGA-BRCA
TCGA-CESC
TCGA-CHOL
TCGA-COAD
TCGA-DLBC
TCGA-ESCA
TCGA-GBM
TCGA-HNSC
TCGA-KICH
TCGA-KIRC
TCGA-KIRP
TCGA-LAML
TCGA-LGG
TCGA-LIHC
TCGA-LUAD
TCGA-LUSC
TCGA-MESO
TCGA-OV
TCGA-PAAD
TCGA-PCPG
TCGA-PRAD
TCGA-READ
TCGA-SARC
TCGA-SKCM
TCGA-STAD
TCGA-TGCT
TCGA-THCA
TCGA-THYM
TCGA-UCEC
TCGA-UCS
TCGA-UVM
TNP SARDANA
TRIO-CRU,phs001163
VAREPOP-APOLLO,phs001374
Vanderbilt
WCDT-MCRPC,phs001648
WUSTL""".split(
        "\n"
    )
    identifiers = [_.strip() for _ in identifiers]
    return [_ for _ in identifiers if _ != ""]
