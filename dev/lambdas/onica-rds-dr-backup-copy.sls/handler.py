import logging
import os
from classes import RDSBackupCopy

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        lambda_region = os.environ['lambda_region']
        primary_region = os.environ['primary_region']
        dr_region = os.environ['dr_region']
        instances = os.environ['instances'].split(",")
        kms_arn = os.environ['kms_arn']
        
        # Initializing classes
        my_rds_backup_copy = RDSBackupCopy.RDSBackupCopy(dr_region)

        # Checking if RDS instance snapshot exists, if present copy instance snapshot
        if my_rds_backup_copy.get_rds_instance_snapshot(instances):

            #Copy RDS instance snapshot to DR region
            my_rds_backup_copy.copy_rds_snapshot(instances,primary_region,dr_region,kms_arn)
            
            #Get RDS instance snapshots in DR region
            my_rds_backup_copy.get_rds_dr_snapshots(instances)
            
        else:
            print("RDS instance snapshot copy failed...")
            
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        
        