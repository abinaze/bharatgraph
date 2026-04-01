from ai.investigators.financial_investigator    import FinancialInvestigator
from ai.investigators.political_investigator    import PoliticalInvestigator
from ai.investigators.corporate_investigator    import CorporateInvestigator
from ai.investigators.judicial_investigator     import JudicialInvestigator
from ai.investigators.procurement_investigator  import ProcurementInvestigator
from ai.investigators.network_investigator      import NetworkInvestigator
from ai.investigators.asset_investigator        import AssetInvestigator
from ai.investigators.international_investigator import InternationalInvestigator
from ai.investigators.media_investigator        import MediaInvestigator
from ai.investigators.historical_investigator   import HistoricalInvestigator
from ai.investigators.public_interest_investigator import PublicInterestInvestigator
from ai.investigators.doubt_investigator        import DoubtInvestigator

ALL_INVESTIGATORS = [
    FinancialInvestigator,
    PoliticalInvestigator,
    CorporateInvestigator,
    JudicialInvestigator,
    ProcurementInvestigator,
    NetworkInvestigator,
    AssetInvestigator,
    InternationalInvestigator,
    MediaInvestigator,
    HistoricalInvestigator,
    PublicInterestInvestigator,
    DoubtInvestigator,
]
