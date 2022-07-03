import logging
import os
from classes import RDSBackup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        lambda_region = os.environ['lambda_region']
        instances = os.environ['instances'].split(",")
        
        # Initializing classes
        my_rds_backup = RDSBackup.RDSBackup()

        # Checking if RDS instances exist, if present create instance snapshot
        if my_rds_backup.get_rds_instance(instances):
            
            #Create RDS instance snapshot
            my_rds_backup.create_rds_snapshot(instances)
        else:
            print("Snapshot failed...")
            
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))