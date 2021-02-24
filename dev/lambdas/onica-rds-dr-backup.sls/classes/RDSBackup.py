import botocore  
import datetime  
import re  
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class RDSBackup:

    def __init__(self):
            self.my_rds = boto3.client('rds')
            
    def get_rds_instance(self,instances):   
        try:
            result = False
            for instance in instances:
                logger.info("Checking if RDS instance: " + instance + " exists")
                response = self.my_rds.describe_db_instances(
                    DBInstanceIdentifier=instance
                )

            if 'DBInstances' in response:
                logger.info("RDS Instance exists")
                result = True
            else:
                logger.info("RDS Instance does not exist")
            return result
        
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFound':
                logger.info("RDS instance does not exist. Returning false")
            return False

        except Exception as e:
            logger.error('Class RDSBackup. Method get_rds_instance failed with error: ' + str(e))
    
    def create_rds_snapshot(self, instances):          
        try:
            for instance in instances:
                logger.info("Creating RDS instance snapshot for instance " + instance)
                date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
                snapshot = "{0}-{1}-{2}".format("lambda-dr-snapshot", instance, date)
                response = self.my_rds.create_db_snapshot(DBSnapshotIdentifier=snapshot, DBInstanceIdentifier=instance,)
                logger.info(response)
            return response
        
        except Exception as e:
            logger.error('Class RDSBackup Method create_rds_snapshot failed with error: ' + str(e))