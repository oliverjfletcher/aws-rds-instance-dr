import botocore  
import datetime  
import re  
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class RDSRestore:

    def __init__(self):
            self.my_rds = boto3.client('rds')
            
    def get_rds_instance_snapshot(self,rds_instance):   
        try:
            result = False
            for instance in rds_instance:
            
                logger.info("Retrieving current RDS instance snapshots for " + instance)
            rds_snapshots = self.my_rds.describe_db_snapshots(
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
                logger.info("RDS instance snapshot does not exist for" + instance + "Returning false")
            return False

        except Exception as e:
            logger.error('Class RDSBackupCleanup. Method get_rds_instance_snapshot failed with error: ' + str(e))

    
    def restore_rds_snapshot(self, rds_instance, rds_instance_type, rds_subnet_group, multi_az, rds_public):  
        try:
            for instance in rds_instance:
                
                date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
                source_snapshot_name = 'lambda-dr-snapshot'
                source_snapshot_id = '%s-%s-%s' % (source_snapshot_name, instance, date)
        
                logger.info('Will restore %s to %s' % (source_snapshot_id, instance))
            
                response = self.my_rds.restore_db_instance_from_db_snapshot(
                    DBInstanceIdentifier=instance,
                    DBSnapshotIdentifier=source_snapshot_id,
                    DBInstanceClass=rds_instance_type,
                    DBSubnetGroupName=rds_subnet_group,
                    MultiAZ=multi_az,
                    PubliclyAccessible=rds_public
                )
            
            return response

        except Exception as e:
            logger.error('Class RDSRestore. Method restore_rds_snapshot failed with error: ' + str(e))
    