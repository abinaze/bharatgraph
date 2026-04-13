import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from loguru import logger
from graph.loader import GraphLoader

load_dotenv()

SAMPLE_POLITICIANS = [
    {"id":"pol_001","name":"Narendra Modi","state":"Gujarat","party":"BJP",
     "constituency":"Varanasi","criminal_cases":0,"criminal_case_count":"0","total_assets":2.85,
     "education":"BA Political Science","year":2024},
    {"id":"pol_002","name":"Rahul Gandhi","state":"Kerala","party":"INC",
     "constituency":"Wayanad","criminal_cases":0,"criminal_case_count":"0","total_assets":15.89,
     "education":"MPhil Development Studies","year":2024},
    {"id":"pol_003","name":"Amit Shah","state":"Gujarat","party":"BJP",
     "constituency":"Gandhinagar","criminal_cases":0,"criminal_case_count":"0","total_assets":42.33,
     "education":"BSc Biochemistry","year":2024},
    {"id":"pol_004","name":"Smriti Irani","state":"Uttar Pradesh","party":"BJP",
     "constituency":"Amethi","criminal_cases":0,"criminal_case_count":"0","total_assets":9.12,
     "education":"BA (Incomplete)","year":2024},
    {"id":"pol_005","name":"Arvind Kejriwal","state":"Delhi","party":"AAP",
     "constituency":"New Delhi","criminal_cases":3,"criminal_case_count":"3","total_assets":3.40,
     "education":"BTech IIT Kharagpur","year":2024},
    {"id":"pol_006","name":"Mamata Banerjee","state":"West Bengal","party":"AITC",
     "constituency":"Bhowanipore","criminal_cases":0,"criminal_case_count":"0","total_assets":1.25,
     "education":"BA History","year":2024},
    {"id":"pol_007","name":"Nitish Kumar","state":"Bihar","party":"JDU",
     "constituency":"Nalanda","criminal_cases":0,"criminal_case_count":"0","total_assets":1.65,
     "education":"BE Electrical","year":2024},
    {"id":"pol_008","name":"Yogi Adityanath","state":"Uttar Pradesh","party":"BJP",
     "constituency":"Gorakhpur","criminal_cases":0,"criminal_case_count":"0","total_assets":1.08,
     "education":"BSc Mathematics","year":2024},
    {"id":"pol_009","name":"Shashi Tharoor","state":"Kerala","party":"INC",
     "constituency":"Thiruvananthapuram","criminal_cases":1,"criminal_case_count":"1","total_assets":27.44,
     "education":"PhD Tufts University","year":2024},
    {"id":"pol_010","name":"Anurag Thakur","state":"Himachal Pradesh","party":"BJP",
     "constituency":"Hamirpur","criminal_cases":0,"criminal_case_count":"0","total_assets":33.87,
     "education":"BA History","year":2024},
]

SAMPLE_COMPANIES = [
    {"id":"co_001","name":"Adani Enterprises Limited","state":"Gujarat",
     "cin":"L51100GJ1993PLC019067","status":"Active","paid_up_capital_crore":112.0},
    {"id":"co_002","name":"Reliance Industries Limited","state":"Maharashtra",
     "cin":"L17110MH1973PLC019786","status":"Active","paid_up_capital_crore":673.0},
    {"id":"co_003","name":"Tata Consultancy Services","state":"Maharashtra",
     "cin":"L22210MH1995PLC084781","status":"Active","paid_up_capital_crore":366.0},
    {"id":"co_004","name":"Infosys Limited","state":"Karnataka",
     "cin":"L85110KA1981PLC013115","status":"Active","paid_up_capital_crore":207.0},
    {"id":"co_005","name":"Bharti Airtel Limited","state":"Delhi",
     "cin":"L74899DL1995PLC070609","status":"Active","paid_up_capital_crore":282.0},
]

SAMPLE_CONTRACTS = [
    {"id":"ct_001","order_id":"GEM/2024/B/001","item_desc":"Road Construction Supplies",
     "amount_crore":45.5,"buyer_org":"Ministry of Road Transport",
     "order_date":"2024-03-15","company_id":"co_001","seller_name":"Adani Enterprises Limited","seller_name_raw":"Adani Enterprises Limited"},
    {"id":"ct_002","order_id":"GEM/2024/B/002","item_desc":"IT Infrastructure Services",
     "amount_crore":128.0,"buyer_org":"Ministry of Electronics and IT",
     "order_date":"2024-02-10","company_id":"co_003","seller_name":"Tata Consultancy Services","seller_name_raw":"Tata Consultancy Services"},
    {"id":"ct_003","order_id":"GEM/2024/B/003","item_desc":"Telecom Equipment",
     "amount_crore":67.3,"buyer_org":"Ministry of Communications",
     "order_date":"2024-01-20","company_id":"co_005","seller_name":"Bharti Airtel Limited","seller_name_raw":"Bharti Airtel Limited"},
]

SAMPLE_AUDIT_REPORTS = [
    {"id":"ar_001","title":"Performance Audit of Pradhan Mantri Gram Sadak Yojana 2023",
     "year":2023,"ministry":"Ministry of Rural Development","state":"National",
     "amount_crore":234.5,"url":"https://cag.gov.in/reports/2023"},
    {"id":"ar_002","title":"Compliance Audit of Smart Cities Mission 2022",
     "year":2022,"ministry":"Ministry of Housing and Urban Affairs","state":"National",
     "amount_crore":189.2,"url":"https://cag.gov.in/reports/2022"},
    {"id":"ar_003","title":"Revenue Audit of GST Collections Maharashtra 2023",
     "year":2023,"ministry":"Ministry of Finance","state":"Maharashtra",
     "amount_crore":456.8,"url":"https://cag.gov.in/reports/2023"},
]


def seed():
    loader = GraphLoader()

    logger.info("[Seed] Loading sample politicians...")
    n = loader.load_politicians(SAMPLE_POLITICIANS)
    logger.success(f"[Seed] Politicians loaded: {n}")

    logger.info("[Seed] Loading sample companies...")
    n = loader.load_companies(SAMPLE_COMPANIES)
    logger.success(f"[Seed] Companies loaded: {n}")

    logger.info("[Seed] Loading sample contracts...")
    n = loader.load_contracts(SAMPLE_CONTRACTS)
    logger.success(f"[Seed] Contracts loaded: {n}")

    logger.info("[Seed] Loading sample audit reports...")
    n = loader.load_audit_reports(SAMPLE_AUDIT_REPORTS)
    logger.success(f"[Seed] Audit reports loaded: {n}")

    logger.success("[Seed] Database seeded. Search 'Modi', 'Gandhi', 'Adani' to test.")


if __name__ == "__main__":
    seed()
