import sys
import os
sys.path.append(os.getcwd())
from feature2.db_ops import get_sourcing_candidates_by_job, update_candidate_status
from bson.objectid import ObjectId
candidates = get_sourcing_candidates_by_job("d6356b02-5ab2-43c3-b276-1f211665c0d0")
for c in candidates:
    print(c.get("status", "NO_STATUS"))
