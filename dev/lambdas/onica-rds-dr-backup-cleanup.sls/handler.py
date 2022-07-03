import logging
import os
from classes import RDSBackupCleanup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        lambda_region = os.environ['lambda_region']
        dr_region = os.environ['dr_region']
        instances = os.environ['instances'].split(",")
        retention_days = os.environ['retention_days']
        retention_days = int(retention_days)
        
        # Initializing classes
        my_rds_backup_cleanup = RDSBackupCleanup.RDSBackupCleanup(dr_region)

        # Checking if RDS instances exist, if present create instance snapshot
        if my_rds_backup_cleanup.get_rds_instance_snapshot(instances):
            
            #Delete RDS snapshots in primary region
            my_rds_backup_cleanup.delete_rds_snapshot_primary(instances,retention_days)
            
            #Delete RDS snapshots in DR region
            my_rds_backup_cleanup.delete_rds_snapshot_dr(instances,retention_days)
            
        else:
            print("Snapshot delete failed...")
            
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        
        
        
        
        
        
