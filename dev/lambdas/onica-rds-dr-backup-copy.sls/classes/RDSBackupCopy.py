import boto3
import botocore 
import logging
import datetime
import re


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDSBackupCopy:

    def __init__(self,dr_region):
            self.my_rds_primary = boto3.client('rds')
            self.my_rds_dr = boto3.client('rds',region_name=dr_region)
            self.my_account = boto3.client('sts').get_caller_identity().get('Account')
            
    def get_rds_instance_snapshot(self,instances):   
        try:
            result = False
            for instance in instances:
            
                logger.info("Retrieving current RDS instance snapshots for " + instance)
            rds_snapshots = self.my_rds_primary.describe_db_snapshots(
            DBInstanceIdentifier=instance,
            Filters=[
                {
                    'Name': 'snapshot-type',
                    'Values': [
                        'manual',
                        ]
                    }
                ]
            )
            logger.info("Checking if RDS snapshot name contains instance name and id")
            for snapshot in rds_snapshots['DBSnapshots']:
                if instance in snapshot['DBSnapshotIdentifier'] and 'lambda-dr' in snapshot['DBSnapshotIdentifier']:
                    logger.info("RDS instance snapshot exists")
                    result = True
                else:
                    logger.info("RDS instance snapshot does not exist")
            return result
        
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFound':
                logger.info("RDS instance snapshot does not exist for " + instance + " Returning false")
            return False

        except Exception as e:
            logger.error('Class RDSBackupCleanup. Method get_rds_instance_snapshot failed with error: ' + str(e))


    def copy_rds_snapshot(self,instances, primary_region, dr_region,kms_arn):
        try:
        
            for instance in instances:
                logger.info("Copying RDS instance snapshot for instance " + instance + " to DR site " + dr_region) 
                date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
                target_snapshot_name = 'lambda-dr-snapshot'
                source_rds_snapshot_arn = 'arn:aws:rds:%s:%s:snapshot:%s-%s-%s' % (primary_region, self.my_account, target_snapshot_name, instance, date)
                target_snapshot_id = '%s-%s-%s' % (target_snapshot_name, instance, date)
        
                self.my_rds_dr.copy_db_snapshot(
                            SourceDBSnapshotIdentifier=source_rds_snapshot_arn,
                            TargetDBSnapshotIdentifier=target_snapshot_id,
                            CopyTags = True,
                            SourceRegion = primary_region,
                            KmsKeyId=kms_arn)
                
                logger.info("RDS instance " + instance + " snapshots have been copied to " + dr_region)
                
                
                
        except Exception as e:
            logger.error('Class RDSBackupCopy. Method copy_rds_snapshot failed with error: ' + str(e))
  
  
    def get_rds_dr_snapshots(self,instances):
        try:      
            for instance in instances:
    
                rds_snapshots = self.my_rds_dr.describe_db_snapshots(SnapshotType='manual', DBInstanceIdentifier=instance)
                for rds_snapshot in rds_snapshots['DBSnapshots']:
                    rds_snapshots = rds_snapshot['SourceDBSnapshotIdentifier']
                 
                    logger.info("RDS instance DR snapshot arns are as followed: " + rds_snapshots)
                 
        except Exception as e:
            logger.error('Class RDSBackupCopy. Method get_rds_dr_snapshots failed with error: ' + str(e))
  