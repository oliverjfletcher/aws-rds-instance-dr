import logging
import os
from classes import RDSRestore

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        lambda_region = os.environ['lambda_region']
        rds_instance = [os.environ['rds_instance']]
        rds_instance_type = os.environ['rds_instance_type']
        rds_subnet_group = os.environ['rds_subnet_group'] 
        multi_az = True
        rds_public = False
        
        # Initializing classes
        my_rds_restore = RDSRestore.RDSRestore()

        # Checking if RDS instance snapshot exist, if present restore to DR region
        if my_rds_restore.get_rds_instance_snapshot(rds_instance):
            
            #Restore RDS instance snapshot to DR region
            my_rds_restore.restore_rds_snapshot(rds_instance,rds_instance_type,rds_subnet_group,multi_az,rds_public)
        else:
            print("RDS Snapshot restore failed...")
            
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))