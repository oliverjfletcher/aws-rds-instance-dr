import logging
import os
from classes import RDSBackupCopy

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define list of RDS instances for snapshot copy
instances = ['oliver-test-database-0', 'oliver-test-database-1']

def lambda_handler(event, context):
    try:
        lambda_region = os.environ['lambda_region']
        primary_region = os.environ['primary_region']
        dr_region = os.environ['dr_region']
        kms_key_arn = os.environ['kms_key_arn']
        
        # Initializing classes
        my_rds_backup_copy = RDSBackupCopy.RDSBackupCopy(dr_region)

        # Checking if RDS instances exist, if present create instance snapshot
        if my_rds_backup_copy.get_rds_instance(instances):

            #Copy RDS instance snapshot to DR region
            my_rds_backup_copy.copy_rds_snapshot(instances,primary_region,dr_region,kms_key_arn)
            
            #Get RDS instance snapshots in DR region
            my_rds_backup_copy.get_rds_dr_snapshots(instances)
            
        else:
            print("RDS instance snapshot copy failed...")
            
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))