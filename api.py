############ LIBRARIES ############
import logging
from fastapi import FastAPI, HTTPException
from algorithm import calculate_production_plan

############ LOGGING ############
logging.basicConfig(level=logging.INFO) # see warning, error and info
logger = logging.getLogger(__name__)

############ API ############
api = FastAPI()


@api.post("/productionplan")
def production_plan(payload: dict):
    try:
        result = calculate_production_plan(payload)
        logger.info("Production plan calculated")
        return result

    except Exception as e:
        logger.error(f"Error calculating production plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))