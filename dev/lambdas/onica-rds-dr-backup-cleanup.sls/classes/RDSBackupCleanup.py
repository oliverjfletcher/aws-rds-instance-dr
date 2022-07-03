import botocore  
import datetime  
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class RDSBackupCleanup:

    def __init__(self,dr_region):
            self.my_rds_primary = boto3.client('rds')
            self.my_rds_dr = boto3.client('rds',region_name=dr_region)
            
    def get_rds_instance_snapshot(self,instances):
        """
        Check if RDS instance exists and return result
        Expects RDS instance name(s) as string
        """
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
                    logger.info("RDS instance " + instance + " snapshot exists")
                    result = True
                else:
                    logger.info("RDS instance " + instance + " snapshot does not exist")
                    result = False
                return result
        
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFound':
                logger.info("RDS instance snapshot does not exist for" + instance + "Returning false")
            return False

        except Exception as e:
            logger.error('Class RDSBackupCleanup. Method get_rds_instance_snapshot failed with error: ' + str(e))
    
    def delete_rds_snapshot_primary(self,instances,retention_days):
        """
        Delete RDS instance(s) snapshot based on static retention days located in DR region
        Expects RDS instance(s) and number of retention days as string
        """           
        try:
            retention_date = (datetime.datetime.now() - datetime.timedelta(days=retention_days)).strftime('%Y-%m-%d')
            
            for instance in instances:
                logger.info("Retrieving current RDS instance snapshots")
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
                logger.info("Checking if RDS snapshot creation date is less than retention date, and lambda-dr found in snapshot id")
                for snapshot in rds_snapshots['DBSnapshots']:
                    if snapshot['SnapshotCreateTime'].strftime('%Y-%m-%d') > retention_date and 'lambda-dr' in snapshot['DBSnapshotIdentifier']:
                        logger.info("Deleting RDS snapshots that are less than retention date")
                        snapshot_delete = self.my_rds_primary.delete_db_snapshot(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])
                        status = snapshot_delete['DBSnapshot']['Status']
                        logger.info("RDS instance" + instance + " snapshot status is now " + status)
        
        except Exception as e:
            logger.error('Class RDSBackupCleanup Method delete_rds_snapshot_primary failed with error: ' + str(e))
            
            
    def delete_rds_snapshot_dr(self,instances,retention_days):
        """
        Delete RDS instance(s) snapshot based on static retention days located in DR region
        Expects RDS instance(s) and number of retention days as string
        """          
        try:
            retention_date = (datetime.datetime.now() - datetime.timedelta(days=retention_days)).strftime('%Y-%m-%d')
            
            for instance in instances:
                logger.info("Setting variable for RDS snapshot retention date")
                
                logger.info("Retrieving current RDS instance snapshots")
                rds_snapshots = self.my_rds_dr.describe_db_snapshots(
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
                logger.info("Checking if RDS snapshot creation date is less than retention date, and lambda-dr found in snapshot id")
                for snapshot in rds_snapshots['DBSnapshots']:
                    if snapshot['SnapshotCreateTime'].strftime('%Y-%m-%d') < retention_date and 'lambda-dr' in snapshot['DBSnapshotIdentifier']:
                        logger.info("Deleting RDS snapshots that are less than retention date")
                        snapshot_delete = self.my_rds_dr.delete_db_snapshot(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])
                        status = snapshot_delete['DBSnapshot']['Status']
                        logger.info("RDS instance " + instance + " snapshot status is now " + status)
        
        except Exception as e:
            logger.error('Class RDSBackupCleanup Method delete_rds_snapshot_dr failed with error: ' + str(e))
                
                
                
         
    
    