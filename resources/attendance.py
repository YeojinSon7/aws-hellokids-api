from flask_restful import Resource
from flask import request
import mysql.connector
from mysql.connector import Error
from mysql_connection import get_connection
from utils import check_password, hash_password
from email_validator import validate_email,EmailNotValidError 
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from datetime import datetime
import boto3
from config import Config
import json

class AttendanceChildrenListResource(Resource) :

    @jwt_required()
    def get(self):

        teacherId = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''select c.classId,className,c.id,childName from children c
                    join teacher t
                    on t.classId = c.classId
                    left join class cl
                    on c.classId = cl.id
                    where t.id = %s;'''
            record = (teacherId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return{'result':'fail', 'error':str(e)}, 400
        
        print(result_list)
        

        return {'result':'success', 'count':len(result_list), 'items':result_list}
    
class AttendanceAddResource(Resource):
    @jwt_required()
    def post(self,childId):

        data = request.get_json()
    
        print(data)

        try:
            connection = get_connection()

            query = '''insert into attendanceCheck (childId,classId,date,status,memo) values (%s,%s,%s,%s,%s);'''
            record = (childId,data["classId"],data["date"], data["status"], data["memo"])
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fail','error': str(e)}, 500

        return {'result' :'success'}
    
class AttendanceClassListResource(Resource):

    @jwt_required()
    def get(self):

        teacherId = get_jwt_identity()
        try:
            connection = get_connection()
            query = '''select a.id,childName,date,status,memo from attendanceCheck a
                    join children c
                    on c.id = a.childId
                    join teacher t
                    on c.classId = t.classId
                    where t.id = %s;'''
            record = (teacherId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return{'result':'fail', 'error':str(e)}, 400
        

        i = 0
        for row in result_list :
            result_list[i]['date']= row['date'].isoformat()
            i = i + 1
        

        return {'items':result_list}

class AttendanceEditResource(Resource):
    @jwt_required()
    def put(self,id):

        data = request.get_json()
        try :
            connection = get_connection()
            query = '''update attendanceCheck
                    set status = %s, memo = %s
                    where id = %s;''' 
            record = (data['status'],data['memo'],id) 
            cursor= connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result': 'fail','error': str(e)},500
        
        return {'result': 'success'} 
    
class AttendanceChildListResource(Resource):
    @jwt_required()
    def get(self):

        parentsId = get_jwt_identity()
        try:
            connection = get_connection()
            query = '''select a.id,childName,date,status,memo from attendanceCheck a
                    join children c
                    on c.id = a.childId
                    join parents p
                    on p.childId = c.id
                    where p.id = %s;'''
            record = (parentsId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return{'result':'fail', 'error':str(e)}, 400
        

        i = 0
        for row in result_list :
            result_list[i]['date']= row['date'].isoformat()
            i = i + 1
        

        return {'items':result_list}

