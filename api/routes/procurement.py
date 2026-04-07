import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends
from loguru import logger
from api.dependencies import get_db
from ai.forensics.bid_dna import BidDNA
from ai.forensics.cartel_detector import CartelDetector

router   = APIRouter()
bid_dna  = BidDNA()
cartel   = CartelDetector()


@router.get("/procurement/bid-dna/{entity_id}")
def bid_fingerprint(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Procurement] Bid DNA: {entity_id}")
    return bid_dna.analyze(entity_id, driver=driver)


@router.get("/procurement/cartel")
def cartel_detection(ministry: str = "road", driver=Depends(get_db)):
    logger.info(f"[Procurement] Cartel check: {ministry}")
    return cartel.analyze(ministry, driver=driver)
